import logging
import sys
import requests #to handle http requests to the API 
from psycopg2 import connect #Connect to local PostgreSQL db
from datetime import datetime
from time import sleep
#import socket

#Not used anymore
class MissingDataException( TypeError):
    pass

class TTCSubwayScraper( object ):
    LINES = {1: range(1, 33), #max value must be 1 greater
             2: range(33, 64),
             4: range(64, 69)}
    BASE_URL = "http://www.ttc.ca/Subway/loadNtas.action"
    NTAS_SQL = """INSERT INTO public.ntas_data(\
            requestid, id, station_char, subwayline, system_message_type, \
            timint, traindirection, trainid, train_message) \
            VALUES (%(requestid)s, %(id)s, %(station_char)s, %(subwayline)s, %(system_message_type)s, \
            %(timint)s, %(traindirection)s, %(trainid)s, %(train_message)s);
          """
    def __init__(self, logger, con):
        self.logger = logger
        self.con = con
        
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
        request_row['request_date'] = request_date
        request_row['data_'] = data['data']
        request_row['stationid'] = station_id
        request_row['lineid'] = line_id
        request_row['all_stations'] = data['allStations']
        request_row['create_date'] = data['ntasData'][0]['createDate'].replace('T', ' ')
        cursor = self.con.cursor()
        cursor.execute("INSERT INTO public.requests(data_, stationid, lineid, all_stations, create_date, pollid, request_date)"
                       "VALUES(%(data_)s, %(stationid)s, %(lineid)s, %(all_stations)s, %(create_date)s, %(pollid)s, %(request_date)s)"
                       "RETURNING requestid", request_row)
        request_id = cursor.fetchone()[0] 
        self.con.commit()
        cursor.close()
        self.logger.debug("Request " + str(request_id) + ": " + str(request_row) )

        return request_id

    def insert_ntas_data(self, ntas_data, request_id):
        cursor = self.con.cursor()

        for record in ntas_data:
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
            cursor.execute(self.NTAS_SQL, record_row)
        self.con.commit()
        cursor.close()

    def insert_poll_start(self, time):
        cursor = self.con.cursor()
        cursor.execute("INSERT INTO public.polls(poll_start)"
                        "VALUES(%s)"
                        "RETURNING pollid", (str(time),))
        poll_id = cursor.fetchone()[0]
        self.con.commit()
        cursor.close()
        self.logger.debug("Poll " + str(poll_id) + " started at " + str(time) )
        return poll_id

    def update_poll_end(self, poll_id, time):
        cursor = self.con.cursor()
        cursor.execute("UPDATE public.polls set poll_end = %s"
                        "WHERE pollid = %s", (str(time), str(poll_id)) )
        self.con.commit()
        cursor.close()
        self.logger.debug("Poll " + str(poll_id) + " ended at " + str(time) )


    def query_all_stations(self):
        poll_id = self.insert_poll_start( datetime.now() )
        retries = 3
        for line_id, stations in self.LINES.items():
            for station_id in stations:
                for attempt in range(retries):
                    data = self.get_API_response(line_id, station_id)
                    if not ( data is None or data.get('ntasData', None) is None or data.get('ntasData', None) == []):
                        break
                    else:
                        if data is None:
                            # for http and timeout errors, sleep 2s before retrying
                            self.logger.debug("Sleeping 2s for request error ...")
                            sleep(2)

                        self.logger.debug("Try " + str(attempt+1) + " for station " + str(station_id) + " failed.")
                            

                if data is None or data.get('ntasData', None) is None or data.get('ntasData', None) == []:
                    errmsg = 'No data for line {line}, station {station}'
                    self.logger.error(errmsg.format(line=line_id, station=station_id))
                    self.logger.debug( errmsg.format(line=line_id, station=station_id) )
                    continue    
                request_id = self.insert_request_info(poll_id, data, line_id, station_id, datetime.now() )
                self.insert_ntas_data(data['ntasData'], request_id)

        self.update_poll_end( poll_id, datetime.now() )

if __name__ == '__main__':
    FORMAT = '%(asctime)-15s %(message)s'
    logging.basicConfig(level=logging.DEBUG, format=FORMAT, filename='scraper.log')
    LOGGER = logging.getLogger(__name__)

    # add console output for debugging
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    LOGGER.addHandler(ch)

    try:
        con = connect(database='ttc',
                  user='postgres')  # adjust for local setup
        scraper = TTCSubwayScraper(LOGGER, con)
        scraper.query_all_stations()
        con.close()
    except Exception as err:
        LOGGER.critical("Unhandled exception - quitting.")
        LOGGER.critical(err)
