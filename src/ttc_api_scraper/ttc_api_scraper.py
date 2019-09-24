import asyncio
import configparser
import logging.config
import re
import os
import subprocess
import sys
from datetime import datetime
from time import sleep
from concurrent.futures._base import TimeoutError

import aiohttp  # this lib replaces requests for asynchronous i/o
import click
from psycopg2 import OperationalError, connect, sql  # Connect to local PostgreSQL db
import pytz
import requests  # to handle http requests to the API

from ttc_api_scraper.writers import WriteS3, WriteSQL


handlers=[logging.StreamHandler()]
if os.environ.get('LOG_FILENAME'):
    handlers.append(logging.FileHandler(os.environ.get('LOG_FILENAME')))

logging.basicConfig(format="%(asctime)-15s %(message)s",
                    handlers=handlers)

LOGGER = logging.getLogger(__name__)

if os.environ.get('LOG_LEVEL'):
    LOGGER.setLevel(getattr(logging, os.environ.get('LOG_LEVEL')))
else:
    LOGGER.setLevel(getattr(logging, 'INFO'))


class DBArchiver (object):
    
    SQLS = {'requests' : sql.SQL('''COPY (SELECT r.* FROM public.requests r
                                          WHERE request_date >= {0}::DATE AND request_date < {1}::DATE + INTERVAL '1 month')
                                     TO STDOUT WITH CSV HEADER'''),
            'ntas_data' : sql.SQL('''COPY (SELECT n.* FROM public.ntas_data n
                                        NATURAL JOIN public.requests 
                                        WHERE request_date >= {}::DATE AND request_date < {}::DATE + INTERVAL '1 month')
                                     TO STDOUT WITH CSV HEADER''')
    }
    
    def __init__(self, con, logger=None):
        self.logger = logger
        self.con = con
    
    def compress(self, filename):
        """Compress the given filename"""
        subprocess.run(['gzip', filename])
    
    def pull_data_to_csv(self, table, month):
        """Download data for the specified month and table to a csv"""
        query = self.SQLS[table].format(sql.Literal(month), sql.Literal(month))
        filename = table+'_'+month+'.csv'
        with self.con:
            with self.con.cursor() as cur:
                with open(filename, 'w') as f:
                    cur.copy_expert(query, f)

    def archive_month(self, month):
        """Pull and comrpess the given month of data for all tables"""
        for table in self.SQLS.keys():
            LOGGER.info('Pulling data for table: %s', table)
            self.pull_data_to_csv(table, month)
            LOGGER.info('Compressing')
            self.compress(table+'_'+month+'.csv')

    @staticmethod
    def format_month(yyyy, mm):
        dd = '01'
        if mm < 10:
            return str(yyyy)+'-0'+str(mm)+'-'+dd
        return str(yyyy)+'-'+str(mm)+'-'+dd

    @staticmethod
    def validate_yyyymm_range(yyyymmrange):
        """Validate the two yyyymm command line arguments provided
        Args:
            yyyymmrange: List containing a start and end year-month in yyyymm format
        
        Returns:
            A dictionary with the processed range like {'yyyy':range(mm1,mm2+1)}
        
        Raises:
            ValueError: If the values entered are incorrect
        """

        step = 1
        
        if len(yyyymmrange) != 2:
            raise ValueError('{yyyymmrange} should contain two YYYYMM arguments'
                            .format(yyyymmrange=yyyymmrange))
        
        regex_yyyymm = re.compile(r'20\d\d(0[1-9]|1[0-2])')
        yyyy, mm = [], []
        years = {}
        
        for yyyymm in yyyymmrange:
            if re.fullmatch(regex_yyyymm.pattern, yyyymm):
                yyyy.append(int(yyyymm[:4]))
                mm.append(int(yyyymm[-2:]))
            else:
                raise ValueError('{yyyymm} is not a valid year-month value of format YYYYMM'
                                .format(yyyymm=yyyymm))
        
        if yyyy[0] > yyyy[1] or (yyyy[0] == yyyy[1] and mm[0] > mm[1]):
            raise ValueError('Start date {yyyymm1} after end date {yyyymm2}'
                            .format(yyyymm1=yyyymmrange[0], yyyymm2=yyyymmrange[1]))
        
        # Iterate over years and months
        if yyyy[0] == yyyy[1]:
            years[yyyy[0]] = range(mm[0], mm[1]+1, step)
        else:
            for year in range(yyyy[0], yyyy[1]+1):
                if year == yyyy[0]:
                    years[year] = range(mm[0], 13, step)
                elif year == yyyy[1]:
                    years[year] = range(1, mm[1]+1, step)
                else:
                    years[year] = range(1, 13, step)
        return years
                    

