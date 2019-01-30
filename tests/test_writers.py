from ttc_api_scraper.writers import WriteS3

from moto import mock_s3
import pytz

import datetime
import json

@mock_s3
def test_service_day():
    x=WriteS3('testbucket')

    tz = pytz.timezone("America/Toronto")
    assert x._service_day(datetime.datetime(2018,10,1,12,0, tzinfo=tz), servicedayhour=4) == datetime.date(2018,10,1)

    assert x._service_day(datetime.datetime(2018, 10, 1, 3, 55, tzinfo=tz),servicedayhour=4) == datetime.date(2018, 9, 30)
    assert x._service_day(datetime.datetime(2018, 10, 1, 4, 5, tzinfo=tz), servicedayhour=4) == datetime.date(2018, 10, 1)

    assert x._service_day(datetime.datetime(2018, 10, 1, 4, 55, tzinfo=tz),servicedayhour=5) == datetime.date(2018, 9, 30)
    assert x._service_day(datetime.datetime(2018, 10, 1, 5, 5, tzinfo=tz), servicedayhour=5) == datetime.date(2018, 10, 1)

@mock_s3
def test_writer():

    bucketname = 'testbucket'
    x=WriteS3(bucketname, aws_access_key='mymockaccesskey', aws_secret_access_key='mymocksecretkey')

    x.s3.create_bucket(Bucket=bucketname)

    tz = pytz.timezone("America/Toronto")

    start = datetime.datetime(2018, 10, 1, 12, 0, tzinfo=tz)
    end = datetime.datetime(2018, 10, 1, 12, 2, tzinfo=tz)

    pollid = x.add_poll_start(start)
    request_row={'pollid': pollid, 'content': 'resquestcontent'}
    requestid = x.add_request_info(request_row)
    record_row = {'requestid':requestid, 'content': 'ntascontent'}
    x.add_ntas_record(record_row)
    x.add_poll_end(pollid, end)

    x.commit(start)

    toronto_now_str = str(start).replace(':', '_').replace(' ', '.')
    s3_path = '{service_date}/{toronto_now_str}.json'.format(service_date=x._service_day(start),
                                                             toronto_now_str=toronto_now_str)

    written_data=json.loads(x.s3.get_object(
        Bucket=bucketname,
        Key=s3_path
    )['Body'].read().decode("utf-8"))

    expected=[
        {
            "start": "2018-10-01 12:00:00-05:18",
            "end": "2018-10-01 12:02:00-05:18",
            "requests": [{
                "content": "resquestcontent",
                "responses": [
                    {
                        "content": "ntascontent"
                    }
                ]
            }]
        }
    ]

    assert written_data==expected, 'Problem with the data written to S3'
