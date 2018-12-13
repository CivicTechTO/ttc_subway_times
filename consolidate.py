import os
import logging
import sys
import pytz
import subprocess

import datetime
import tempfile


handlers=[logging.StreamHandler()]
if os.environ.get('LOG_FILENAME'):
    handlers.append(logging.FileHandler(os.environ.get('LOG_FILENAME')))

logging.basicConfig(format="%(asctime)-15s %(message)s",
                    handlers=handlers)

LOGGER = logging.getLogger(__name__)


def _service_day(datetimestamp, servicedayhour=4):
    """Will round down a timestamp to the previous service day

    Times before servicedayhour will get rounded down to the previous day

    :param timestamp: A datetime to get the service day of
    :param servicedayhour: The cut time to go to the previous sercice day
    :return: A datetime.date of the service day
    """
    if datetimestamp.time() < datetime.time(servicedayhour, 0, 0):
        return datetimestamp.date() - datetime.timedelta(days=1)

    return datetimestamp.date()

def consolidate():
    if os.environ.get('S3_BUCKET') is None:
        LOGGER.critical("S3_BUCKET environmental variable is not set")
        sys.exit(1)

    s3_bucket = os.environ.get('S3_BUCKET')
    tz = pytz.timezone("America/Toronto")
    consoli_date = str(datetime.datetime.now(tz).date()-datetime.timedelta(days=1))

    with tempfile.TemporaryDirectory() as dir:

        scrape_path = os.path.join(dir, consoli_date)

        cmds=[
            ['aws', 's3', 'sync', f's3://{s3_bucket}/{consoli_date}', f'{scrape_path}'],
            ['tar', '-czf', f'{scrape_path}.tar.gz', '-C' , dir, consoli_date],
            ['aws', 's3', 'cp', f'{scrape_path}.tar.gz', f's3://{s3_bucket}'],
            # f'aws s3 rm s3://{s3_bucket}/{consoli_date} --recursive --dryrun'
        ]

        for cmd in cmds:
            print(cmd)
            try:
                logging.info(f'Running {cmd}')
                r = subprocess.call(cmd)
                if r != 0:
                    raise subprocess.CalledProcessError(r, cmd)

            except subprocess.CalledProcessError as e:
                logging.critical(e)
                return

def handler(event, context):
    """Entry point for the AWS Lambda way of launching this script"""

    consolidate()

def main():
    consolidate()

if __name__=="__main__":
    main()