class TTCSubwayScraper( object ):
    LINES = {1: list(range(1, 33)) + list(range(75, 81)), # max value must be 1 greater
                                                          # Line 1 extension is 75-80
             2: range(33, 64),
             4: range(64, 69)}

    BASE_URL = "http://api.ttc.ca/Subway/loadNtas.action"
    INTERCHANGES = (9,10,22,30,47,48,50,64) 

    def __init__(self, logger, writer, filter_flag):
        self.logger = logger
        self.filter_flag = filter_flag
        self.writer = writer

    def get_API_response(self, line_id, station_id):
        payload = {"subwayLine":line_id,
                   "stationId":station_id,
                   "searchCriteria":''}
        
        # with timeout set to 10, need to use a try block here to catch timeout errors
        try:
            r = requests.get(self.BASE_URL, params = payload, timeout = 10)
        except requests.exceptions.RequestException as err:
            self.logger.critical(err)
            return None
        
        # another try block will check for http error codes
        try:
            r.raise_for_status()
        except requests.exceptions.RequestException as err:
            self.logger.critical(err)
            return None

        return r.json()

    def insert_request_info(self, poll_id, data, line_id, station_id, request_date):
        request_row = {
            'pollid': poll_id,
            'request_date': str(request_date),
            'data_': data['data'],
            'stationid': station_id,
            'lineid': line_id,
            'all_stations': data['allStations'],
            'create_date': data['ntasData'][0]['createDate'].replace('T', ' ')
        }

        request_id = self.writer.add_request_info(request_row)
        self.logger.debug("Request " + str(request_id) + ": " + str(request_row))

        return request_id

    def insert_ntas_data(self, ntas_data, request_id):

        for record in ntas_data:
            if self.filter_flag and record['trainMessage'] == "Arriving":
                continue # skip any records that are Arriving or not final
            record_row ={
                'requestid': request_id,
                'id': str(record['id']),
                'station_char': record['stationId'],
                'subwayline': record['subwayLine'],
                'system_message_type': record['systemMessageType'],
                'timint': str(record['timeInt']),
                'traindirection': record['trainDirection'],
                'trainid': str(record['trainId']),
                'train_message': record['trainMessage'],
                'train_dest': record['stationDirectionText']
            }

            self.writer.add_ntas_record(record_row)

    def insert_poll_start(self, time):

        poll_id = self.writer.add_poll_start(time)
        self.logger.debug("Poll " + str(poll_id) + " started at " + str(time))
        return poll_id

    def update_poll_end(self, poll_id, time):
        self.writer.add_poll_end(poll_id, time)
        self.logger.debug("Poll " + str(poll_id) + " ended at " + str(time))

    def check_for_missing_data( self, stationid, lineid, data):
        if data is None:
            return True
        ntasData = data.get('ntasData')
        if ntasData is None or ntasData == []:
            return True

        # there is data, so do more careful checks

        # at interchange stations, the API returns trains on both lines, despite the fact that each line has a unique stationid
        # So for interchange stations, make sure we have at least one observation on the right line!
        # if we're not in an interchange station, we're done
        if stationid not in self.INTERCHANGES:
            return False 
        # most general way to detect the problem is to check subwayLine field
        linecodes = ("YUS", "BD", "", "SHEP")
        # look for one train observed in the right direction
        for record in ntasData:
            if record['subwayLine'] == linecodes[lineid-1]:
                return False

        # none match
        return True
    
    async def query_station_async(self, session, line_id, station_id ):
        retries = 4
        payload = {"subwayLine":line_id,
                       "stationId":station_id,
                       "searchCriteria":'',
                       "_": '1548199023829'}

        for attempt in range(retries):
            try:
                rtime = datetime.now(pytz.timezone("America/Toronto"))
                async with session.get(self.BASE_URL, params=payload, timeout=5,
                                       headers={'User-Agent': 'Mozilla/5.0',
                                                'Accept-Encoding': 'gzip, deflate, br',
                                                'Referer': 'https://www.ttc.ca/Subway/next_train_arrivals.jsp'},
                                       raise_for_status=True) as resp:
                    try:
                        data = await resp.json()
                    except ValueError as err:
                        self.logger.error('Malformed JSON for station {} on line {}'.format(station_id, line_id))
                        self.logger.error(err)
                        if attempt < retries-1:
                            self.logger.debug("Sleeping 2s  ...")
                            await asyncio.sleep(2)
                        continue

                    if self.check_for_missing_data(station_id, line_id, data):
                        self.logger.error("Missing data!")
                        self.logger.error("Try " + str(attempt+1) + " for station " + str(station_id) + " failed.")
                        if attempt < retries-1:
                            self.logger.debug("Sleeping 2s  ...")
                            await asyncio.sleep(2)
                        continue

                    return (data, rtime)
            except aiohttp.client_exceptions.ClientConnectorError:
                if attempt < retries - 1:
                    self.logger.error("Sleeping 2s  ...")
                    await asyncio.sleep(2)
                # continue

            except aiohttp.client_exceptions.ClientResponseError as err:
                self.logger.error('Client response error')
                self.logger.error(err)

                if attempt < retries - 1:
                    self.logger.error("Sleeping 2s  ...")
                    await asyncio.sleep(2)
                # continue
            except TimeoutError as err:
                self.logger.error('Timout Error')
                self.logger.error(err)

                if attempt < retries - 1:
                    self.logger.error("Sleeping 2s  ...")
                    await asyncio.sleep(2)
                # continue

        self.logger.error('Out of retries, could not fetch '
                          '{line_id}, {station_id}'.format(line_id=line_id, station_id=station_id))

        return (None, None)

    # async def qtest( self, session, line_id, station_id):
    #     payload = {"subwayLine":line_id,
    #                    "stationId":station_id,
    #                    "searchCriteria":''}
    #     async with session.get(self.BASE_URL, params=payload, timeout=10) as resp:
    #         ret = await resp.json()
    #         print(ret)
    #         return ret

    # async def qstest( self, loop):
    #       async with aiohttp.ClientSession() as session:
    #             tasks = []
    #             task = asyncio.ensure_future(self.query_station_async(session, 1, 1))
    #             tasks.append(task)
    #             responses = await asyncio.gather(*tasks)
    #             if self.check_for_missing_data( 1, 1, responses[0]) :
    #                 errmsg = 'No data for line {line}, station {station}'
    #                 self.logger.error(errmsg.format(line=1, station=1))
    #                 self.logger.debug( errmsg.format(line=1, station=1) )
    #             print( responses[0])

    async def query_all_stations_async(self, loop):

        poll_id = self.insert_poll_start(datetime.now(pytz.timezone("America/Toronto")))

        # run requests simultaneously using asyncio
        async with aiohttp.ClientSession() as session:
            tasks = []
            for line_id, stations in self.LINES.items():
                for station_id in stations:

                    task = asyncio.ensure_future(self.query_station_async(session, line_id, station_id))
                    tasks.append(task)
            responses = await asyncio.gather(*tasks)

        for data, rtime in responses:
            if data is not None:
                line_id = data['subwayLine']
                station_id = data['stationId']

                request_id = self.insert_request_info(poll_id, data, line_id, station_id, rtime)

                self.insert_ntas_data(data['ntasData'], request_id)

        self.update_poll_end( poll_id, datetime.now(pytz.timezone("America/Toronto")) )
        self.writer.commit()

    def query_all_stations(self):

        poll_id = self.insert_poll_start( datetime.now(pytz.timezone("America/Toronto")) )
        retries = 3

        for line_id, stations in self.LINES.items():
            for station_id in stations:
                for attempt in range(retries):
                    data = self.get_API_response(line_id, station_id)
                    if not self.check_for_missing_data( station_id, line_id, data) :
                        break
                    else:
                        self.logger.debug("Try " + str(attempt+1) + " for station " + str(station_id) + " failed.")
                        #if data is None:
                        # for http and timeout errors, sleep 2s before retrying
                        self.logger.debug("Sleeping 2s  ...")
                        sleep(2)
       

                if self.check_for_missing_data( station_id, line_id, data) :
                    errmsg = 'No data for line {line}, station {station}'
                    self.logger.error(errmsg.format(line=line_id, station=station_id))
                    continue    
                request_id = self.insert_request_info(poll_id, data, line_id, station_id,
                                                      datetime.now(pytz.timezone("America/Toronto")
                                                                   )
                                                      )
                self.insert_ntas_data(data['ntasData'], request_id)

        self.update_poll_end( poll_id, datetime.now(pytz.timezone("America/Toronto")) )
        self.writer.commit()


