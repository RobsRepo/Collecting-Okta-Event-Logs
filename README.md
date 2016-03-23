#Collecting Okta Event Logs for Log Aggregation Tools

This Python script will pull Okta logs into a format that is easily parsable by log aggregation tools such as SumoLogic and Splunk. Run it using a cron job or some kind of scheduler. With Sumo Logic you can run this as a script source.

##Key Points About this Script
- This script will produce a file called "output-<current date>.log".
- It will bring back at most 1000 entries on each outbound call. 
- It will continue to call until there aren't anymore event logs to pull.
- There is a system lock on this script when it is initially started to prevent another process from running this script more than once.
 
# Prerequisites
-	You will need Python 2.7
-	You will need the "zc.lockfile" library. Install it using “pip install zc.lockfile”

# Setup
1. Install the prerequisites.
2. Add the necessary Okta configuration information inside config.properties.
3. You can omit the contents for "startime.properties". However, if you would like to have this script start collecting events before the current time, you will need to add the following line by line:
 * YEAR
 * MONTH
 * Day
 * Hour
 * Minute
 * Second
 
# Run:
To run this on its own: "python oktaEvents.py"
