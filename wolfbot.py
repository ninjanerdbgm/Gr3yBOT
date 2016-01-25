#!/usr/bin/env python

from gr3ybot_settings import *
import httplib2
import urllib,urllib2
from pytz import timezone
import pytz
from time import strftime, sleep, localtime
import time
import datetime
import xml.etree.ElementTree as ET
import sys

if WOLFRAM_ENABLED == False:
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

def addTwoPlusTwo(q):
	answer, ans = '',''
	lines = []
	returl = 'http://www.wolframalpha.com/input/?{0}'.format(urllib.urlencode({'i':q}))
	q = urllib.urlencode({'input':q})
        url='https://api.wolframalpha.com/v2/query?{0}&appid={1}&format=plaintext'.format(q,WOLFRAM_KEY)
        lists = urllib2.urlopen(url, None)
	root = ET.fromstring(lists.read())
	for pod in root.findall('.//pod'):
		for pt in pod.findall('.//plaintext'):
			if "input" not in pod.attrib['title'].lower():
				ans = pt.text
				try:
					ans = ans.encode('utf-8','replace')
				except:
					continue
				try:
					if ans != '?^~':
						answer = answer + '{0}, '.format(ans.lower())
					else:
						answer = answer + 'complex infinity, '
				except:
					answer = ''
					pass
		if len(answer) > 2:
			lines.append('{0} - {1}'.format(pod.attrib['title'].lower(),answer[:-2]))
	return lines[:3],returl
				

