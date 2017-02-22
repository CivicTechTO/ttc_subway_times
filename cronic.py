# dumb looping script for those who do not love cron

from time import sleep
import subprocess
from datetime import datetime

def run_parallel():
	while True:
		subprocess.Popen("python ttc_api_scraper.py", shell = True)
		sleep(10)

def run_blocking():
	period = 10
	while True:
		st = datetime.now()
		subprocess.run("python ttc_api_scraper.py", shell = True)
		et = datetime.now()
		# quit if after operating hours
		if et.hour > 2 & et.minute > 15 & et.hour < 4: 
			exit()
		delta = et-st
		if(delta.seconds < period):
			sleep(period - delta.seconds)


def main():
	# run_parallel()
	run_blocking()

if __name__ == "__main__":
    main()