def _connection(ctx, retries=3, delay=3):
    for idx in range(retries):
        attempt = idx + 1
        try:
            return connect(**ctx.obj['dbset'])
        except OperationalError as e:
            if 'could not connect to server' not in str(e):
                raise
            if attempt == retries:
                raise
            LOGGER.debug("Cannot connect to db. Attempt {} of {}. Trying again in {}s".format(attempt, retries, delay))
            sleep(delay)

@click.group()
@click.option('-d', '--settings', type=click.Path(exists=True), default='db.cfg')
@click.pass_context
def cli(ctx, settings='db.cfg'):
    CONFIG = configparser.ConfigParser(interpolation=None)
    CONFIG.read(settings)
    dbset = CONFIG['DBSETTINGS']

    ctx.obj['dbset'] = dbset

@cli.command()
@click.pass_context
@click.option('--s3/--no-s3', default=False)
@click.option('--postgres/--no-postgres', default=False)
@click.option('--filtering/--no-filtering', default=False)
@click.option('-s','--schemaname', default='public')
@click.option('--bucketname')
def scrape(ctx, s3, postgres, filtering, schemaname, bucketname):
    """Run the scraper"""

    if s3 == postgres:
        LOGGER.critical("Must specify s3 or Postgres writers (not both, or neither).")
        sys.exit(1)

    if postgres:
        con = _connection(ctx)
        writer = WriteSQL(schemaname, con)

    if s3:
        if bucketname is None:
            LOGGER.critical("Bucket name not set.")
            sys.exit(1)

        writer = WriteS3(bucketname)

    try:
        scraper = TTCSubwayScraper(LOGGER, writer, filtering)

        scraper.query_all_stations()

        # loop = asyncio.get_event_loop()
        # future = asyncio.ensure_future( scraper.query_all_stations_async(loop))
        # loop.run_until_complete( future )
    finally:
        if postgres:
            con.close()

