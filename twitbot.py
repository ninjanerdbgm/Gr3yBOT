#!/usr/bin/env python

from gr3ybot_settings import TWIT_CONSUMER_KEY,TWIT_CONSUMER_SECRET,TWIT_ACCESS_KEY,TWIT_ACCESS_SECRET
from gr3ysql import Gr3ySQL
import time
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

sql = Gr3ySQL()

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

def getTweetFromID(idnum=None):
	try:
		if idnum is None:
			return False
		else:
			twt = twit.get_status(id=idnum)
			usr = twt.user.screen_name
			twt = twt.text
		return usr,twt
	except tweepy.error.TweepError as e:
		if e.message == "Not Authorized":
			return "~*501"
		try:
			if e.message[0]['code'] == 34:
				return "~*404"
		except TypeError:
			return "~*501"

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
		q = sql.db.cursor()
		q.execute("""
			SELECT id FROM TwitterIDs WHERE id = ? """, (int(i["id"]),))
		tid = q.fetchone()
		try:
			ids.remove(tid[0])
		except:
			for i in ids:
				q.execute("""
					INSERT INTO TwitterIDs (id, dateTime) VALUES (?, ?) """, (i, time.time()))
			sql.db.commit()
	if len(ids) > 0: return ids
	else: return False
