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

### Database setup

The database engine used to store the data is PostgreSQL, you can find instructions to get the latest and greatest version [here](https://www.postgresql.org/). After you've set up your database you can run the contents of `create_tables.sql` in a pgAdmin query window (or run it as a sql query). 

#### Edit `db.cfg`

```
[DBSETTINGS]
database=ttc
host=host.ip.address
user=yourusername
password=pw
```


### Automating the scraper runs

The scraper runs with a `python ttc_scraper_api.py` command. It doesn't have any command line options (at the moment). We've been running this from 6AM to 1AM

#### Linux/Unix
If you use Mac or Linux, add the below to cron. Don't forget to change `/path/to/ttc_api_scraper.py`

```shell
# m h  dom mon dow   command
* 5-23 * * 1-5 cd /path/to/repo/ttc_subway_times/ && bin/python3 ttc_api_scraper.py
* 0-1 * * 1-5 cd /path/to/repo/ttc_subway_times/ && bin/python3 ttc_api_scraper.py
* 5-23 * * 6-7 cd /path/to/repo/ttc_subway_times/ && bin/python3 ttc_api_scraper.py
* 0-2 * * 6-7 cd /path/to/repo/ttc_subway_times/ && bin/python3 ttc_api_scraper.py
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
