import json
import datetime
import urllib2
import re
import ConfigParser
import zc.lockfile

def main():
    try:
        lock = zc.lockfile.LockFile('lock') # lock the script, so that another process cannot run it
        print "OKTA Events Script LOCKED " + str(datetime.datetime.now())
        config = ConfigParser.RawConfigParser()
        config.readfp(open('config.properties'))
        org = config.get("Config", "org")
        token = config.get("Config", "token")
        restRecordLimit = config.get("Config", "restRecordLimit")
        runit(org,token,restRecordLimit)
    finally:
        lock.close() # unlock this script
        print "OKTA Events Script UNLOCKED " + str(datetime.datetime.now())

def runit(org,token,restRecordLimit):
    jsonData = getDataFromEndPoint(org,token,getStartTime(),restRecordLimit)
    writeToFile(jsonData,org,token,restRecordLimit)

def getDataFromEndPoint(org,token,startTime,limit):
    # Since the Okta events cannot have a paging size greater than 1000, this
    # check is set in place to prevent that
    if(int(limit) > 1000):
        limit = '1000'

    url = 'https://' + org + '.okta.com/api/v1/logs?startDate=' + startTime + '&limit=' + limit
    headers = { 'Authorization' : 'SSWS ' + token }
    request = urllib2.Request(url, None, headers)
    response = urllib2.urlopen(request)
    return json.loads(response.read())

def getStartTime():
    timeFormat = ""
    times = [line.rstrip('\n') for line in open('startTime.properties')]
    if len(times) > 0:
        timeFormat = getFormattedTime(times[0], times[1], times[2], times[3], times[4], times[5])
    if len(times) == 0:
        offsetTime = getOffsetStartTime()
        timeFormat = getFormattedTime(offsetTime.strftime('%Y'), offsetTime.strftime('%m'), offsetTime.strftime('%d'), offsetTime.strftime('%H'), offsetTime.strftime('%M'), offsetTime.strftime('%S'))
    return timeFormat

def getFormattedTime(year, month, day, hour, minute, second):
    return year + "-" + month + "-" + day + "T" + hour + ":" + minute + ":" + second + ".000Z"

def writeOffsetTimeToFile(year, month, day, hour, minute, seconds):
    f = open("startTime.properties",'w+')
    f.write(year + '\n')
    f.write(month + '\n')
    f.write(day + '\n')
    f.write(hour + '\n')
    f.write(minute + '\n')
    f.write(seconds + '\n')
    f.close()

def getOffsetStartTime():
    now = datetime.datetime.now();
    offsetTime = now + datetime.timedelta(0,5) # days, seconds, then other fields.
    return offsetTime

def writeToFile(jsonData,org,token,restRecordLimit):
    numberOfRows = 0;
    lastWrittenPublishedTime = "";
    fileName = "output-" + str(datetime.datetime.date(datetime.datetime.now())) + ".log"
    eventLogFile = open(fileName, 'a')

    # this will loop through each of the objects in the JSON list
    for stuff in jsonData:
        lastWrittenPublishedTime = stuff['published']
        eventLogFile.write("Published Time: " + lastWrittenPublishedTime + "\n")
        json.dump(stuff,eventLogFile)
        eventLogFile.write("\n")

    match = re.match("(\d{1,4})-(\d{1,2})-(\d{1,2})T(\d{1,2}):(\d{1,2}):(\d{1,2})", lastWrittenPublishedTime)
    writeOffsetTimeToFile(match.group(1), match.group(2), match.group(3), match.group(4), match.group(5), match.group(6))

    # Call the endpoint again if the data returned exceeds the limit returned
    if(numberOfRows > int(restRecordLimit) - 1):
        runit(org,token,restRecordLimit)

# start this off
main()