@cli.command()
@click.pass_context
@click.argument('month')
@click.argument('end_month', required=False)
def archive(ctx, month, end_month):
    """Download month (YYYYMM) of data from database and compress it"""
    con = connect(**ctx.obj['dbset']) 
    archive = DBArchiver(con)

    if end_month is None: end_month = month

    months_to_iterate = DBArchiver.validate_yyyymm_range([month, end_month])
    for year in months_to_iterate:
        for mm in months_to_iterate[year]:
            LOGGER.info('Archiving month: %s-%s', year, mm)
            archive.archive_month(DBArchiver.format_month(year, mm))
    LOGGER.info('Archiving complete.')


def handler(event, context):
    """Entry point for the AWS Lambda way of launching this script"""

    if os.environ.get('S3_BUCKET') is None:
        LOGGER.critical("S3_BUCKET environmental variable is not set")
        sys.exit(1)

    bucket_name = os.environ.get('S3_BUCKET')

    writer = WriteS3(bucket_name)

    scraper = TTCSubwayScraper(LOGGER, writer, False)
    scraper.query_all_stations()

    # loop = asyncio.get_event_loop()
    # future = asyncio.ensure_future(scraper.query_all_stations_async(loop))
    # loop.run_until_complete(future)


def main():
    # https://github.com/pallets/click/issues/456#issuecomment-159543498
    cli(obj={})


if __name__ == '__main__':

    try:
        main()
    except Exception as err:
        LOGGER.critical("Unhandled exception - quitting.")
        LOGGER.critical(err, exc_info=True)
