#!/usr/bin/env python

from gr3ybot_settings import TWIT_CONSUMER_KEY,TWIT_CONSUMER_SECRET,TWIT_ACCESS_KEY,TWIT_ACCESS_SECRET
import tweepy
from tweepy import OAuthHandler
import sys
import json
import random

#-- SETUP STUFF
if __name__ == '__main__':
	print "This can't be run on its own!"
	sys.exit()

auth = OAuthHandler(TWIT_CONSUMER_KEY,TWIT_CONSUMER_SECRET)
auth.set_access_token(TWIT_ACCESS_KEY,TWIT_ACCESS_SECRET)

twit = tweepy.API(auth)
twot = tweepy.API(auth, parser=tweepy.parsers.JSONParser())
#--

def getRateLimit():
	return twit.rate_limit_status()

def getRandomFollower():
	c = tweepy.Cursor(twit.followers).items()
	users = []
	try:
		fol = c
        except tweepy.error.TweepError as e:
		return None
	for usr in fol:
		users.append(usr.screen_name)
	name = users[random.randint(0,len(users) - 1)]
        return "gr3ynoise" if name == None else name

def followAll():
	try:
		for follower in tweepy.Cursor(twit.followers).items():
			follower.follow()
	except tweepy.error.TweepError as e:
		if e.message[0]['code'] == 88:
			return None
	return None

def getTweet(user, checkids=None):
	try:
		if user != 0:
			twt = twit.user_timeline(screen_name=user, count=1)
		if checkids is not None:
			twt = twit.get_status(id=checkids)
		return twt
	except tweepy.error.TweepError as e:
		if e.message == "Not Authorized":
                        return "-*501"
		try: 
			if e.message[0]['code'] == 34:
				return "-*404"
		except TypeError:
			return "-*501"

def getTweetTest(user, checkids=None):
        try:
                if user != 0:
                        twt = twit.user_timeline(screen_name=user, count=500)
                if checkids is not None:
                        twt = twit.get_status(id=checkids)
                return twt
        except tweepy.error.TweepError as e:
                if e.message == "Not Authorized":
                        return "-*501"
                try:
                        if e.message[0]['code'] == 34:
                                return "-*404"
                except TypeError:
                        return "-*501"

def postTweet(msg):
	try:
		twit.update_status(status=msg)
	except tweepy.error.TweepError as e:
		if e.message[0]["code"] == 137:
			return "DUPLICATE"
	return 0

def isTweetedAt(bn):
	ids = []
	twt = twot.search(q=bn)
	for i in twt["statuses"]:
		if i["retweeted"]: continue
		ids.append(i["id"])
		with open('twitids','r') as f:
			lines = f.readlines()
			f.seek(0)
			for line in lines:
				theline = line.strip('\r').strip('\n')
				if int(theline) == int(i["id"]):
					ids.remove(i["id"])
					break
			f.close()
	f = open('twitids','a')
	for i in ids:	
		f.write("{0}\n".format(i))
	f.truncate()
	f.close()
	if len(ids) > 0: return ids
	else: return False
