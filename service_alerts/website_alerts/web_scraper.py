import requests
import re
import psycopg2
from bs4 import BeautifulSoup
from datetime import datetime
import calendar
import configparser
import threading #used to call the api over and over again

now = datetime.now()

CONFIG = configparser.ConfigParser(interpolation=None)
CONFIG.read('db.cfg')
dbset = CONFIG['DBSETTINGS']

conn = psycopg2.connect(**dbset)
#conn = psycopg2.connect(host='localhost', dbname='service_alerts', user='postgres', port=5432)
conn.set_session(autocommit=True)
cur = conn.cursor()

last_time = 0
last_pushed = 0

url = "https://ttc.ca/Service_Advisories/all_service_alerts.jsp"
def call_api():
    global last_time
    global last_pushed
    threading.Timer(60.0, call_api).start()
    html_doc = requests.get(url, timeout = 10)

    alerts = []
    soup = BeautifulSoup(html_doc.text, 'html.parser')
    for tag in soup.find_all('div',{"class": "alert-content"}):
        alerts.append(tag.text)

    alerts = alerts[:-1]

    len_arr = len(alerts)
    for alert in alerts:
        split = alert.split('Last updated ')
        time = split[1]
        #dt = datetime.strptime("02:31:33 PM", "%I:%M:%S %p")
        #print(int(dt.timestamp()))
        #print(last_time)
        #print(split)
        timestamp = 0
        if time[0].isdigit():
            dt = datetime.strptime(str(now.month)+ " "+str(now.day)+" "+ str(now.year)+" "+time,"%m %d %Y %I:%M %p")
            timestamp = int(dt.timestamp())
        else:
            #May 30, 5:41 AM
            year = str(now.year)
            if str(now.month) == "1" and time.split(" ")[0] == "December":
                year = str(int(year)-1)
            dt = datetime.strptime(year+" "+time,"%Y %B %d, %I:%M %p")
            timestamp = int(dt.timestamp())
        if timestamp == last_time: #this means that the either the alerts didn't update or that we've looped through all of the alerts and have found one that we've already put in
            break

        issue = split[0]
        atype = ""
        if "REMINDER" in issue:
            atype = "re"
        elif "ALL CLEAR" in issue:
            atype = "ac"
        elif "No subway service" in issue:
            atype = "nss"
        elif "No train service" in issue:
            atype = "nts"
        elif "Elevator Alert" in issue:
            atype = "ea"
        elif "Travelling from" in issue:
            atype = "tf"
        elif "Travelling to" in issue:
            atype = "tt"
        elif "Trains are holding on" in issue:
            atype = "tho"
        else:
            atype = "o"
        cur.execute('INSERT INTO service_alerts_tb (a_type, a_time, a_text) VALUES (%s,%s,%s)',(atype, timestamp, issue))
        print(timestamp)
        last_pushed = timestamp
    last_time = last_pushed
call_api()
