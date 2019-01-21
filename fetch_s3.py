# coding: utf8
from collections import namedtuple
import datetime
import glob
from itertools import zip_longest
import json
import os
import tempfile
import tarfile

import boto3
import click
from joblib import Parallel, delayed
import pandas as pd
from retrying import retry
from tqdm import tqdm

Poll = namedtuple("Poll", ["pollid", "poll_start", "poll_end"])
Request = namedtuple(
    "Request",
    [
        "requestid",
        "data_",
        "stationid",
        "lineid",
        "all_stations",
        "create_date",
        "pollid",
        "request_date",
    ],
)
Response = namedtuple(
    "Response",
    [
        "requestid",
        "id",
        "station_char",
        "subwayline",
        "system_message_type",
        "timint",
        "traindirection",
        "trainid",
        "train_message",
        "train_dest",
    ],
)


@retry(stop_max_attempt_number=5)
def download_extract(bucket, file, dir):
    client = boto3.client("s3")

    localfile = os.path.join(dir, file[1])

    print("Fetching {targz}".format(targz=file))
    client.download_file(bucket, file, localfile)

    print("Extracting {targz}".format(targz=file))
    tar = tarfile.open(localfile, "r:gz")
    tar.extractall(path=dir)
    tar.close()


def grouper(iterable, n, fillvalue=None):
    "Collect data into fixed-length chunks or blocks"
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)


def fetch_and_transform(targzs, output_dir):
    with tempfile.TemporaryDirectory() as tmpdir:
        Parallel(n_jobs=15)(delayed(download_extract)(file[0], file[1], tmpdir) for file in targzs)
        jsons_to_csv(tmpdir, output_dir)


def jsons_to_csv(dir, output_dir, chunksize=2000):

    pollid = 0
    requestid = 0

    mode = "w"
    header = True

    files = glob.glob(os.path.join(dir, "**/*.json"), recursive=True)
    pbar = tqdm(total=len(files))
    for i, g in enumerate(grouper(files, chunksize, fillvalue=None)):

        polls = []
        requests = []
        responses = []

        if i != 0:
            mode = "a"
            header = False

        for filename in g:

            if filename is None:
                continue

            pollid, requestid, p, r, resp = parse_json(filename, pollid, requestid)
            polls.extend(p)
            requests.extend(r)
            responses.extend(resp)

        pd.DataFrame.from_records(polls, columns=polls[0]._fields).to_csv(
            os.path.join(output_dir, "polls.csv"), index=False, mode=mode, header=header
        )

        pd.DataFrame.from_records(requests, columns=requests[0]._fields).to_csv(
            os.path.join(output_dir, "requests.csv"), index=False, mode=mode, header=header
        )

        pd.DataFrame.from_records(responses, columns=responses[0]._fields).to_csv(
            os.path.join(output_dir, "responses.csv"), index=False, mode=mode, header=header
        )

        pbar.update(chunksize)
    pbar.close()


def parse_json(json_path, pollid, requestid):

    polls = []
    requests = []
    responses = []

    with open(json_path) as f:
        json_file = json.load(f)

        for poll in json_file:
            pollid += 1
            polls.append(Poll(pollid=pollid, poll_start=poll["start"], poll_end=poll["end"]))

            for request in poll["requests"]:
                requestid += 1
                requests.append(
                    Request(
                        requestid=requestid,
                        data_=request["data_"],
                        stationid=request["stationid"],
                        lineid=request["lineid"],
                        all_stations=request["all_stations"],
                        create_date=request["create_date"],
                        pollid=pollid,
                        request_date=request["request_date"],
                    )
                )

                for response in request["responses"]:
                    responses.append(
                        Response(
                            requestid=requestid,
                            id=response["id"],
                            station_char=response["station_char"],
                            subwayline=response["subwayline"],
                            system_message_type=response["system_message_type"],
                            timint=response["timint"],
                            traindirection=response["traindirection"],
                            trainid=response["trainid"],
                            train_message=response["train_message"],
                            train_dest=response.get("train_dest", ""),
                        )
                    )

    return pollid, requestid, polls, requests, responses


@click.command()
@click.option("--bucket")
@click.option("--output_dir", help="The directory to output CSVs to", required=False)
@click.option("--start_date", help="Start date in YYYY-MM-DD format")
@click.option("--end_date", help="End date in YYYY-MM-DD format", required=False)
def fetch_s3(bucket, output_dir, start_date, end_date=None):
    client = boto3.client("s3")

    start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")

    if end_date is not None:
        end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")

    to_download = []

    paginator = client.get_paginator("list_objects_v2")
    for result in paginator.paginate(Bucket=bucket):
        for key in result["Contents"]:
            if os.path.basename(key["Key"])[-7:] == ".tar.gz":
                file_date = datetime.datetime.strptime(
                    os.path.basename(key["Key"][:-7]), "%Y-%m-%d"
                )

                if (file_date < start_date) or ((end_date is not None) and (file_date > end_date)):
                    continue
                to_download.append((bucket, key["Key"]))

    fetch_and_transform(to_download, output_dir)


if __name__ == "__main__":
    fetch_s3()
