# ttc_subway_times
A scraper to grab and publish TTC subway arrival times. The ultimate goal of the project is to publish a dashboard of citizen-led performance metrics and do analysis of unreliability in order to build the political will to better public transit in Toronto.

## State of the project

We have a Python scraper running on AWS and submitting predicted subway arrivals to an AWS PostgreSQL database since late February 2017. We want to process this data to generate observed station arrival times for each train at each station. Have a look at [**How to Get Involved**](#how-to-get-involved). There was a couple month hiatus in data scraping because the database was full between August and November, but the scraper is now continuing to hum along nicely.

We're still trying to process the predicted arrival times we get from the API into reasonably reliable observed arrivals. This work is happening in a Jupyter Notebook [Filtering Observed Arrivals.ipynb](doc/Filtering%20Observed%20Arrivals.ipynb) . The work is actually mostly in SQL, despite being in a Python notebook. Feel free to follow along. More eyes on the data leads to better data.

### First Step Metric

**Buffer Time:** A measure of reliability useful for the customer: how much extra time a customer needs to buffer in order for their trip to be on time 1 day out of 20.

## Documentation
Have a look in the [`doc/`](doc/) folder for Jupyter Notebooks explaining how we explored developing this project and understanding the data.

### Data Flow and Data Structure
The scraper runs every minute when the TTC is in service. Each of these runs is logged in `polls`, with a unique `pollid` and a start and end time. 
During one run of the scraper, each station gets its predicted arrivals requested. This is logged in `requests`, with a unique `requestid` and noting which station it is using `stationid` and `lineid`. 
For each request, 3 predicted arrivals are recorded for each line and direction at that station. This is stored in `ntas_data` (Next Train Arrival System). This table notes the train's `traindirection` and its unique id `trainid`, the time until the train's arrival `timint` and a `train_message`, whether the train is arriving, at station, or is delayed.
**For more info:** have a look at the API exploration notebook under [`doc/API_exploration.ipynb`](https://github.com/CivicTechTO/ttc_subway_times/blob/master/doc/API_exploration.ipynb)

## Analysing the Data

If you don't want to set up the scraper yourself, and you want to look at historical data: read on! The data is currently stored in a PostgreSQL database on Amazon Relational Database Service (RDS). Have a look at [**How to Get Involved**](#how-to-get-involved) to find out how to get access to the data. 

Archives are provided in two formats: a `csv` for each of the three tables and a PostgreSQL database dump file. If you want to use R or Python to play with the data, you should be fine with the `csv` files, but if you want to play with the data in SQL, read on.

The database dump (`datadump.tar.gz`)is a directory format output of [`pg_dump`](https://devdocs.io/postgresql~9.6/app-pgdump). The dump command used is:
```shell
pg_dump -d ttcsubway -U username -h url.to.rds.amazonaws.com -F d -n public -n filtered -f datadump
```

To uncompress it:
```shell
tar xvzf datadump.tar.gz
```
And then to restore:
```shell
pg_restore -d ttc -c -O --if-exists --no-privileges datadump
```
Some notes on [restore](https://devdocs.io/postgresql~9.6/app-pgrestore):  
 - `-d` specifies the database. Since I'm using a database local to my computer, and I have a db username that shares my computer username, I don't need other authentication parameters. Your Mileage May Vary.
 - `-O` doesn't change owner of objects, so everything should be created as the user you connect to your database with
 - `-c` deletes and creates the tables again. If you already have data in your database, you may want to use the `-a` flag to specify data only, you may also want to specify `--inserts` which will insert each row separately. It's slow but it will prevent the entire restore from failing if you have a duplicate row.
 - `--if-exists` will silence errors due to objects already existing (or not existing)
 - `--no-privileges` prevents some annoying error messages because the username which created the dump (`raphael`) doesn't exist in your database
 - you may want to specify which schema to restore with `-n`, or which tables to restore with `-t`

## Setting up the scraper

**Note: You don't need to set up the scraper to analyze the data, but if you want to improve the scraper go ahead.**

Set up a python3 environment and install requirements with the below command. If you want to modify the Jupyter notebooks to explore the data remove the `#` symbols below `# if using jupyter notebooks`
```shell
pip install -r requirements.txt
```
### aiohttp

We're using [this library](https://aiohttp.readthedocs.io/en/stable/) to improve speed of polling the TTC's API by making requests asynchronous. Installation was... fine in Ubuntu 16.04 and OSX, had some hiccoughs in Debian/Raspbian. Stay tuned.

## The Scraper
We can retrieve the state of the subway via the `ttc_scraper_api.py` script.

This will fetch the arrival information for each subway station and persist it. The options to 
this are specified in the help, it needs an action as well as  a destination 
(e.g. scrape and --postgres).

### Data Destinations
The scraper script is able to persist the results to either Postgres, or AWS S3. One (and only one)
of these must be chosen with either the --postgres or the --s3 flag.

#### S3
If the --s3 flag is set then the S3_BUCKET environmental variable must be set which specifies 
the bucket. 

This script generates JSONS of the results and puts them into 
`S3://<AWS S3 BUCKET>/<SERVICE DATE>/<TIMESTAMP.tar.gz>`, where the service date is the date 
that service started on (e.g. before the subway shutdown for the night).

These tarballs have three JSONS 

- <TIMESTAMP>/ntas.json
- <TIMESTAMP>/requests.json
- <TIMESTAMP>/polls.json

#### Postgres

If the --postgres flag is set the results will be persisted to Postgresql. You can find 
instructions to get the latest and greatest version [here](https://www.postgresql.org/). 
After you've set up your database you can run the contents of `create_tables.sql` in a pgAdmin 
query window (or run it as a sql query). 

Credentials for the database should be stored in db.cfg, an example is:

```
[DBSETTINGS]
database=ttc
host=host.ip.address
user=yourusername
password=pw
```

## Automating the Scraper Runs

There are two ways that the scraper can be automated, via cron, or via Serverless
with AWS Lambda. No matter how you choose to run it the scraper runs with 
a `python ttc_scraper_api.py` command.

### AWS Lambda Scraping
There is a mode which will allow scraping via AWS Lambda 
with logging added to AWS Cloudwatch. This mode uses the Serverless framework.

The [Serverless](https://serverless.com/) framework is a suite of tooling which allows the 
easy deployment and management of serverless code.

This allows us to run this code without having to spin up/monitor for an instance 
manually. And since we only pay for the code when it is running the compute 
costs are nearly zero.

#### Setup
In addition to installing the Python requirements (above) 
we need to install the Serverless framework with npm by running `npm install`
in the project root. 

Move serverless.yml.template to serverless.yml and replace the bucket name with the actual values

At the time of writing the schedule line in serverless.yml is set as

```yaml
    rate: cron(* 0-2,5-23 * * ? *)
```
which means that it should run every minute from 5am to 2am every day. More 
information on this cron line can be found on the [AWS documentation](https://docs.aws.amazon.com/lambda/latest/dg/tutorial-scheduled-events-schedule-expressions.html),
in this documentation references to UTC should be ignored, we use the 
'serverless-local-schedule' package which allows us to specify crons in local 
time rather than UTC (otherwise the behaviour would change during daylight 
savings time).

Tell Serverless which AWS creds you would like to use with  

`serverless config credentials --provider aws --key <AWS_ACCESS_KEY> --secret <AWS_SECRET_KEY>`

Finally deploy the function with 
```shell
serverless deploy -v
```

Logs are automatically persisted to Cloudwatch. 

### Cron
If you would like to run it on your local machine, the best way to do it is to set
up a cron to periodically run the scraper command. 

#### Linux/Unix
If you use Mac or Linux, add the below to cron. Don't forget to change `/path/to/ttc_api_scraper.py`
These command will run the scraper from 5am to 2am on weekdays, and from 5am to 3am on weekends. 
This also persists the results to Postgres.

```shell
# m h  dom mon dow   command
* 5-23 * * 1-5 cd /path/to/repo/ttc_subway_times/ && bin/python3 ttc_api_scraper.py --postgres
* 0-1 * * 1-5 cd /path/to/repo/ttc_subway_times/ && bin/python3 ttc_api_scraper.py --postgres
* 5-23 * * 6-7 cd /path/to/repo/ttc_subway_times/ && bin/python3 ttc_api_scraper.py --postgres
* 0-2 * * 6-7 cd /path/to/repo/ttc_subway_times/ && bin/python3 ttc_api_scraper.py --postgres
```
Or if you want to run every 20s while filtering out any "arriving" records

```shell

* 5-23 * * 1-5 cd ~/git/ttc_subway_times && bin/python3 ttc_api_scraper.py --filter --schemaname filtered
* 0-1 * * 1-5 cd ~/git/ttc_subway_times && bin/python3 ttc_api_scraper.py --filter --schemaname filtered
* 5-23 * * 6-7 cd ~/git/ttc_subway_times && bin/python3 ttc_api_scraper.py --filter --schemaname filtered
* 0-2 * * 6-7 cd ~/git/ttc_subway_times && bin/python3 ttc_api_scraper.py --filter --schemaname filtered
* 5-23 * * 1-5 (sleep 20; cd ~/git/ttc_subway_times && bin/python3 ttc_api_scraper.py --filter --schemaname filtered)
* 0-1 * * 1-5 (sleep 20; cd ~/git/ttc_subway_times && bin/python3 ttc_api_scraper.py --filter --schemaname filtered)
* 5-23 * * 6-7 (sleep 20; cd ~/git/ttc_subway_times && bin/python3 ttc_api_scraper.py --filter --schemaname filtered)
* 0-2 * * 6-7 (sleep 20; cd ~/git/ttc_subway_times && bin/python3 ttc_api_scraper.py --filter --schemaname filtered)
* 5-23 * * 1-5 (sleep 40; cd ~/git/ttc_subway_times && bin/python3 ttc_api_scraper.py --filter --schemaname filtered)
* 0-1 * * 1-5 (sleep 40; cd ~/git/ttc_subway_times && bin/python3 ttc_api_scraper.py --filter --schemaname filtered)
* 5-23 * * 6-7 (sleep 40; cd ~/git/ttc_subway_times && bin/python3 ttc_api_scraper.py --filter --schemaname filtered)
* 0-2 * * 6-7 (sleep 40; cd ~/git/ttc_subway_times && bin/python3 ttc_api_scraper.py --filter --schemaname filtered)
```

#### Windows users

Use Task Scheduler.

#### cronic.py
If the above sounds complicated, here's a simple looping script that calls `ttc_api_scraper.py` every minute during the TTC's operating hours. Just start it in your command line with  
```shell
python cronic.py
```

And let it collect the data.


## How to Get Involved

We discuss the project on [CivicTechTO's Slack Team](https://civictechto-slack-invite.herokuapp.com/) on the `#transportation` channel. This is probably the best place to introduce yourself and ask how you can participate. There are links in that channel to get access to ~1 month of the raw data in a `csv` or a PostgreSQL dump. You can also ask about getting read access to the database. Alternatively you can set up the scraper yourself and play with your own archive locally, hack away!

If you're exploring the data, please write up your exploration in a Jupyter Notebook/RMarkdown/Markdown file and place it in the `doc/` folder and submit a Pull Request with details on what you explored.

Otherwise have a look at [open issues](https://github.com/CivicTechTO/ttc_subway_times/issues) and comment on any thing you think you could contribute to or open your own issue if you notice something to improve upon in the code.

## Sources of Inspiration
Boldly following in [others' footsteps](https://blog.sammdot.ca/pockettrack-tracking-subway-trains-is-hard-9c8fdfb7fd3c?source=collection_home---4------0----------)
See more on the [Resources page](https://github.com/CivicTechTO/ttc_subway_times/wiki/Resources)
