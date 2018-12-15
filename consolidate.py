import errno
import os
import logging
import sys
import datetime
import tempfile
import tarfile

import boto3
import pytz

handlers = [logging.StreamHandler()]
if os.environ.get("LOG_FILENAME"):
    handlers.append(logging.FileHandler(os.environ.get("LOG_FILENAME")))

logging.basicConfig(format="%(asctime)-15s %(message)s", handlers=handlers)

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
    s3_bucket = os.environ.get("S3_BUCKET")
    tz = pytz.timezone("America/Toronto")
    consoli_date = str(datetime.datetime.now(tz).date() - datetime.timedelta(days=1))

    if os.environ.get("S3_BUCKET") is None:
        LOGGER.critical("S3_BUCKET environmental variable is not set")
        sys.exit(1)

    client = boto3.client("s3")
    with tempfile.TemporaryDirectory() as dir:
        targz_path = os.path.join(dir, "{consoli_date}.tar.gz".format(consoli_date=consoli_date))

        scrape_path = os.path.join(dir, consoli_date)

        LOGGER.info("Downloading files")
        download_dir(client, s3_bucket, "{consoli_date}/".format(consoli_date=consoli_date), scrape_path)

        LOGGER.info("Tar.gzing files")
        tar = tarfile.open(targz_path, "w:gz")
        tar.add(scrape_path, arcname=consoli_date)
        tar.close()

        LOGGER.info("Downloading tar.gz")
        client.upload_file(
            targz_path,
            s3_bucket,
            "{consoli_date}.tar.gz".format(consoli_date=consoli_date),
        )


def assert_dir_exists(path):
    """ Will check if directory tree in path exists. If not it created it.

    :param path: the path to check if it exists
    """
    try:
        os.makedirs(path)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise


def download_dir(client, bucket, path, target):
    """ Will recursively download the given S3 path to the target directory.

    :param client: S3 client to use.
    :param bucket: the name of the bucket to download from
    :param path: The S3 directory to download.
    :param target: the local directory to download the files to.
    """

    # Handle missing / at end of prefix
    if not path.endswith("/"):
        path += "/"

    paginator = client.get_paginator("list_objects_v2")
    for result in paginator.paginate(Bucket=bucket, Prefix=path):
        # Download each file individually
        for key in result["Contents"]:
            # Calculate relative path
            rel_path = key["Key"][len(path) :]
            # Skip paths ending in /
            if not key["Key"].endswith("/"):
                local_file_path = os.path.join(target, rel_path)
                # Make sure directories exist
                local_file_dir = os.path.dirname(local_file_path)
                assert_dir_exists(local_file_dir)
                client.download_file(bucket, key["Key"], local_file_path)


def handler(event, context):
    """Entry point for the AWS Lambda way of launching this script"""

    consolidate()


def main():
    consolidate()


if __name__ == "__main__":
    main()
