import asyncio
import logging
import logging.config
import re
import subprocess
import sys
from datetime import datetime
from time import sleep

import click
from psycopg2 import connect, sql  # Connect to local PostgreSQL db

import aiohttp  # this lib replaces requests for asynchronous i/o
import async_timeout
import requests  # to handle http requests to the API

#import socket

# Note - the package yarl, a dependency of aiohttp, breaks the library on version 0.9.4 and 0.9.5
# So need to manually install 0.9.3 or try 0.9.6, which should fix the bug.
# e.g. pip uninstall yarl; pip install yarl==0.9.3
# see https://github.com/KeepSafe/aiohttp/issues/1635
# Use virtualenv to avoid borking your system install of python

# optimal performance may require installation of cchardet and aiodns packages
# see  http://aiohttp.readthedocs.io/en/stable/index.html

#Not used anymore
class MissingDataException( TypeError):
    pass

LOGGER = logging.getLogger(__name__)

class DBArchiver (object):

    SQLS = {'polls': sql.SQL('''COPY(SELECT * FROM public.polls
                                    WHERE poll_start >= {0}::DATE AND poll_start < {1}::DATE + INTERVAL '1 month')
                                TO STDOUT WITH CSV HEADER'''),
            'requests' : sql.SQL('''COPY (SELECT r.* FROM public.requests r
                                          NATURAL JOIN public.polls
                                          WHERE poll_start >= {0}::DATE AND poll_start < {1}::DATE + INTERVAL '1 month')
                                     TO STDOUT WITH CSV HEADER'''),
            'ntas_data' : sql.SQL('''COPY (SELECT n.* FROM public.ntas_data n
                                        NATURAL JOIN public.requests
                                        NATURAL JOIN public.polls
                                        WHERE poll_start >= {}::DATE AND poll_start < {}::DATE + INTERVAL '1 month')
                                     TO STDOUT WITH CSV HEADER''')
    }

    def __init__(self, con, logger=None):
        self.logger = logger
        self.con = con

    def compress(self, filename):
        '''Compress the given filename'''
        subprocess.run(['gzip', filename])

    def pull_data_to_csv(self, table, month):
        '''Download data for the specified month and table to a csv'''
        query = self.SQLS[table].format(sql.Literal(month), sql.Literal(month))
        filename = table+'_'+month+'.csv'
        with self.con:
            with self.con.cursor() as cur:
                with open(filename, 'w') as f:
                    cur.copy_expert(query, f)

    def archive_month(self, month):
        '''Pull and comrpess the given month of data for all tables'''
        for table in self.SQLS.keys():
            LOGGER.info('Pulling data for table: %s', table)
            self.pull_data_to_csv(table, month)
            LOGGER.info('Compressing')
            self.compress(table+'_'+month+'.csv')

    @staticmethod
    def format_month(yyyy, mm):
        dd='01'
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

        #Iterate over years and months
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
    LINES = {1: list(range(1, 33)) + list(range(75, 81)), #max value must be 1 greater
                                                          #Line 1 extension is 75-80
             2: range(33, 64),
             4: range(64, 69)}
    BASE_URL = "http://www.ttc.ca/Subway/loadNtas.action"
    INTERCHANGES = (9,10,22,30,47,48,50,64)
    #BASE_URL = 'http://www.ttc.ca/Subway/'

    def __init__(self, logger, con, filter_flag, schema):
        self.logger = logger
        self.con = con
        self.filter_flag = filter_flag
        self.NTAS_SQL = """INSERT INTO {schema}.ntas_data(\
            requestid, id, station_char, subwayline, system_message_type, \
            timint, traindirection, trainid, train_message, train_dest) \
            VALUES (%(requestid)s, %(id)s, %(station_char)s, %(subwayline)s, %(system_message_type)s, \
            %(timint)s, %(traindirection)s, %(trainid)s, %(train_message)s, %(train_dest)s);
          """.format(schema=schema)
        self.requests_sql = """INSERT INTO {schema}.requests(data_,
                        stationid, lineid, all_stations, create_date, pollid, request_date)
                       VALUES(%(data_)s, %(stationid)s, %(lineid)s, %(all_stations)s, %(create_date)s, %(pollid)s, %(request_date)s)
                       RETURNING requestid""".format(schema=schema)
        self.poll_update_sql = """UPDATE {schema}.polls set poll_end = %s
                        WHERE pollid = %s""".format(schema=schema)
        self.poll_insert_sql =  """INSERT INTO {schema}.polls(poll_start)
                        VALUES(%s)
                        RETURNING pollid""".format(schema=schema)

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
        request_row = {}
        request_row['pollid'] = poll_id
        request_row['request_date'] = str(request_date)
        request_row['data_'] = data['data']
        request_row['stationid'] = station_id
        request_row['lineid'] = line_id
        request_row['all_stations'] = data['allStations']
        request_row['create_date'] = data['ntasData'][0]['createDate'].replace('T', ' ')
        cursor = self.con.cursor()
        cursor.execute(self.requests_sql, request_row)
        request_id = cursor.fetchone()[0]
        self.con.commit()
        cursor.close()
        self.logger.debug("Request " + str(request_id) + ": " + str(request_row) )

        return request_id

    def insert_ntas_data(self, ntas_data, request_id):
        cursor = self.con.cursor()

        for record in ntas_data:
            if self.filter_flag and record['trainMessage'] == "Arriving":
                continue # skip any records that are Arriving or not final
            record_row ={}
            record_row['requestid'] = request_id
            record_row['id'] = record['id']
            record_row['station_char'] = record['stationId']
            record_row['subwayline'] = record['subwayLine']
            record_row['system_message_type'] = record['systemMessageType']
            record_row['timint'] = record['timeInt']
            record_row['traindirection'] = record['trainDirection']
            record_row['trainid'] = record['trainId']
            record_row['train_message'] = record['trainMessage']
            record_row['train_dest'] = record['stationDirectionText']

            cursor.execute(self.NTAS_SQL, record_row)
        self.con.commit()
        cursor.close()

    def insert_poll_start(self, time):
        cursor = self.con.cursor()
        cursor.execute(self.poll_insert_sql, (str(time),))
        poll_id = cursor.fetchone()[0]
        self.con.commit()
        cursor.close()
        self.logger.debug("Poll " + str(poll_id) + " started at " + str(time) )
        return poll_id

    def update_poll_end(self, poll_id, time):
        cursor = self.con.cursor()
        cursor.execute(self.poll_update_sql, (str(time), str(poll_id)) )
        self.con.commit()
        cursor.close()
        self.logger.debug("Poll " + str(poll_id) + " ended at " + str(time) )


    def check_for_missing_data( self, stationid, lineid, data):
        if data is None:
            return True
        ntasData = data.get('ntasData')
        if ntasData is None or ntasData ==[] :
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
                       "searchCriteria":''}
        for attempt in range(retries):
            #with async_timeout.timeout(10):
            try:
                rtime = datetime.now()
                async with session.get(self.BASE_URL, params=payload, timeout=5) as resp:
                    #data = None
                    try:
                        data = await resp.json()
                    except ValueError as err:
                        self.logger.error('Malformed JSON for station {} on line {}'.format(station_id, line_id))
                        self.logger.error(err)
                        self.logger.error(resp.text())
                        if attempt < retries-1:
                            self.logger.debug("Sleeping 2s  ...")
                            await asyncio.sleep(2)
                        continue


                    if self.check_for_missing_data(station_id, line_id, data):
                        self.logger.debug("Missing data!")
                        self.logger.debug("Try " + str(attempt+1) + " for station " + str(station_id) + " failed.")
                        if attempt < retries-1:
                            self.logger.debug("Sleeping 2s  ...")
                            await asyncio.sleep(2)
                        continue
                    return (data, rtime)
            except Exception as err:
                self.logger.critical(err)
                self.logger.debug("request error!")
                self.logger.debug("Try " + str(attempt+1) + " for station " + str(station_id) + " failed.")
                if attempt < retries-1:
                    self.logger.debug("Sleeping 2s  ...")
                    await asyncio.sleep(2)
                continue
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

    async def query_all_stations_async(self,loop):
            poll_id = self.insert_poll_start(datetime.now())

            # run requests simultaneously using asyncio
            async with aiohttp.ClientSession() as session:
                tasks = []
                for line_id, stations in self.LINES.items():
                    for station_id in stations:
                        task = asyncio.ensure_future(self.query_station_async(session, line_id, station_id))
                        tasks.append(task)
                responses = await asyncio.gather(*tasks)

            # check results and insert into db
            for line_id, stations in self.LINES.items():
                for station_id in stations:
                    (data, rtime) = responses[station_id-1]  # may want to tweak this to check error codes etc
                    if self.check_for_missing_data( station_id, line_id, data) :
                        errmsg = 'No data for line {line}, station {station}'
                        self.logger.error(errmsg.format(line=line_id, station=station_id))
                        continue
                    request_id = self.insert_request_info(poll_id, data, line_id, station_id, rtime )
                    self.insert_ntas_data(data['ntasData'], request_id)

            self.update_poll_end( poll_id, datetime.now() )




    def query_all_stations(self):
        poll_id = self.insert_poll_start( datetime.now() )
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
                request_id = self.insert_request_info(poll_id, data, line_id, station_id, datetime.now() )
                self.insert_ntas_data(data['ntasData'], request_id)

        self.update_poll_end( poll_id, datetime.now() )

