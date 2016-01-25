#!/usr/bin/env python

import feedparser
import random

def weirdBotOutput():
	feed = feedparser.parse("http://www.simplyconfess.com/feed")
	conf = feed["entries"][random.randint(0,len(feed["entries"]) - 1)]["summary_detail"]["value"]
	conf = conf.replace("&#8217", "'").replace("&#8220","\"").replace("&#8221","\"").replace(" [&#8230;]",".. u no what?  nevermind").encode('utf8')
	return conf
