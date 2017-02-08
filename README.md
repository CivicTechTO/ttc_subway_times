# ttc_subway_times
A scraper to grab and publish TTC subway arrival times.
Boldly following in [others' footsteps](https://blog.sammdot.ca/pockettrack-tracking-subway-trains-is-hard-9c8fdfb7fd3c?source=collection_home---4------0----------)

## Documentation
Have a look in the `doc/` folder for Jupyter Notebooks explaining how we explored developing this project and understanding the data.

## Setting up the scraper

Set up a python3 environment and install requirements with the below command. If you want to modify the Jupyter notebooks to explore the data remove the `#` symbols below `# if using jupyter notebooks`
```shell
pip install requirements.txt
```

### Database setup

The database engine used to store the data is PostgreSQL, you can find instructions to get the latest and greatest version [here](https://www.postgresql.org/). After you've set up your database you can run the contents of `create_tables.sql` in a pgAdmin query window (or run it as a sql query). 

### Automating the scraper runs

The scraper runs with a `python ttc_scraper_api.py` command. It doesn't have any command line options (at the moment). We've been running this from 6AM to 1AM, so add the below to cron if you use UNIX (Mac or Linux). Don't forget to change `/path/to/ttc_api_scraper.py`

`TODO`

#### Windows users

Use Task Scheduler.