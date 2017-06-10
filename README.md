# ttc_subway_times
A scraper to grab and publish TTC subway arrival times. The ultimate goal of the project is to publish a dashboard of citizen-led performance metrics and do analysis of unreliability in order to build the political will to better public transit in Toronto.

## State of the project

The scraper is running on AWS and submitting data to an AWS PostgreSQL database since late February 2017. We want to process this data to generate stop arrival times for each train at each station. Have a look at [**How to Get Involved**](#how-to-get-involved).

## Documentation
Have a look in the [`doc/`](doc/) folder for Jupyter Notebooks explaining how we explored developing this project and understanding the data.

## Setting up the scraper

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
user=pi
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

Otherwise have a look at [open issues](https://github.com/CivicTechTO/ttc_subway_times/issues) and comment on any thing you think you could contribute to or open your own issue if you notice something in the code.

## Sources of Inspiration
Boldly following in [others' footsteps](https://blog.sammdot.ca/pockettrack-tracking-subway-trains-is-hard-9c8fdfb7fd3c?source=collection_home---4------0----------)
