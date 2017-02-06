import logging
import sys
import requests #to handle http requests to the API
from psycopg2 import connect #Connect to local PostgreSQL db

class MissingDataException( TypeError):
    pass

class TTCSubwayScraper( object ):
    LINES = {1: range(1, 33), #max value must be 1 greater
             2: range(33, 64),
             4: range(64, 68)}
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
        r = requests.get(self.BASE_URL, params = payload)
        try:
            r.raise_for_status()
        except HTTPError as err:
            self.logger.FATAL(err)
            sys.exit(0)
        return r.json()

    def insert_request_info(self, data, line_id, station_id):
        request_row = {}
        request_row['data_'] = data['data']
        request_row['stationid'] = station_id
        request_row['lineid'] = line_id
        request_row['all_stations'] = data['allStations']
        try:
            request_row['create_date'] = data['ntasData'][0]['createDate'].replace('T', ' ')
        except TypeError as err:
            self.logger.ERROR(err)
            self.logger.ERROR(data)
            raise MissingDataException()
        cursor = self.con.cursor()
        cursor.execute("INSERT INTO public.requests(data_, stationid, lineid, all_stations, create_date)"
                       "VALUES(%(data_)s, %(stationid)s, %(lineid)s, %(all_stations)s, %(create_date)s)"
                       "RETURNING requestid", request_row)
        request_id = cursor.fetchone()[0] 
        self.con.commit()
        cursor.close()
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

    def query_all_stations(self):
        
        for line_id, stations in self.LINES.items():
            for station_id in stations:
                data = self.get_API_response(line_id, station_id)
                try:
                    request_id = self.insert_request_info(data, line_id, station_id)
                except MissingDataException:
                    continue
                self.insert_ntas_data(data['ntasData'], request_id)

if __name__ == '__main__':
    FORMAT = '%(asctime)-15s %(message)s'
    logging.basicConfig(level=logging.INFO, format=FORMAT)
    LOGGER = logging.getLogger(__name__)
    con = connect(database='ttc',
                  user='rad')
    scraper = TTCSubwayScraper(LOGGER, con)
    scraper.query_all_stations()
    con.close()