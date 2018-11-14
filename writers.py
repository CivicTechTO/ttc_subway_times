from uuid import uuid4
import boto3
import tarfile
from io import BytesIO
import json
import time
import pytz, datetime
import logging
import os

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(getattr(logging, os.environ.get('LOG_LEVEL')))

class WriteSQL(object):

    def __init__(self, schema, conn):

        self.schema = schema
        self.conn = conn
        self.cursor = None

        self.requests_sql = """INSERT INTO {schema}.requests(data_,
                        stationid, lineid, all_stations, create_date, pollid, request_date)
                       VALUES(%(data_)s, %(stationid)s, %(lineid)s, %(all_stations)s, %(create_date)s, %(pollid)s, %(request_date)s)
                       RETURNING requestid""".format(schema=schema)
        self.poll_update_sql = """UPDATE {schema}.polls set poll_end = %s
                        WHERE pollid = %s""".format(schema=schema)
        self.poll_insert_sql = """INSERT INTO {schema}.polls(poll_start)
                        VALUES(%s)
                        RETURNING pollid""".format(schema=schema)

        self.ntas_sql = """INSERT INTO {schema}.ntas_data(\
            requestid, id, station_char, subwayline, system_message_type, \
            timint, traindirection, trainid, train_message, train_dest) \
            VALUES (%(requestid)s, %(id)s, %(station_char)s, %(subwayline)s, %(system_message_type)s, \
            %(timint)s, %(traindirection)s, %(trainid)s, %(train_message)s, %(train_dest)s);
          """.format(schema=self.schema)

        self.cursor = self.conn.cursor()

    def add_ntas_record(self, record_row):
        self.cursor.execute(self.ntas_sql, record_row)

    def add_request_info(self, request_row):
        self.cursor.execute(self.requests_sql, request_row)
        request_id = self.cursor.fetchone()[0]

        return request_id

    def add_poll_start(self, time):
        self.cursor.execute(self.poll_insert_sql, (str(time),))
        poll_id = self.cursor.fetchone()[0]

        return poll_id

    def add_poll_end(self, poll_id, time):
        self.cursor.execute(self.poll_update_sql, (str(time), str(poll_id)) )


    def commit(self):
        self.conn.commit()
        self.cursor.close()


class WriteS3(object):

    def __init__(self, bucket_name, access_key, secret_key):
        self.ntas_records = []
        self.requests = []
        self.polls = {}

        self.bucket_name = bucket_name

        self.s3 = boto3.resource('s3', aws_access_key_id=access_key, aws_secret_access_key=secret_key)

    def add_ntas_record(self, record_row):
        self.ntas_records.append(record_row)

    def add_poll_start(self, time):
        poll_id = str(uuid4())
        self.polls[poll_id]={'start': str(time)}

        return poll_id

    def add_poll_end(self, poll_id, time):
        self.polls[poll_id]['end']=str(time)

    def add_request_info(self, request_row):
        request_id=str(uuid4())

        self.requests.append(request_row)

        self.requests[-1]['request_id']=request_id
        return request_id

    @staticmethod
    def _service_day(datetimestamp, servicedayhour=4):
        ''' Rounds down a timestamp to the previous service day

        Times before servicedayhour will get rounded down to the previous day

        :param timestamp: A datetime to get the service day of
        :param servicedayhour: The cut time to go to the previous sercice day
        :return: A datetime.date of the service day
        '''
        if datetimestamp.time() < datetime.time(servicedayhour, 0, 0):
            return datetimestamp.date()-datetime.timedelta(days=1)

        return datetimestamp.date()

    def commit(self):
        LOGGER.info('Writing {nrecords} records to S3'.format(nrecords=len(self.ntas_records)))
        f = BytesIO()

        tar = tarfile.open(fileobj=f, mode='w')

        string, tar_info = self.string_to_tarfile("ntas", json.dumps(self.ntas_records))
        tar.addfile(tarinfo=tar_info, fileobj=string)

        string, tar_info = self.string_to_tarfile("requests", json.dumps(self.requests))
        tar.addfile(tarinfo=tar_info, fileobj=string)

        string, tar_info = self.string_to_tarfile("polls", json.dumps(self.polls))
        tar.addfile(tarinfo=tar_info, fileobj=string)

        f.seek(0)

        tz = pytz.timezone('America/Toronto')
        toronto_now = datetime.datetime.now(tz)
        service_date = self._service_day(toronto_now)

        try:
            filename = '{servicedate}/{timestamp}.tar'.format(servicedate=service_date,
                                                              timestamp=str(toronto_now))
            self.s3.Bucket(self.bucket_name).put_object(Key=filename, Body=f)
        except:
            LOGGER.critical('Error writing to S3')

        tar.close()
        self.ntas_records = []
        self.requests = []
        self.polls = {}

    def string_to_tarfile(self, name, string):
        encoded = string.encode('utf-8')
        s = BytesIO(encoded)

        tar_info = tarfile.TarInfo(name=name)
        tar_info.size=len(encoded)
        tar_info.mtime=time.time()
        tar_info.size=len(encoded)

        return s, tar_info