@click.group()
@click.option('-d', '--settings', type=click.Path(exists=True), default='db.cfg')
@click.pass_context
def cli(ctx, settings='db.cfg'):
    import configparser
    CONFIG = configparser.ConfigParser(interpolation=None)
    CONFIG.read(settings)
    dbset = CONFIG['DBSETTINGS']
    log_settings = CONFIG['LOGGING']
    ctx.obj['dbset'] = dbset
    logging.basicConfig(level=logging.getLevelName(log_settings['level']), format=log_settings['format'], filename=log_settings['filename'])

    # add console output for debugging
    if log_settings['level'] == 'DEBUG':
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        LOGGER.addHandler(ch)

@cli.command()
@click.pass_context
@click.option('--filtering/--no-filtering', default=False)
@click.option('-s','--schemaname', default='public')
def scrape(ctx, filtering, schemaname):
    '''Run the scraper'''
    con = connect(**ctx.obj['dbset'])
    scraper = TTCSubwayScraper(LOGGER, con, filtering, schemaname)

    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(scraper.query_all_stations_async(loop))
    loop.run_until_complete(future)

    con.close()

@cli.command()
@click.pass_context
@click.argument('month')
@click.argument('end_month', required=False)
def archive(ctx, month, end_month):
    '''Download month (YYYYMM) of data from database and compress it'''
    con = connect(**ctx.obj['dbset'])
    archive = DBArchiver(con)

    if end_month is None: end_month = month

    months_to_iterate = DBArchiver.validate_yyyymm_range([month, end_month])
    for year in months_to_iterate:
        for mm in months_to_iterate[year]:
            LOGGER.info('Archiving month: %s-%s', year, mm)
            archive.archive_month(DBArchiver.format_month(year, mm))
    LOGGER.info('Archiving complete.')

def main():
    #https://github.com/pallets/click/issues/456#issuecomment-159543498
    cli(obj={})

if __name__ == '__main__':

    try:
        main()
    except Exception as err:
        LOGGER.critical("Unhandled exception - quitting.")
        LOGGER.critical(err, exc_info=True)
