# TTC Subway times

This is a project implementing a ‘scraper’ to grab and publish TTC subway arrival times against citizen-led performance metrics analyzing service timeliness and reliability.  The end goal is to maintain and publish this performance dashboard building consensus on service quality betterment over public transit in Toronto.

# State of the project

We have a Python scraper running on AWS saving predicted subway arrivals since late February 2017.  We need to process this data to generate observed station arrival times for each train at each station.  There was a couple month hiatus in data scraping because the database was full between August and November, but the scraper is now continuing to hum along nicely.

We're still trying to process the predicted arrival times obtained from the API into reasonably reliable state.  This work is happening in a Jupyter Notebook [Filtering Observed Arrivals.ipynb](doc/Filtering%20Observed%20Arrivals.ipynb); it is mostly in SQL, despite being in a Python notebook.

Take a look at [How to Get Involved](#how-to-get-involved) with your expertise. Feel free to follow along; your informed feedback will surely lead to better data.

# First Step Metric

**Buffer Time** - A measure of reliability useful for the rider:

- how much extra time he/she needs to buffer in order for their trip to be on time 1 trip out of 20.

# Documentation

Review the [doc/](doc/) folder for the [Jupyter Notebooks](https://jupyter-notebook-beginner-guide.readthedocs.io/en/latest/what_is_jupyter.html#id5) explaining how we explored developing this project and understanding the data. Jupyter notebooks are a way of having code, descriptive text, and output together in one document to present a narrative around data exploration. 

**If you're interested in a Data Dictionary**, [click here](doc/DataDictionary.md) (it's also in the `doc/` folder).

## Presentations

You can watch Raphael give a presentation to CivicTech Toronto January 15, 2019 on [this blurry Youtube](https://youtu.be/DtNR5whN9gg?t=728) and the slides are [here](https://radumas.info/presentations/20190115#/)

# Data Flow and Data Structure

The scraper runs every minute during TTC service hours.  Each of these runs is termed a `polls`
and has a start / end time.  During one run of the scraper, each station gets its predicted arrivals returned as a `request`, noting which station it is using `stationid` and `lineid`. 
For each request, 3 predicted arrivals are recorded for each line and direction at that station. These responses include the train's `traindirection` and its unique ID `trainid`, the time until the train's arrival `timint` and a `train_message`, whether the train is arriving, at station, or is delayed.

For more info: review the API exploration notebook under [`doc/API_exploration.ipynb`](https://github.com/CivicTechTO/ttc_subway_times/blob/master/doc/API_exploration.ipynb)

# Analyzing the Data

:warning: **We're not entirely sure how to make this work, you can get data by finding us in the `#transportation` channel on [Slack](https://civictechto-slack-invite.herokuapp.com/). If you think you can help with this, check out [issue #59](https://github.com/CivicTechTO/ttc_subway_times/issues/59)**

Historical data is stored in the s3://ttc.scrape bucket, the fetch_s3.py script can be used to automatically fetch and assemble this data. Its usage is

```shell
python3 fetch_s3.py --bucket ttc.scrape --start_date 2018-12-02 --end_date 2018-12-05 --output_dir out/
```

If end date is omitted it is taken to be the latest available date. This script can only select by day.

This will generate three CSVs in the output_dir which can be copied into the Postgres database with the following SQL commands

```SQL
COPY polls FROM '/path/to/polls.csv' DELIMITER ',' CSV HEADER;
COPY requests FROM '/path/to/requests.csv' DELIMITER ',' CSV HEADER;
COPY ntas_data FROM '/path/to/responses.csv' DELIMITER ',' CSV HEADER;
```

# Automating the Scraper Runs

There are two ways that the scraper can be automated, via Docker/cron, or via Serverless with AWS Lambda. No matter how you choose to run it the scraper runs through ttc_scraper_api.py

## Storage Backends

There are two ways the data can be stored once it has been scraped, AWS S3 and Postgres.

AWS S3 stores each scrape in a JSON collected by service day (see Consolidate function). This requires an AWS account. This can be enabled by with the `--s3` flag. The advantage of S3 is that it requires no persistant server, and is extremely cheap. Its main disadvantage is that the data is not as easily queryable as an SQL database and some steps are required before it can be queried in SQL (see [Analyzing the Data](#analyzing-the-data)). This storage method is well suited to the AWS Lambda scraping mode.

Postgres requires a running Postgres instance. While the data is immediately queryable, it requires a Postgres server to be always running, which increases the work, risk and cost of the project. This can be selected with the `--postgres` flag and is most often used with the Docker/Cron scraping mode.

Both modes store the same data, in largely the same structure (nested JSONs vs tables with joinable keys).

## AWS Lambda Scraping

There is a mode which will allow scraping via AWS Lambda with logging added to AWS Cloudwatch. This mode uses the Serverless framework.

The [Serverless](https://serverless.com/) framework is a suite of tooling which allows the easy deployment and management of serverless code.

This allows us to run this code without having to spin up/monitor for an instance manually. And since we only pay for the code when it is running the compute costs are nearly zero.

### Setup

In addition to installing the Python [requirements](requirements.txt) we need to install the [Serverless framework](https://serverless.com/) with [npm](https://www.npmjs.com/get-npm) ([install instructions for Ubuntu](https://www.digitalocean.com/community/tutorials/how-to-install-node-js-on-ubuntu-18-04) by running `npm install` in the project root. 

On Ubuntu you'll need to add the `serverless` binary to your `PATH` variable with `PATH="$PATH:/[PATH/TO]/ttc_subway_times/node_modules/serverless/bin/"` (replace `[PATH/TO]` with the absolute path to the repository). This will only be temporary for your session, if you're going to use `serverless` for other projects, you should probably install it globally with `sudo npm install -g`.

Tell Serverless which AWS creds you would like to use with:

`serverless config credentials --provider aws --key <AWS_ACCESS_KEY> --secret <AWS_SECRET_KEY>`

Creating these credentials must be done through your AWS account. A good guide to this
process can be found on the [Serverless Website](https://serverless.com/framework/docs/providers/aws/guide/credentials/)

#### Configure the `serverless.yml`

The template `serverless.yml` is configured to use dev and prod environments. This will create functions with `dev-` or `prod-` prepended to them, and will also direct output to the buckets that are defined in the custom section

Move `serverless.yml.template` to `serverless.yml`.

[Create an S3 bucket](https://s3.console.aws.amazon.com/s3/home). Replace the angle bracketed bucket names (under the `custom:` properties at the end of the document with the **names** of the buckets you created.

At the time of writing the schedule line in serverless.yml is set as

```yaml
    rate: cron(* 0-2,5-23 * * ? *)
```
which means that it should run every minute from 5am to 2am every day. More information on this cron line can be found on the [AWS documentation](https://docs.aws.amazon.com/lambda/latest/dg/tutorial-scheduled-events-schedule-expressions.html), in this documentation references to UTC should be ignored, we use the 'serverless-local-schedule' package which allows us to specify crons in local time rather than UTC (otherwise the behaviour would change during daylight savings time).

### Deploy

You'll need to install docker for this step ([Ubuntu install instructions](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-18-04)).

Finally deploy the function with 
```shell
serverless deploy -v
```
This command will deploy to the dev environment by default, the environment can be specified on the command line with the `--stage` flag (acceptable values for this project are `dev` and `prod`)

Logs are automatically persisted to Cloudwatch.

### Consolidate Function
If you are scraping with the AWS Lambda function with the S3 data destination it will write a JSON to `s3://<BUCKET>/<SERVICE DATE>`. As the scraper runs once per minute, this results in a very large number of small files, which are inefficient and expensive to store and transfer.

To remedy this there is a second 'consolidate' serverless function which runs at the end of every service day and combines the previous day into a .tar.gz file, storing it at `s3://<BUCKET>/<SERVICE_DATE>.tar.gz`.

This isn't relevant if you are storing the data in Postgres with the Lambda scraper, but this configuration will require you to modify serverless.yml.

## Docker/Cron Scraping

Another way to run the scraper is to run it periodically a Cron in a Docker container. This is useful if you would like to scrape from a computer that is always left on.

Follow the below command to set up a Python 3 environment and install requirements.

<details><summary>Running inside docker</summary>
Follow the instructions [here](https://docs.docker.com/compose/install/) to get `docker-compose`.

All you need to do is `docker-compose run --rm scraper`.
This will setup a database container, initialize the tables, and then run the initial scrape.

To have cli access to the data you can use `docker-compose exec db psql -U postgres -d ttc`.
Commands of interest:
- `\?`: list the help information for all the special commands
- `\h`: list all the sql commands that are available
- `\q`: quit the console
</details>

### Linux/Unix

To use Mac or Linux, add the following to cron. Don't forget to change `/path/to/ttc_api_scraper.py`.

Note: These commands assume postgres as a data destination.

```bash
# m h  dom mon dow   command
* 5-23 * * 1-5 cd /path/to/repo/ttc_subway_times/ && python3 ttc_api_scraper.py --postgres
* 0-1 * * 1-5 cd /path/to/repo/ttc_subway_times/ && python3 ttc_api_scraper.py --postgres
* 5-23 * * 6-7 cd /path/to/repo/ttc_subway_times/ && python3 ttc_api_scraper.py --postgres
* 0-2 * * 6-7 cd /path/to/repo/ttc_subway_times/ && python3 ttc_api_scraper.py --postgres
```
Or to run every 20s while filtering out any "arriving" records
```bash
* 5-23 * * 1-5 cd /path/to/repo/ttc_subway_times/ && python3 ttc_api_scraper.py --filter --schemaname filtered --postgres
* 0-1 * * 1-5 cd /path/to/repo/ttc_subway_times/ && python3 ttc_api_scraper.py --filter --schemaname filtered --postgres
* 5-23 * * 6-7 cd /path/to/repo/ttc_subway_times/ && python3 ttc_api_scraper.py --filter --schemaname filtered --postgres
* 0-2 * * 6-7 cd /path/to/repo/ttc_subway_times/ && python3 ttc_api_scraper.py --filter --schemaname filtered --postgres
* 5-23 * * 1-5 (sleep 20; cd /path/to/repo/ttc_subway_times/ && python3 ttc_api_scraper.py --filter --schemaname filtered  --postgres)
* 0-1 * * 1-5 (sleep 20; cd /path/to/repo/ttc_subway_times/ && python3 ttc_api_scraper.py --filter --schemaname filtered  --postgres)
* 5-23 * * 6-7 (sleep 20; cd /path/to/repo/ttc_subway_times/ && python3 ttc_api_scraper.py --filter --schemaname filtered --postgres)
* 0-2 * * 6-7 (sleep 20; cd /path/to/repo/ttc_subway_times/ && python3 ttc_api_scraper.py --filter --schemaname filtered --postgres)
* 5-23 * * 1-5 (sleep 40; cd /path/to/repo/ttc_subway_times/ && python3 ttc_api_scraper.py --filter --schemaname filtered --postgres)
* 0-1 * * 1-5 (sleep 40; cd /path/to/repo/ttc_subway_times/ && python3 ttc_api_scraper.py --filter --schemaname filtered --postgres)
* 5-23 * * 6-7 (sleep 40; cd /path/to/repo/ttc_subway_times/ && python3 ttc_api_scraper.py --filter --schemaname filtered)
* 0-2 * * 6-7 (sleep 40; cd /path/to/repo/ttc_subway_times/ && python3 ttc_api_scraper.py --filter --schemaname filtered --postgres)
```

### Windows users

Use Task Scheduler.

### cronic.py

If the above sounds complicated, here's a simple looping script that calls `ttc_api_scraper.py` every minute during the TTC's operating hours. Just start it in your command line with
```shell
python cronic.py
```

And let it collect the data.

# Database setup
If you would like to use Postgres as a data repository, the database engine used to store the data is PostgreSQL. Instructions to obtain the latest and greatest version are [here](https://www.postgresql.org/). After setting up your database, you can run the contents of `create_tables.sql` in a pgAdmin query window (or run it as a sql query).

You will also need to edit `db.cfg`
```ini
[DBSETTINGS]
database=ttc
host=host.ip.address
user=yourusername
password=pw
```


# How to Get Involved

We discuss the project on [CivicTechTO's Slack Team](https://civictechto-slack-invite.herokuapp.com/) on the `#transportation` channel. This is probably the best place to introduce yourself and ask how you can participate. There are links in that channel to get access to ~1 month of the raw data in a `csv` or a PostgreSQL dump. You can also ask about getting read access to the database. Alternatively you can set up the scraper yourself and play with your own archive locally, hack away!

If you're exploring the data, please write up your exploration in a Jupyter Notebook/RMarkdown/Markdown file and place it in the `doc/` folder and submit a Pull Request with details on what you explored.

Otherwise have a look at [open issues](https://github.com/CivicTechTO/ttc_subway_times/issues) and comment on any thing you think you could contribute to or open your own issue if you notice something to improve upon in the code.

# Sources of Inspiration

Boldly following in [others' footsteps](https://blog.sammdot.ca/pockettrack-tracking-subway-trains-is-hard-9c8fdfb7fd3c?source=collection_home---4------0----------)
See more on the [Resources page](https://github.com/CivicTechTO/ttc_subway_times/wiki/Resources)
