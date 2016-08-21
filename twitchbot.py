from gr3ybot_settings import *
import sys
import json
import urllib, urllib2

if __name__ == "__main__":
	print "Can't do it, Boyo.  Can't do it."
	sys.exit()

def getIsTwitchStreaming():
	url = 'https://api.twitch.tv/kraken/streams/{}'.format(twitchchan)
	rawdata = urllib.urlopen(url)
	data = json.loads(rawdata.read())
	if data["stream"] is None:
		return "No"
	else: return "Yes"
