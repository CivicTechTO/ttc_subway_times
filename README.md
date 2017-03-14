# ttc_subway_times
A scraper to grab and publish TTC subway arrival times. The ultimate goal of the project is to publish a dashboard of citizen-led performance metrics and do analysis of unreliability in order to build the political will to better public transit in Toronto.

## Documentation
Have a look in the `doc/` folder for Jupyter Notebooks explaining how we explored developing this project and understanding the data.

## Setting up the scraper

Set up a python3 environment and install requirements with the below command. If you want to modify the Jupyter notebooks to explore the data remove the `#` symbols below `# if using jupyter notebooks`
```shell
pip install -r requirements.txt
```
### aiohttp

We're using [this library](https://aiohttp.readthedocs.io/en/stable/) to improve speed of polling the TTC's API by making requests asynchronous. Installation was... fine in Ubuntu 16.04 and OSX, had some hiccoughs in Debian/Raspbian. Stay tuned.

### Database setup

The database engine used to store the data is PostgreSQL, you can find instructions to get the latest and greatest version [here](https://www.postgresql.org/). After you've set up your database you can run the contents of `create_tables.sql` in a pgAdmin query window (or run it as a sql query). 

### Automating the scraper runs

The scraper runs with a `python ttc_scraper_api.py` command. It doesn't have any command line options (at the moment). We've been running this from 6AM to 1AM

#### Linux/Unix
If you use Mac or Linux, add the below to cron. Don't forget to change `/path/to/ttc_api_scraper.py`

`TODO`

#### Windows users

Use Task Scheduler.

#### cronic.py
If the above sounds complicated, here's a simple looping script that calls `ttc_api_scraper.py` every minute during the TTC's operating hours. Just start it in your command line with  
```shell
python cronic.py
```

And let it collect the data.

## How to Get Involved

We discuss the project on [CivicTechTO's Slack Team](https://civictechto-slack-invite.herokuapp.com/) on the `#transportation` channel. This is probably the best place to introduce yourself and ask how you can participate.

Otherwise have a look at open issues and comment on any thing you think you could contribute to or open your own issue if you notice something in the code.

## Sources of Inspiration
Boldly following in [others' footsteps](https://blog.sammdot.ca/pockettrack-tracking-subway-trains-is-hard-9c8fdfb7fd3c?source=collection_home---4------0----------)
