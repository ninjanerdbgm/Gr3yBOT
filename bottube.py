#!/usr/bin/env python

from gr3ybot_settings import *
from apiclient.discovery import build
import urllib
import urllib2
from pytz import timezone
import pytz
from time import strftime, sleep, localtime
import time
import datetime
import json
import sys

if YOUTUBE_LINKS == False:
	sys.exit()

if __name__ == "__main__":
	print "You can't run this on its own!"
	sys.exit()

#-- Logging...
timeformat = "%m/%d/%y %H:%M:%S"
def log(text):
        localnow = datetime.datetime.now(timezone(LOCALTZ))
        with open(LOGFILE, 'a+') as f:
                f.write("{0} --==-- {1}\r\n".format(strftime(timeformat),text))
        f.close()
#--

youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,developerKey=YOUTUBE_DEVELOPER_KEY)

# Call the search.list method to retrieve results matching the specified
# query term.
def getVideo(term):
	results = []
	search_response = youtube.search().list(
	q=term,
	part="id,snippet"
	).execute()

# Add each result to the appropriate list, and then display the lists of
# matching videos, channels, and playlists.
	for search_result in search_response.get("items", []):
		if search_result["id"]["kind"] == "youtube#video":
			if VERBOSE: log("Found a YouTube video matching ID: {0} (URL: https://www.youtube.com/watch?v={0})".format(term))
			results.append("{0}".format(search_result["snippet"]["title"].encode('utf-8')))
			break
	url='https://www.googleapis.com/youtube/v3/videos?id={0}&part=contentDetails&key={1}'.format(term,YOUTUBE_DEVELOPER_KEY)
	lists = urllib2.urlopen(url, None)
	page = json.loads(lists.read())
	duration = page["items"][0]
	duration = duration["contentDetails"]["duration"]
	duration = duration.replace('PT','')
	hoursnominutes = False
	# Here's where we do some formatting magic to get the length...
	if 'H' in duration and 'M' not in duration: hoursnominutes = True
	if 'H' not in duration: duration = "00:{0}".format(duration)
	else: duration = duration.replace('H',':')
	if 'M' not in duration and not hoursnominutes: duration = "00:{0}".format(duration)
	elif 'M' not in duration and hoursnominutes: duration = duration.replace(":",":00:")
	else: duration = duration.replace('M',':')
	if 'S' not in duration: duration = "{0}00".format(duration)
	else: duration = duration.replace('S','')
	duration = duration.split(':')
	if int(duration[0]) < 10 and duration[0] != '00': duration[0] = "0{0}".format(duration[0])
	if int(duration[1]) < 10 and duration[1] != '00': duration[1] = "0{0}".format(duration[1])
	if int(duration[2]) < 10 and duration[2] != '00': duration[2] = "0{0}".format(duration[2])
	duration = ":".join(duration)
	results.append(duration)
	if VERBOSE: log("Video Info --==-- Title: {0}, Length: {1}".format(results[0],results[1]))
	return results
