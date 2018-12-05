# TTC Subway times

This is a project implementing a ‘scraper’ to grab and publish TTC subway arrival times against citizen-led performance metrics analyzing service timeliness and reliability.  The end goal is to maintain and publish this performance dashboard building consensus on service quality betterment over public transit in Toronto.

## State of the project

We have a Python scraper running on AWS submitting predicted subway arrivals to an AWS PostgreSQL database since late February 2017.  We need to process this data to generate observed station arrival times for each train at each station.  There was a couple month hiatus in data scraping because the database was full between August and November, but the scraper is now continuing to hum along nicely.

We're still trying to process the predicted arrival times obtained from the API into reasonably reliable state.  This work is happening in a Jupyter Notebook [Filtering Observed Arrivals.ipynb](doc/Filtering%20Observed%20Arrivals.ipynb); it is mostly in SQL, despite being in a Python notebook.

Take a look at [How to Get Involved](#how-to-get-involved) with your expertise. Feel free to follow along; your informed feedback will surely lead to better data.

## First Step Metric

**Buffer Time** - A measure of reliability useful for the rider:

- how much extra time he/she needs to buffer in order for their trip to be on time 1 trip out of 20.

## Documentation

Review the [doc/](doc/) folder for the [Jupyter Notebooks](https://jupyter-notebook-beginner-guide.readthedocs.io/en/latest/what_is_jupyter.html#id5) explaining how we explored developing this project and understanding the data. Jupyter notebooks are a way of having code, descriptive text, and output together in one document to present a narrative around data exploration. 

If you're interested in a Data Dictionary, [click here](doc/DataDictionary.md) (it's also in the `doc/` folder.

## Data Flow and Data Structure

The scraper runs every minute during TTC service hours.  Each of these runs is logged in `polls`, with a unique `pollid` and a start / end time.  During one run of the scraper, each station gets its predicted arrivals requested. This is logged in `requests`, with a unique `requestid` and noting which station it is using `stationid` and `lineid`. For each request, 3 predicted arrivals are recorded for each line and direction at that station.  This is stored in `ntas_data` (Next Train Arrival System). This table notes the train's `traindirection` and its unique ID `trainid`, the time until the train's arrival `timint` and a `train_message`, whether the train is arriving, at station, or is delayed.

For more info: review the API exploration notebook under [`doc/API_exploration.ipynb`](https://github.com/CivicTechTO/ttc_subway_times/blob/master/doc/API_exploration.ipynb)

## Analyzing the Data

The historical data is currently stored in a PostgreSQL database on Amazon Relational Database Service (RDS).  Archives are provided in two formats: a csv for each of the three tables and a PostgreSQL database dump file.

Without setting up the scraper yourself, follow this section to access the data: [How to Get Involved](#how-to-get-involved).
Use R or Python to play with the csv files.

To play with the data in SQL, the database dump `datadump.tar.gz` is a directory format output of [`pg_dump`](https://devdocs.io/postgresql~9.6/app-pgdump).

The dump command is:
```shell
pg_dump -d ttcsubway -U username -h url.to.rds.amazonaws.com -F d -n public -n filtered -f datadump
```

To uncompress it:
```shell
tar xvzf datadump.tar.gz
```

And to restore:
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

To improve the scraper, setting up the scraper is needed.  The scraper is not needed to analyze the data.
Follow the below command to set up a python3 environment and install requirements.

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

```bash
pip install -r requirements.txt
```
To modify the Jupyter notebooks to explore the data, remove the # symbols below # if using jupyter notebooks

### aiohttp

We use this library for speed of polling the TTC's API by making the requests asynchronous.  Installation was... fine in Ubuntu 16.04 and OSX, had some hiccoughs in Debian/Raspbian. Stay tuned.

### Database setup

The database engine used to store the data is PostgreSQL. Instructions to obtain the latest and greatest version are [here](https://www.postgresql.org/). After setting up your database, you can run the contents of `create_tables.sql` in a pgAdmin query window (or run it as a sql query).

You will also need to edit `db.cfg`
```ini
[DBSETTINGS]
database=ttc
host=host.ip.address
user=yourusername
password=pw
```

### Automating the scraper runs

The scraper runs with a `python ttc_scraper_api.py` command. It doesn't have any command line options (at the moment).  We've been running this from 6AM to 1AM

#### Linux/Unix

To use Mac or Linux, add the following to cron. Don't forget to change `/path/to/ttc_api_scraper.py`
```bash
# m h  dom mon dow   command
* 5-23 * * 1-5 cd /path/to/repo/ttc_subway_times/ && bin/python3 ttc_api_scraper.py
* 0-1 * * 1-5 cd /path/to/repo/ttc_subway_times/ && bin/python3 ttc_api_scraper.py
* 5-23 * * 6-7 cd /path/to/repo/ttc_subway_times/ && bin/python3 ttc_api_scraper.py
* 0-2 * * 6-7 cd /path/to/repo/ttc_subway_times/ && bin/python3 ttc_api_scraper.py
#Or to run every 20s while filtering out any "arriving" records
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
