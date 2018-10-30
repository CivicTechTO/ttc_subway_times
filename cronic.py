# dumb looping script for those who do not love cron

from time import sleep
import subprocess
from datetime import datetime

def run_parallel():
    while True:
        subprocess.Popen("python src/ttc_api_scraper/__init__.py scrape", shell=True)
        sleep(10)

def run_blocking():
    period = 10
    while True:
        st = datetime.now()
        # sleep 5 mins then check time again if after operating hours
        if ((st.hour >= 2 and st.minute > 15) or (st.hour >= 3)) and ((st.hour < 5) or (st.hour < 6 and st.minute < 45)):
            sleep(300)
            print("After operating hours: " + str(st) + " -- Sleeping 5 mins.")
            continue

        subprocess.run("python src/ttc_api_scraper/__init__.py scrape", shell=True)
        et = datetime.now()
        delta = et-st
        if(delta.seconds < period):
            sleep(period - delta.seconds)


def main():
    # run_parallel()
    run_blocking()

if __name__ == "__main__":
    main()
