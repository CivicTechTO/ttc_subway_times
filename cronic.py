# dumb looping script for those who do not love cron

from time import sleep
import subprocess

def main():
	while True:
		#subprocess.run("python ttc_api_scraper.py", shell = True)
		# use Popen rather than run to avoid blocking
		subprocess.Popen("python ttc_api_scraper.py", shell = True)
		sleep(60)


if __name__ == "__main__":
    main()