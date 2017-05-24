# service_alerts

A large part of improving subway efficiency is distinguishing the difference from poor scheduling to errors caused by delays.

The goal for this folder is to generate an archive of service delays to explain anomalies in our main dataset.

# Twitter

The twitter scraper will pull tweets from the TTC's service announcement page (https://twitter.com/TTCnotices) and compile delay data into a database.

 - Offers detailed delayed data (includes information on elevator maintenance and all clears)

#website_alerts

The scraper will download official service delays from the city of Toronto's website (https://ttc.ca/Service_Advisories/all_service_alerts.jsp) by scraping away all of the HTML and retrieving the specific delays.

 - Offers concise information about major delays
