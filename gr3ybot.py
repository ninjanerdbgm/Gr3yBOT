#!/usr/bin/env python

#--
# Gr3yBOT by BGM, 05/27/2015
# https://greynoi.se
#
#	What started as a small bot aimed for no more than just printing
#	out the latest episode info in chat turned in to something much,
#	much more.  At the time of this writing, it supports:
#		
#		- Wikipedia searching
#		- Meal suggestions powered by Yelp
#		- Urban Dictionary definitions
#		- A full-fledged RPG fighting system
#		- CleverBot integration
#		- A memos system to relay a message to another user
#		- Unobtrusive and entertaining idle chat.
#		- Twitter Integration, including:
#			- Being able to send tweets as the bot.
#			- The bot auto-follows its followers.
#			- The bot randomly reads a follower's latest tweet in chat.
#			- You can get any twitter user's latest tweet in chat.
#			- The bot responds to tweets @ it on Twitter
#			- The bot automatically displays tweets @ it in chat too.
#		- Channel op commands, if user's in the admin file:
#			- Op a user
#			- Change the topic
#		And of course,
#		- Displays latest GR3YNOISE podcast info
#		- Displays the upcoming events at SynShop Las Vegas
#--

#
from gr3ybot_settings import *
from chatterbotapi import ChatterBotFactory, ChatterBotType
import struct
from bottube import *
import socket
import string
from urbandict import *
import sys
from twitbot import *
from slackbot import *
from yelpbot import *
from weatherbot import *
from os import path
import random
import signal
import parsedatetime as pdt
from time import sleep, strftime, localtime
import threading
import urllib
import urllib2
import json
from pytz import timezone
import pytz
from wiki import wiki
import datetime
import re
from fightbot import *

#-- Version, and AI initialization, and variables
version = "1.0. Version Name: Unassuming Local Guy"
random.seed()

AI = ChatterBotFactory()
botAI = AI.create(ChatterBotType.CLEVERBOT)
convo = botAI.create_session()

andcount = 0 #for gimli
stopfight = 0 #for fight
lastMessage = "Hi" #for idle chat
lastPerson = "-*404" #for idle chat, too
lastTime = time.time() #for idle chat, too, too
tellinghistory = 0 #for flood protection
defchannel = channel

if fightchan == channel or fightchan is None or fightchan == '':
	fightchan = channel

#-- Clear the log, if there is one.  If there isn't one, create one
f = open(LOGFILE, 'w+')
f.close()
#--

#-- Set botname match string and connect to IRC
matchbot = botname.lower()

irc = socket.socket ( socket.AF_INET, socket.SOCK_STREAM )
irc.connect((server,port))
irc.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER, struct.pack('ii', 1, 0))
print irc.recv(512)
irc.send ( 'PASS {0} \r\n'.format(password) )
irc.send ( 'NICK {0}\r\n'.format(botname) )
irc.send ( 'USER {0} {1} {2} :Python-powered IRC bot to help moderate #gr3ynoise\r\n'.format(botname,botname,botname) )
irc.send ( 'JOIN {0}\r\n'.format(channel))
if len(fightchan) > 0:
	irc.send ( 'JOIN {0}\r\n'.format(fightchan))
#--

#-- Send a message upon joining the channel
irc.send ( 'PRIVMSG {0} :hey type %help if youre dumn\r\n'.format(channel))
if fightchan != defchannel: irc.send ( 'PRIVMSG {0} :llllllets get ready to rumbleeeee orrrr read %fight help if you dont know what im talking abouuuuuuuuuuut\r\n'.format(fightchan))
#--

#-- Functions
def log(text):
	localnow = datetime.datetime.now(timezone(LOCALTZ))
	with open(LOGFILE, 'a+') as g:
		g.write("{0} --==-- {1}\r\n".format(localnow.strftime(timeformat),text))
		if ECHO_LOG: print "{0} --==-- {1}".format(localnow.strftime(timeformat),text)
	g.close()

def admins(host):
	synackers = open('admins', 'r')
	for line in synackers:
		if VERBOSE: log("Host/Line: {0}/{1}".format(host,line))
		if host in line:
			return 1
		else:
			status = 0
	return status

def getHost(host):
	host = host.split('!')[1]
	host = host.split(' ')[0]
	return host

def getChannel(data):
	chan = data.split('#')[1]
	chan = chan.split(':')[0]
	chan = '#' + chan
	chan = chan.strip(' \t\n\r')
	return chan

def getNick(data):
	nick = data.split('!')[0]
	nick = nick.replace(':', '')
	nick = nick.strip(' \t\n\r')
	return nick

def getChatters():
	data = irc.recv(2048)
	if VERBOSE: log("Call for list of names in {0}".format(channel))
	if '353' in data:
		names = data.split('353')[1]
		names = names.split(':')[1]
		names = names.split(' ')
		names = [i.strip('@').strip('\r\n') for i in names]
		try:
			names.remove(botname)
		except ValueError: names = names
		if VERBOSE:
			log("People in the channel:")
			for i in names:
				log(i)
	else: names = False
	return names

def getRandomPerson():
	names = getChatters()
	if not names: return False
	if creepfactor == 2 and creepperson in names: person = creepperson
	else: person = names[random.randint(0,len(names) - 1)]
	return person

def getMessage(data):
	try:
		msg = data.split('#')[1]
	except IndexError:
		msg = None

	if msg is not None:
		msg = msg.split(':')[1:]
		msg = " ".join(msg)
	return msg

def matchYouTube(msg):
	yt = (
	r'(https?://)?(www\.)?'
        '(youtube|youtu|youtube-nocookie)\.(com|be)/'
        '(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})')

	matchit = re.match(yt, msg)
	if matchit: return True
	return False

def join():
	irc.send('JOIN ' + channel + '\r\n')
	if fightchan != defchannel: irc.send('JOIN ' + fightchan + '\r\n')

def send(msg):
	irc.send('PRIVMSG ' + channel + ' :{0}\r\n'.format(msg))

def fightsend(msg):
	irc.send('PRIVMSG ' + fightchan + ' :{0}\r\n'.format(msg))

def sendraw(msg):
	irc.send((msg + '\n').encode('utf-8'))

def notify(name,msg):
	irc.send('NOTICE ' + name + ' :{0}\r\n'.format(msg))

def privsend(msg, nick):
	irc.send('PRIVMSG ' + nick + ' :{0}\r\n'.format(msg))

def op(opuser):
	if isinstance(opuser, list):
		for i in opuser:
			irc.send('MODE {0} +o {1}\r\n'.format(channel,i.strip('\r\n')))
	else:
		irc.send('MODE {0} +o {1}\r\n'.format(channel,opuser))

def deop(opuser):
	if isinstance(opuser, list):
		for i in opuser:
			irc.send('MODE {0} -o {1}\r\n'.format(channel,i.strip('\r\n')))
	else:
		irc.send('MODE {0} -o {1}\r\n'.format(channel,opuser))

def kick(user, reason):
	irc.send('KICK ' + channel + ' ' + user + ' :{0}'.format(reason))

def jsontitle(data):
	title = data.split('title":"')
	title = title[1].split('",')
	title = title[0]
	return title

def jsonurl(data):
	url = data.split('":"')
	url = url[1].split('",')
	url = url[0]
	return "http://www.greynoi.se/podcasts/{0}".format(url)

def jsondesc(data):
	desc = data.split('html":"')
	desc = desc[1].replace('\r\n',' ')
	desc = desc.split('Related Links')
	desc = desc[0]
	desc = desc.replace('\\r\\n\\r\\n','  ')
	return desc

def rline(f):
	line = next(f)
	for n, randline in enumerate(f):
		if random.randrange(n+2): continue
		line = randline
	return line

def checkTwits():
	 #--
         # Let's check to see if someone tweeted at the bot every so often.
         # If so, post the message in chat.
         #--
        if VERBOSE: log("Checking for tweets @ the bot...")
        try:
		twts = isTweetedAt(twittername)
	#
	#
	# The following section is commented out because it suddenly stopped working.
	# Fix it, bgm
	#
	#
	#except tweepy.TweepError as e:
	#	if e.message[0]["code"] == 130:	
	#		if VERBOSE: log("Twitter has reached a bandwidth limit and kicked back no response.")
	#	return False
	except:
		log("Something went wrong...")
		return False
	try:
		if twts != False:
			if len(twts) > 0:
				j = 0
			      	send("ive got some new tweets @ me...")
			        if VERBOSE: log("Someone tweeted at {0}!".format(botname))
			        for msg in enumerate(twts):
			              	mag = getTweet(0,checkids=msg[1])
				        send("@{0} >> {1}".format(mag.user.screen_name,mag.text.encode('utf-8')))
			                if VERBOSE: log("@{0} >> {1}".format(mag.user.screen_name,mag.text.encode('utf-8')))
					q = convo.think(mag.text.encode('utf-8')); # Trigger a cleverbot response
                                        q = q.lower()
                                        q = "".join(c for c in q if c not in ('\'','"','!',':',';'))
					q = "@{0} {1}".format(mag.user.screen_name,q)
					if "@{}".format(mag.user.screen_name) != "{}".format(twittername):
						send("i think ill reply with: {0}".format(q))
						try:
							postTweet(q)
						except:
							pass
					else:
						send("making me talk to myself. clever.")
			else: 
				if VERBOSE: log("None found!")
		else: 
			if VERBOSE: log("None found!")
	except TypeError:
	       	if VERBOSE: log("None found!")
			
def checkReminders():
	#--
	# Check the reminders file to see if anyone needs to be reminded
	# of anything...
	#--
	with open('reminders','r+') as f:
		lines = f.readlines()
		f.seek(0)
		for line in lines:
			thisline = line.split('[-]')
			if float(thisline[1]) < time.time():
				send("hey {0}, heres a reminder for you: {1}".format(thisline[0],thisline[2]))
				privsend("hey {0}, heres a reminder for you: {1}".format(thisline[0],thisline[2]),thisline[0])
				sendPing("SynackBOT","{}".format(thisline[0]),"heres your reminder: {0}".format(thisline[2]))
				g = open('memos', 'a')
				g.write("SynackBOT[-]{0}[-]dont forget: {1}".format(thisline[0],thisline[2]))
				g.close()
				if VERBOSE: log("Sent a reminder to {0}!".format(thisline[0]))
			else:
				f.write(line)
		f.truncate()
		f.close()
	#--

#-- Main Function
def main(joined):
	while True:
		special = 0
		action = 'none'
		data = irc.recv(4096)
		if len(data) == 0:
			break
	
		if CHATLOG: log(data)

		# OLD
		#if data.find(server_slug) != -1:
		#	join()
	
		try:
			if data.find('PING') != -1:
	                        #--
	                        # Since IRC servers send out a PING message at fixed intervals, I use it for timed functions.
				#
				# Reset the fight history flood protection...
				tellinghistory = 0
	                        #
	                        # Check to see if anyone tweeted at the bot...
	                        if TWITTER_ENABLED: checkTwits()
				#checkReminders()
	                        # Have a 30% chance to shift the XOR bits in the fightbot RNG (this is to try to make it more random)
	                        if (random.randint(1,99193) * int(time.time())) % 100 < 30:
	                                shift = xOrShift()
	                                if VERBOSE: log("XOR bits shifted to: {0}".format(shift))
	                        #
	                        # And finally, return the PONG message to keep the bot alive.
	                        irc.send('PONG ' + data.split()[1] + '\r\n')
		except UnicodeDecodeError:
                        continue
	
		if data.find('#') != -1:
			action = data.split('#')[0]
			action = action.split(' ')[1]

		if data.find('PRIVMSG {0} :%'.format(botname)) != -1:
			action = 'PRIVMSG'
			special = 1
	
		if data.find('NICK') != -1:
			if data.find('#') == -1:
				action = 'NICK'
	
		if action != 'none':
			sender = getNick(data)
			if action == 'JOIN': joined = 1
			if action == 'PRIVMSG':
				if getChannel(data) == fightchan:
					channel = fightchan
				else:
					channel = defchannel
				if data.find('%') != -1: # Change the % here to be ! or whatever you want the command trigger to be
					x = data.split(':',2)[2:] # let's make sure to get all the text
					x = " ".join(x)
					x = x.split('%',1)[1:] # Do the same as before, but with any other commands later on in the line
					x = " ".join(x)
					info = x.split(' ') # Now let's turn it back into a list
					info[0] = info[0].strip(' \t\n\r')
					info[0] = ''.join(c for c in info[0] if c not in ('.',',','!','?',':','"','\''))
					#--
					# Separate fights from normal stuff
					#
					if channel == fightchan and info[0].lower() != 'fight':
						fightsend("sorry bud, i only do fights here.  if you want the other stuff, /join {0}".format(defchannel))
						continue
					#--
					if VERBOSE: log("Command found: %{0}".format(info[0]))

					#--
					# info[0] gets set to whatever the first thing after % is in chat.
					# info[1:] refers to all other text after it.
					#--
					
					#--
					# OPER COMMAND
					if info[0].lower() == 'op':
						host = getHost(data)
						status = admins(host)
						if status == 1:
							try:
								op(info[1:])
								if VERBOSE: log("Opped {0}".format(info[1:]))
							except TypeError:
								send("who do you wanna op, dumb dumn")
								continue
						else:
							send("you dont know what youre talking about")
							continue
					#--

					#--
                                        # DEOP COMMAND
                                        if info[0].lower() == 'deop':
						host = getHost(data)
						status = admins(host)
						if status == 1:
		                                        try:
	        	                                        deop(info[1:])
	                                                        if VERBOSE: log("Deopped {0}".format(info[1:]))
	                                                except TypeError:
	                                                        send("who do you wanna deop, dumb dumn")
	                                                        continue
						else:
							send("you dont know what youre talking about")
							continue
                                        #--

					# TOPIC COMMAND
					if info[0].lower() == 'topic':
						host = getHost(data)
						status = admins(host)
						if status == 1:
							try:
								topic = info[1:]
								topic = " ".join(topic)
								topic = topic.replace('http //','http://')
								topic = topic.strip('\t\r\n')
								send("the new topic is butts.  discuss, everyone.")
								time.sleep(2)
								irc.send("TOPIC {0} :{1}\n".format(channel,topic))
								if VERBOSE: log("Topic changed to: {0}".format(topic))
							except:
								sendraw("TOPIC {0}".format(channel))
								topic = irc.recv(2056)
								topic.split("{0}: ".format(channel))
								send(topic[1])
				
					# VERSION COMMAND
					if info[0].lower() == 'version':
						if special == 0: send("Gr3yBOT by bgm: version {0}. You know you wanna fork me: https://github.com/ninjanerdbgm/Gr3yBOT".format(version))
						else: name = getNick(data); privsend("Gr3yBOT by bgm: version {0}. You know you wanna fork me: https://github.com/ninjanerdbgm/Gr3yBOT".format(version),name)
						if VERBOSE: log("Version: {0}".format(version))
			
					# SYNSHOP COMMAND
					if info[0].lower() == 'synshop':
						nick = getNick(data)
						try:
							end = info[1]
						except IndexError:
							end = 3 # Did the user specify a numer?  If not, set it to 3 by default.
						try:
							end = int(round(float(end))) # Make sure that they specified a number, and not anything else
						except IndexError:
							end = 3 # If it wasn't a number, let's set it to the default
						except ValueError:
							end = 3 # Same as above
						if VERBOSE: log("The next {0} events at SynShop:".format(end))
						if special == 0: send("geez fine, check your pms")
						time.sleep(1.5)
						#--  I broke up the URL into five lines here for formatting reasons only
						meetupurl = 'https://api.meetup.com/2/events'
						meetupmsc = 'format=json&limited_events=False&group_urlname=synshop&photo-host=public&page=20'
						meetupsigid = 186985877
						meetupsig = 'a57dac5ef9c747785636bb4038cc921b94926c9e'
						html = urllib2.urlopen('{0}?offset=0&{1}&fields=&order=time&desc=false&status=upcoming&sig_id={2}&sig={3}'.format(meetupurl,meetupmsc,meetupsigid,meetupsig))
						#--
						getjson = json.load(html)
						i = 0
						if end and end > 3: end = 3
						privsend("next {0} synshop events (small flood inbound):".format(end), nick)
						while i < end:
							name = getjson["results"][i]["name"]
							name = name.encode('utf-8').lower()
							desc = getjson["results"][i]["description"]
							desc = desc.strip('\\')
							desc = re.sub('<[^>]*', '', desc)
							desc = desc.encode('utf-8').lower()
							gettime = getjson["results"][i]["time"]
							gettime = datetime.datetime.fromtimestamp(gettime / 1e3)
							url = getjson["results"][i]["event_url"]
							URl = url.strip('\\')
							privsend("{0} - {1}".format(name,desc), nick)
							privsend("when: {0}".format(gettime.strftime("%A, %B %d %Y")), nick)
							privsend("more info: {0}".format(url), nick)
							if VERBOSE: log("Sent the following info to {0}:\n{1} - {2}\nWhen: {3}\nMore Info: {4}".format(nick, name, desc, gettime.strftime("%A, %B %d %Y"), url))
							time.sleep(2)
							i = i + 1
						privsend("visit synshop: 117 n 4th st, las vegas, nv 89101", nick)
						privsend("-- done, ok thx bai --", nick)					
	
					# BREAKFAST, BRUNCH, LUNCH, DINNER COMMANDS	
					if any(info[0].lower() in s for s in yelp_keywords) and YELP_ENABLED:
						try:
							loc = info[1:]
						except IndexError:
							loc = DEFAULT_LOC

						loc = "".join(loc)
						loc = loc.replace(' in ','')
						if len(loc) < 5: loc = DEFAULT_LOC

						terms = {
							'term': info[0].lower(),
							'location': loc.replace(' ','+'),
							'limit': SEARCH_LIMIT
						}

						query = getFood(terms)
						name = []
						url = []
						rating = []
						reviews = []
						try:
							for i in query["businesses"]:
								name.append(i["name"])
								url.append(i["url"])
								rating.append(i["rating_img_url"])
								reviews.append(i["review_count"])
						except TypeError:
							if special == 0: send("what?  did a cat walk all over your keyboard just now?")
							else: usernick = getNick(data); privsend("what?  did a cat walk all over your keyboard just now?", usernick)
							continue
						randresult = random.randint(0,len(name)-1)
						name = name[randresult].encode('utf-8').lower()
						url = url[randresult].encode('utf-8').lower()
						reviews = reviews[randresult]
						#--
						# Guess what?  Yelp doesn't return the rating in a json string for
						# some reason. They do, however, return a png with a name that
						# indicates how many stars the restaurant got.  Let's parse
						# the name of this png file and see if we can turn that into an
						# IRC-friendly text string...
						#--
						rating = rating[randresult][-10:].encode('utf-8').lower()
						rating = rating.replace('.png','')
						rating = rating.replace('tars','')
						rating = rating.replace('_','')
						rating = rating.replace('half','.5')
						if VERBOSE: log("Suggesting: {0} ({1} stars from {2} reviews).  URL: {3}".format(name,rating,reviews,url))
						if special == 0: send("maybe you should try {0}? ({1} stars from {2} reviews). more info: {3}".format(name,rating,reviews,url))
						else: usernick = getNick(data); privsend("maybe you should try {0}? ({1} stars from {2} reviews). more info: {3}".format(name,rating,reviews,url),usernick)

					# URBAN DICTIONARY			
					if info[0].lower() == 'define' and URBANDICT_ENABLED:
						try:
							mean = info[1:]
						except IndexError:
							if special == 0: send("i dont kno how to define nothing, guy")
							else: usernick = getNick(data); privsend("what",usernick)
							continue
						word = " ".join(mean)
						word = "".join(c for c in word if c not in ('\n','\r','\t')) # Rebuild the string letter by letter to strip out certain things.  You'll see this a lot in this script
						if VERBOSE: log("Define {0}:".format(word))
						meaning, example, url = getWord(word)
						if meaning is None:
							if special == 0: send("that doesnt seem to be a thing.")
							else: usernick = getNick(data); privsend("that doesnt seem to be a thing",usernick)
							if VERBOSE: log("Nothing Found.")
							continue
						meaning = "".join(c for c in meaning if c not in ('\n','\r','\t'))
						example = "".join(c for c in example if c not in ('\n','\r','\t'))
						if special == 0:
							send("first thing i could find:")
							send("{0} - {1}".format(word, meaning))
							send("example: {0}".format(example))
							send("this is where you can get more definitions: {0}".format(url))					
						else:
							name = getNick(data)
							privsend("first thing i could find:",name)
                                                        privsend("{0} - {1}".format(word, meaning),name)
                                                        privsend("example: {0}".format(example),name)
                                                        privsend("this is where you can get more definitions: {0}".format(url),name)
						if VERBOSE: log("{0} - {1}\nExample: {2}\nMore Info: {3}".format(word,meaning,example,url))

					# WEATHER
                                        if info[0].lower() == 'weather':
                                                degrees = " F"
                                                try:
                                                        where = info[1:]
                                                except IndexError:
                                                        if special == 0: send("the weather of space is cold and dark")
                                                        else: usernick = getNick(data); privsend("the weather of space is cold and dark",usernick)
                                                        continue
                                                where = " ".join(where)
                                                where = "".join(c for c in where if c not in ('\n','\r','\t'))
                                                if VERBOSE: log("Get weather for {0}".format(where))
                                                weather = getWeather(where)
                                                if weather == "~*404" or weather is None:
                                                        if special == 0: send("i dont know where dat iz")
                                                        else: usernick = getNick(data); privsend("i dont know where dat iz",usernick)
                                                        if VERBOSE: log("Nothing found.")
                                                        continue
                                                if special == 0:
                                                        send("weather for {0}:".format(weather['location']))
                                                        send("currently {0} at {1}{2} (feels like {6}{2}). visibility is at {5} miles. humidity is currently {3}%, with an atmospheric pressure of {4}psi".format(weather['cloudcover'],weather['temp'],degrees,weather['humidity'],weather['pressure'],weather['visibility'],weather['windchill']))
                                                        send("wind is blowing {0} at {1}mph. sunrise today is at {2} and sunset is at {3}".format(weather['winddirection'],weather['windspeed'],weather['sunrise'],weather['sunset']))
		
					# PODCAST INFO
					if any(info[0].lower() in s for s in podcast_keywords):
						if special == 0: send("ok one sec...")
						else: usernick = getNick(data); privsend("one sec",usernick)
						time.sleep(1.5)
						html = urllib2.urlopen('http://www.greynoi.se/feeds/json')
						getjson = html.read()
						if special == 0:
							send("latest episode: {0}".format(jsontitle(getjson)))
							time.sleep(1.5)
							send("description: {0}".format(jsondesc(getjson).replace("\\\"","\"")))
							time.sleep(1.5)
							send("more info: {0}".format(jsonurl(getjson)))
							time.sleep(1.5)
							send("ok im done now thx")
						else:
							name = getNick(data)
							privsend("latest episode: {0}".format(jsontitle(getjson)),name)
                                                        time.sleep(1.5)
                                                        privsend("description: {0}".format(jsondesc(getjson)),name)
                                                        time.sleep(1.5)
                                                        privsend("more info: {0}".format(jsonurl(getjson)),name)
                                                        time.sleep(1.5)
                                                        privsend("ok im done now thx",name)
						if VERBOSE: log("Episode: {0}\nDescription: {1}\nURL: {2}".format(jsontitle(getjson),jsondesc(getjson),jsonurl(getjson)))
	
					# HELP
					if any(info[0].lower() in s for s in help_keywords):
						name = getNick(data)
						if len(info) == 1:
							if special == 0: send("geez are you slow or something god.  check your pms")
							privsend("%op <user> -=- allows you to op the specified <user>. only works if youre a podcaster.", name)
							time.sleep(.5)
							privsend("%topic <topic> -=- allows you to change the <topic>.  only works if youre a podcaster.", name)
							time.sleep(.5)
							privsend("%tell <nick> <message> -=- stores a <message> for <nick> and sends it to them when they become active again.", name)
							if PING_ENABLED: privsend("%ping <nick> <message> -=- send a message to <nick> via slacker.  this should ping their phone.  message is optional.  want to be able to be pinged? type %help ping", name)
							privsend("%remindme <timeframe> - <message> -=- remind yourself to do something in the future. %help reminders for more info", name)
							time.sleep(.5)
							if TWITTER_ENABLED: privsend("%tweet <message> -=- make synackbot send a tweet containing <message>.", name)
							if TWITTER_ENABLED: privsend("%twit <user> -=- <user> is optional.  retrieves the last tweet from <user> or from a random follower", name)
							time.sleep(.5)
							if YELP_ENABLED: 
								privsend("%breakfast/%brunch/%lunch/%dinner <location> -=- gives you a random restaurant suggestion for the provided location.",name)
								privsend("  ===  ==  = <location> is optional (default is las vegas), and can be a city, state or a zip code.",name)
							if WIKIPEDIA_ENABLED: privsend("%wiki/%wikipedia/%lookup/%search <string> -=- search wikipedia for <string> and return a quick summary.", name)
							if URBANDICT_ENABLED: privsend("%define <word(s)> -=- define stuff from urbandictionary.", name)
							privsend("%weather <location> -=- get the weather forecast for <location>", name)
							privsend(" ", name)
							time.sleep(.5)
							privsend("%info -=- displays the latest podcast info", name)
							time.sleep(.5)
							privsend("%synshop <num> -=- displays the next <num> upcoming events at synshop.  the <num> parameter is optional, but it cant go over 3.", name)
							time.sleep(.5)
							privsend(" ", name)
							privsend("%overlord -=- display a random 'if i were an evil overlord,' quote.", name)
							privsend("%fight -=- play the fighting game against another chatter.",name)
							privsend("== NOTE! %fight by itself wont do anything. for more info: %fight help",name)
							time.sleep(.5)
							privsend(" ", name)
							privsend("%help/%commands -=- displays basic help. pretty sure you know that already", name)
							privsend("%version -=- displays current bot version.", name)
							privsend("{0}: <message> -=- chat with {1}! this is tied into cleverbot".format(botname,botname), name)
							if VERBOSE: log("Sent help to {0}".format(name))
						if len(info) > 1 and info[1].strip('\r\n').lower() == 'ping' and PING_ENABLED:
							privsend("%ping <user> <message>",name)
							privsend("this sends a message to a specified user via slack. slack will notify a users phone when it receives a message.",name)
							privsend("if you want to be able to be pinged, let bgm know, along with your email address, and hell send you an invite.",name)
							privsend("----------------------",name)
							privsend("<user> - can be any slack username or someone in chat.",name)
							privsend("<message> - optional. can be any message.",name)
						if len(info) > 1 and info[1].strip('\r\n').lower() == 'reminders':
							privsend("%remindme/%remind me <timeframe> - <message>",name)
							privsend("set yourself a reminder for some time	to do something. when the time comes, youll be notified in here 3 different ways, and if you have a slack",name)
							privsend("account, it will send you a notification to your phone. due to the way irc sockets are handled, the reminder may be off by a minute or two, so",name)
							privsend("dont use it as a cooking timer unless you mind a few minutes extra cooking. ask bgm how to get a slack account if youre interested.",name)
							privsend("----------------------",name)
							privsend("<timeframe> - make it plain english. examples: %remindme in five minutes, %remindme on the second tuesday of march, %remindme 9/1/16, etc",name)
							privsend("<message> - message is required, and must be separated from the <timeframe> by a single dash (-).",name)
	
					# OVERLORD
					if any(info[0].lower() in s for s in overlord_keywords):
						sender = getNick(data)
						afile = open('overlord.txt', 'rb')
						line = rline(afile)
						afile.close()
						send("when i am an evil overlord, {0}".format(line)) if special == 0 else privsend("when i am an evil overlord, {0}".format(line),sender)
						if VERBOSE: log("Overlord: {0}".format(line))
		
					# MEMOS
					if any(info[0].lower() in s for s in memo_keywords):
						#--
						# This is the Memos feature.  It allows a user to set a memo for another inactive user.
						# It stores the memo in an external file.
						# When the target user becomes active again, it sends the memo from the file and then
						# deletes the line so it never resends.  The message sending is handles at the very
						# bottom of this script.  This is just to set the memo:
						#--
						if special == 1: name = getNick(data); privsend("you can only leave a memo in a public channel.  try this in {0}".format(channel),name); continue
						message = info[1:]
						fromnick = getNick(data)
						try:
							tellnick = message[0]
						except IndexError:
							send("{0} you dickmunch you need to specify a person".format(fromnick))
							continue
						if tellnick.lower() == botname.lower():
							send("why would i want to leave myself a memo tho")
							continue
						if tellnick.lower() == fromnick.lower():
							send("ok sure thing.")
							time.sleep(3)
							send("hey {0}, {0} says youre an idiot.".format(fromnick))
							continue
						sendraw("NAMES {0}".format(channel))
                                                channicks = getChatters()
                                                for i in channicks:
                                                        if tellnick.lower() in i.lower(): tellnick = i
						try:
							message = " ".join(message[1:])
							message = message.strip(' \t\r\n')
						except IndexError:
							send("{0} get some %help.  actually, learn to read first, then get some %help.".format(fromnick))
							time.sleep(.1)
							continue
						if not message: 
							send("{0} get some %help.  actually, learn to read first, then get some %help.".format(fromnick))
							time.sleep(.1)
							continue
						f = open('memos', 'a')
						f.write("{0}[-]{1}[-]{2}\n".format(fromnick,tellnick,message))
						f.close()
						if VERBOSE: log("{0} says \"Tell {1} {2}\"".format(fromnick, tellnick, message))
						send("ok ill tell {0} that you hate everything about them forever.".format(tellnick))
					
					# ROLL DICE
					if info[0].lower() == 'roll':
						try:
							totalroll = info[1]
						except:
							if special == 0: send("you need to specify a roll, like d20 or 2d10 or something.")
							else: usernick = getNick(data); privsend("you need to specify a roll, like d20 or 2d10 or something.",usernick)
							continue
						try:
							printlow = info[2]
						except:
							printlow = 'nope'
						totalroll = totalroll.split('d')
						try:
							rolls = int(totalroll[0])
						except:
							rolls = 1
						try:
							sides =	int(totalroll[1])
						except:
							if special == 0: send("you need to specify the amount of sides, like d20 or d10")
							else: usernick = getNick(data); privsend("you need to specify the amount of sides, like d20 or d10",usernick)
							continue
						if rolls < 1: 
							if special == 0: send("im assuming you want at least one roll")
							else: usernick = getNick(data); privsend("im assuming you want at least one roll",usernick)
							rolls = 1
						if sides < 1:
							if special == 0: send("ok let me just break the space-time continuum for you.")
							else: usernick = getNick(data); privsend("ok let me just break the space-time continuum for you.")
							continue
						equation = []
						total = 0
						try:
							for i in range(0,rolls):
								roll = (xOrShift() % sides) + 1
								total = total + roll
								if rolls < 20 and rolls > 1: equation.append(roll)
							if rolls >= 20: equation = "thats too many numbers for my digital fingers to type. just trust me that this is the total roll: {0}".format(total)
							elif rolls > 1: 
								lowest=equation[(equation.index(min(equation)))]
								if '-nolow' in printlow: equation[(equation.index(min(equation)))] = '({0})'.format(equation[(equation.index(min(equation)))])
								equation = " + ".join(map(str, equation))
								equation = '{0} = {1}'.format(equation,total)
								if '-nolow' in printlow: equation = '{0}. without the lowest roll: {2} - {3} = {1}'.format(equation,total-int(lowest),total,int(lowest))
							elif rolls == 1: equation = "heres your roll: {0}".format(total)
							if special == 0: send(equation)
							else: usernick = getNick(data); privsend(equation,usernick)
						except OverflowError:
							if special == 0: send("dude for real tho: http://www.wolframalpha.com")
							else: usernick = getNick(data); privsend("dude for real tho: http://www.wolframalpha.com", usernick)
							continue
				
					# GET A TWITTER FEED
					if any(info[0].lower() in s for s in showtwitter_keywords) and TWITTER_ENABLED:
						#--
						# Get the latest tweet from a specified username, or, if no username is specified,
						# get the latest tweet from a random follower.
						#--
						if special == 1: name = getNick(data); privsend("you can only get a tweet in a public channel.  try this in {0}".format(channel),name); continue
						try:
							tweetnick = info[1]
						except IndexError: # No username specified, so get a tweet from a random follower.
							try:
				                                fol = getRandomFollower() # Check twitbot.py for this and other twitter functions
				                        except tweepy.error.TweepError as e:
								print "error"
				                                if e.message[0]['code'] == 88:
									print "rate limit: {0}".format(getRateLimit())
									send("im making too many calls to twitter and the twitter hates when i do that.  try again later.")
				                                        continue
				                        send("lets see what one of my followers, {0}, is doing on twitter...".format(fol))
				                        time.sleep(1)
				                        mag = getTweet(fol)
				                        for tweet in mag:
				                        	try: # Is the message a retweet?  Let's grab it and specify that it's an RT
		                                                        mag = tweet.retweeted_status.text
		                                                        getrt = tweet.text.encode('utf-8','ignore') # Encode the message to be safe.
		                                                        getrt = getrt.split('@')[1].split(':')[0]
		                                                        mag = "RT @{0}: {1}".format(getrt,mag)									
		                                                except AttributeError:
		                                                        mag = tweet.text.encode('utf-8', 'ignore')
	        	                                                mag = "".join(c for c in mag if c not in ('\t'))
		                                                mag = mag.replace('\r', ' ')
		                                                mag = mag.replace('\n', ' ')
		                                                send("@{0} >> {1}".format(fol,mag))
								if VERBOSE: log("@{0} >> {1}".format(fol,mag))
							        send("follow {} to get your tweets in here".format(twittername))
							continue
						tweetnick = "".join(c for c in tweetnick if c not in ('\r', '\n', '\t')) # Strip any weird formatting in the user name.  Yes, this is a thing that happens.
						msg = getTweet(tweetnick)
						if VERBOSE: log("Twitter Handle: {0}".format(tweetnick))
						if msg == "-*404":
							send("that person doesnt really exist tho")
							if VERBOSE: log("Doesn't Exist")
							continue
						if msg == "-*501":
							send("@{0}'s profile is private and bigoted and hates synackbot because they wont let me follow them, so i cant see their tweets".format(tweetnick))
							if VERBOSE: log("Not Authorized")
							continue
						if len(msg) == 0:
							send("@{0} doesnt have no tweets yet".format(tweetnick))
							if VERBOSE: log("Doesn't have any tweets")
						for tweet in msg:
							try:
								msg = tweet.retweeted_status.text
								getrt = tweet.text.encode('utf-8','ignore')
								getrt = getrt.split('@')[1].split(':')[0]
								msg = "RT @{0}: {1}".format(getrt,msg)
							except AttributeError:
								msg = tweet.text.encode('utf-8', 'ignore')
								msg = "".join(c for c in msg if c not in ('\t'))
							msg = msg.replace('\r', ' ')
							msg = msg.replace('\n', ' ')
							tweetnick = tweetnick.encode('utf-8')
							send("@{0} >> {1}".format(tweetnick,msg))
							if VERBOSE: log("@{0} >> {1}".format(tweetnick, msg))
	
					# POST A TWEET
					if info[0].lower() == 'tweet' and TWITTER_ENABLED:
						#--
						# This allows users to make the bot send a tweet!
						# Configure an account complete with an API key here: https://dev.twitter.com
						# to allow users to tweet as your own bot.
						#--
						if special == 1: name = getNick(data); privsend("you can only post a tweet in a public channel.  try this in {0}".format(channel),name); continue
						fromnick = getNick(data)
						try:
							q = info[1:]
						except IndexError:
							send("you need to actually tweet something") if special == 0 else privsend("you need to actually tweet something",sender)
							continue
						if len(q) == 0:
							send("you didnt tweet anything dumby") if special == 0 else privsend("you didnt tweet anything dumby",sender)
							continue
						if q[0] == '%overlord\r\n':	# Did the user want to tweet an overlord quote?
							 afile = open('overlord.txt', 'rb')
	                                                 q = "{0}".format(rline(afile))
						else:
							q = " ".join(q)
						q = "{0}: {1}".format(fromnick,q)
						q = (q[:137] + '...') if len(q) > 140 else q
						if postTweet(q) == "DUPLICATE":
							send("you already said that dummy")
							continue 
						if VERBOSE: log("{0} tweeted: {1}".format(fromnick, q))
						sendraw("NAMES {0}".format(channel))
						person = getRandomPerson()
						send("ok i tweeted that. i hope i didnt sound like a stupid racist like {0}.".format(person)) if special == 0 else privsend("ok i tweeted that i hope i didnt sound like a stupid racist like you",sender)
						time.sleep(1)

					# SET A REMINDER
					if any(info[0].lower() in s for s in reminder_keywords):
						if len(info) < 3 or "-" not in info:
							if special == 0: send("ok so %help reminders is probably more your thing.")
							else: usernick = getNick(data); privsend("ok so %help reminders is probably more your thing.",usernick)
							continue							
						try:
							if info[0].lower() == 'remind' and info[1].lower() != 'me':
								if special == 0: send("you might want to check %help reminders")
								else: usernick = getNick(data); privsend("you might want to check %help reminders",usernick)
								continue
						except:
							if special == 0: send("ok so %help reminders is probably more your thing.")
							else: usernick = getNick(data); privsend("ok so %help reminders is probably more your thing.",usernick)
							continue
						alreadyset = 0
						cal = pdt.Constants()
						cal.BirthdayEpoch = 80
						cal = pdt.Calendar(cal)
						try:
							if info[0].lower() == 'remindme': message = info[1:]
							if info[0].lower() == 'remind' and info[1].lower() == 'me': message = info[2:]
						except: 
							if special == 0: send("heres your reminder: 1) learn to read, 2) read %help")
							else: usernick = getNick(data); privsend("heres your reminder: 1) learn to read, 2) read %help",usernick)
							continue
						message = " ".join(message)
						try:
							reminddate = message.split('-',1)[0].strip()
							message = message.split('-',1)[1:]
						except:
							if special == 0: send("did you put in a date for the reminder? %help reminders")
							else: usernick = getNick(data); privsend("did you put in a date for the reminder? %help reminders",usernick)
							continue
						message = " ".join(message)
						try:
							reminddate = cal.parse(reminddate)
						except:
							if special == 0: send("did you put in a date for the reminder? %help reminders")
                                                        else: usernick = getNick(data); privsend("did you put in a date for the reminder? %help reminders",usernick)
							continue
						try:
							checkdate = datetime.datetime.fromtimestamp(time.mktime(reminddate[0]))
						except OverflowError:
							if special == 0: send("no youll be dead by then")
							else: usernick = getNick(data); privsend("no youll be dead by then",usernick)
							continue
						timefloat = time.mktime(reminddate[0])
						if timefloat <= time.time():
							if special == 0: send("ok let me just go hop in my time machine")
							else: usernick = getNick(data); privsend("ok let me just go hop in my time machine",usernick)
                                                        continue
						try:
							reminddate = checkdate
						except:
							if special == 0: send("that doesnt make any sense.")
							else: usernick = getNick(data); privsend("that doesnt make any sense",usernick)
							continue
						with open('reminders','r+') as f:
							lines = f.readlines()
							f.seek(0)
							for line in lines:
								thisline = line.split('[-]')
								if thisline[0] == getNick(data) and timefloat < float(thisline[1]) < timefloat + 30.0:
									if special == 0: send("are you reminding me to remind you or do you have short-term memory loss?")
									else: usernick = getNick(data); privsend("are you reminding me to remind you or do you have short-term memory loss?")
									f.write(line)
									alreadyset = 1
									break
								elif thisline[0] == getNick(data) and time.time() < float(thisline[3]) + 120.0:
									if special == 0: send("hey calm down with the reminders, guy")
									else: usernick = getNick(data); privsend("hey calm down with the reminders, guy",usernick)
									f.write(line)
									alreadyset = 1
									break
								else:
									f.write(line)
									continue
	
							if alreadyset == 0:
								if VERBOSE: log("{0} set a reminder for {1}: {2}".format(getNick(data),reminddate.strftime("%m/%d/%y %H:%M:%S"),message.lstrip()))
								f.write("{0}[-]{1}[-]{2}[-]{3}\r\n".format(getNick(data),timefloat,message.lstrip().strip('\r\n'),time.time()))
								if special == 0: send("k reminder set for {0}".format(reminddate.strftime("%m/%d/%y %H:%M:%S")))
								else: usernick = getNick(data); privsend("k reminder set for {0}".format(reminddate.strftime("%m/%d/%y %H:%M:%S")),usernick)
							f.truncate()
							f.close()
			
					# PING
					if info[0].lower() == 'ping' and PING_ENABLED:
						if special == 1: name = getNick(data); privsend("you can only ping someone from a public channel.  try this in {0}".format(channel),name); continue
						try:
							touser = info[1]
						except:
							send("ping who now?")
							continue
						touser = touser.strip('@')
						touser = touser.strip(' \r\n')
						sendraw("NAMES {0}".format(channel))
                                                channicks = getChatters()
						for i in channicks:
							if touser.lower() in i.lower(): touser = i
						try:
							msg = " ".join(info[2:])
						except:
							msg = "alive?"
						msg = msg.strip('\r\n')
						if not msg: msg = "alive?"
						if VERBOSE: log("Ping request sent from: {0}, to: {1}, with this message: {2}".format(getNick(data),touser,msg))
						message = sendPing(getNick(data),touser,msg)
						if message != "Sent!":
							send(message)
							continue
						send("ok i pinged {0} for you now pay me $1.".format(touser))
			
					# WIKIPEDIA
					if any(info[0].lower() in s for s in wiki_keywords) and WIKIPEDIA_ENABLED:
						#--
						# Look up a word on Wikipedia and return the first sentence of the summary, as well as
						# the url to the article and other things to search for.
						#--
						sender = getNick(data)
						try:
							q = info[1:]
						except IndexError:
							send("whatchuwanna wiki, friend") if special == 0 else privsend("whatchuwanna wiki, friend",sender)
							continue
						q = " ".join(q)
						if VERBOSE: log("Wiki: {0}".format(q))
						result = wiki(q) # See wiki.py for more info on is and other wiki functions.
						if result == "-*e":
							send("that clearly doesnt exist") if special == 0 else privsend("that clearly doesnt exist",sender)
							continue
						if special == 0: send("ok one sec")
						else: name = getNick(data); privsend("ok one sec",name)
						time.sleep(1)
						if result[0] == "-*d":
							if len(result) > 10:
	                                                        result = result[1:10]
	                                                        result.append("etc...")
							result = ", ".join(result)
							result = result.encode('utf-8').lower()
							result = "".join(c for c in result if c not in ('\'','"','!',':',';'))
							if special == 0:
								send("theres a lot of stuff you could mean by that.")
								time.sleep(.5)
								send("stuff like: {0}".format(result))
							else: 
								name = getNick(data)
								privsend("theres a lot of stuff you could mean by that.",name)
                                                                time.sleep(.5)
                                                                privsend("stuff like: {0}".format(result),name)
							continue
						else:					
							url = result[0]
							desc = result[1]
							desc = desc.encode('utf-8').lower()
							desc = "".join(c for c in desc if c not in ('\'','"','!',':',';'))
							try:
								search = result[2]
							except IndexError:
								search = 0
							send(desc) if special == 0 else privsend(desc,sender)
							time.sleep(.5)
							send("more info here: {0}".format(url)) if special == 0	else privsend("more info here: {0}".format(url),sender)
							if search != 0: 
								search = (search[:497] + '...') if len(search) > 497 else search
								search = search.lower()
								search = "".join(a for a in search if (a.isalnum() or a in (",",".","'","\"","?","!","@","#","$","%","^","&","*","(",")","_","+","=","-","\\","|","]","}","{","[",";",":","/",">","<","`","~"," ")))
								send("see also: {0}".format(search)) if special == 0 else privsend("see also: {0}".format(search),sender)
							if VERBOSE: log("{0}\nMore Info: {1}\nSee Also: {2}".format(desc,url,search))
					
					# FIGHT
					if info[0].lower() == 'fight':
						#--
						# This is the chat fight subroutine.
						#--
						if getChannel(data) != fightchan:
							send("no we have a fight fightchan for this: /join {0}".format(fightchan))
							continue
						channel = fightchan
						try:
							act = info[1:]
						except IndexError:
							name = getNick(data)
							infight = 0
							with open('fightsongoing','r') as f:
								lines = f.readlines()
								f.seek(0)
								for line in lines:
									thisline = line.split('[-]')
									p1,p2,accepted,whoseturn = thisline[0],thisline[1],thisline[2],thisline[3]
									if p1.lower() == name.lower():
										infight = 1
										if int(accepted) == 1:
											fightsend("youre currently fighting {0} and its {1} turn.".format(p2,"your" if p1 == whoseturn else "{0}'s".format(p2)))
										else:
											fightsend("you sent a fight invite to {0}, but they didnt accept it yet.".format(p2))
										break
									elif p2.lower() == name.lower():
										infight = 1
										if int(accepted) == 1:
											fightsend("youre currently fighting {0} and its {1} turn.".format(p1,"your" if p2 == whoseturn else "{0}'s".format(p1)))
										else:
											fightsend("you were sent an invitation to fight from {0}. type %fight yes to accept or %fight no to decline.".format(p1))	
										break
								f.close()
							if infight == 0:
								sendraw("NAMES {0}".format(fightchan))
		                                                person = getRandomPerson()
								while person.lower() == name.lower(): person = getRandomPerson()
								fightsend("you arent fighting anyone right now.  youd better start with {0} or maybe someone else, idk.".format(person))
								continue
						except:
							fightsend("ive decided not to work right now. let bgm know how lazy i am please.")
							continue
						#--
						# We need to force the action to be in a list, so...
						#--
						if not hasattr(act,"__iter__"):
							act = [act]
						#--
						# Ok good, now let's clean up all the stuff
						#--
						act = [i.strip('\r\n') for i in act]
						#--
						# Done
						#--	
						try:
							tmp = act[0].lower()
						except IndexError:
							name = getNick(data)
                                                        infight = 0
                                                        with open('fightsongoing','r') as f:
                                                                lines = f.readlines()
                                                                f.seek(0)
                                                                for line in lines:
                                                                        thisline = line.split('[-]')
                                                                        p1,p2,accepted,whoseturn = thisline[0],thisline[1],thisline[2],thisline[3]
                                                                        if p1.lower() == name.lower():
                                                                                infight = 1
                                                                                if int(accepted) == 1:
                                                                                        fightsend("youre currently fighting {0} and its {1} turn.".format(p2,"your" if p1 == whoseturn else "{0}'s".format(p2)))
                                                                                else:
                                                                                        fightsend("you sent a fight invite to {0}, but they didnt accept it yet.".format(p2))
                                                                                break
                                                                        elif p2.lower() == name.lower():
                                                                                infight = 1
                                                                                if int(accepted) == 1:
                                                                                        fightsend("youre currently fighting {0} and its {1} turn.".format(p1,"your" if p2 == whoseturn else "{0}'s".format(p1)))
                                                                                else:
                                                                                        fightsend("you were sent an invitation to fight from {0}. type %fight yes to accept or %fight no to decline.".format(p1))
                                                                                break
                                                                f.close()
                                                        if infight == 0:
                                                                sendraw("NAMES {0}".format(fightchan))
								person = getRandomPerson()
                                                                while person.lower() == name.lower(): person = getRandomPerson()
                                                                fightsend("you arent fighting anyone right now.  youd better start with {0} or maybe someone else, idk.".format(person))
                                                                continue
							continue
						except:
							fightsend("i decided not to work today. let bgm know how lazy i am please.")
							continue

						if act[0].lower() == "help":
							name = getNick(data)
							if VERBOSE: log("Helping out this guy with fighting: {0}".format(name))
							try:
								if act[1].lower() == "actions":
									privsend("when its your turn, type %fight <number> to fightsend one of the following actions:",name)
									privsend("1 - attack: attacks the other guy.  how did you not kno this",name)
									privsend("2 - strong attack: you reel back go for a hail mary.  this has a higher chance to miss, but it does more damage if it connects.",name)
									privsend("3 - flurry attack: you just throw all the shit at the target and hope for a bullseye.  this has a higher chance of hitting, but at the cost of damage.",name)
									privsend("4 - magic attack: wave your hand around or some shit.  magic inherently does more damage than physical attacks, but has a slightly higher chance to miss.",name)
									privsend("5 - guard: put your hands up to reduce the damage of the next physical attack.  if you guard and the other guy tries a strong attack, theres a small chance for you to parry it.",name)
									privsend("6 - meditate: prepare your mind for the next magic attack.  if you meditate and the other guy uses a magic attack next round, you will reflect some of the damage and ignore the rest of it.",name)
									continue
								elif act[1].lower() == "stats":
									privsend("level - a numeric indicator of your current fighting prowess.  make this number bigger by fighting -- win or lose.",name)
									privsend("atk - your physical strength. directly affects physical attack damage.",name)
									privsend("grd - your physical defense. determines how much damage you take from physical attacks.",name)
									privsend("mag - your magic attack strength.  determines how much magic damage you can deal.",name)
									privsend("mdef - your magic defense. dermines how much damage you take from magic attacks.",name)
									privsend("hp - your hit points. determines how much damage you can take before you die and get killed.",name)
									privsend("xp - how many win points you need to raise the above numbers",name)
									privsend("--",name)
									privsend("you level when your xp dips to 0 or lower. that stats that go up are determined by what actions youve taken since your last level",name)
									continue
								else: privsend("what",name)
							except IndexError:
								if special == 0: fightsend("ok check your pms please and thankyou")
								privsend("heres da rulz:",name)
								privsend("1) you dont talk about this cliche",name)
								privsend("2) all fights are 1-on-1, so you gotta wait if someone you want to fight is already fighting",name)
								privsend("3) thats it try to make the fights dirty ok bye",name)
								privsend("------",name)
								privsend("heres a list or something:",name)
								privsend("%fight challenge <name> - challenge <name> to a fight",name)
								privsend("%fight stats (<name>) - get the stats of <name>, if no <name> specified, then get your own stats",name)
								privsend("%fight cancel - cancel a fight. if the fight hasnt been accepted, theres no penalty, otherwise your opponent gets a win",name)
								privsend("------",name)
                                                                privsend("theres additional help available by typing one of the following commands:",name)
                                                                privsend("%fight help actions - get more info on what each fight action does",name)
                                                                privsend("%fight help stats - get more info on what each stat does",name)
								continue


						elif act[0].lower() == "challenge":
							#--
							# Someone wants to challenge someone else.
							# So let's set that up.
							#--
							fighter = getNick(data)
							# Let's see if this person already has stats set...
							checkStats = getFighterStats(fighter)
							if not checkStats or checkStats is False:
								# No stats yet, so let's set this person up:
								setFighterStats(fname=fighter)
								if VERBOSE: log("Created a fighting statsheet for {}".format(fighter))
							else:
								if VERBOSE: log("Specs for {0}:\n{1}".format(fighter,checkStats))
							readytofight = 1
							try:
								challenger = act[1]
							except IndexError:
								fightsend("you need to specify a challenger dumny")
								continue
							if challenger.lower() == botname.lower(): fightsend("im more of a lover than a fighter"); continue
							if challenger.lower() == fighter.lower(): fightsend("no masochism allowed in chat thats like rule 3 or something."); continue
							sendraw("NAMES {0}".format(fightchan))
							channicks = getChatters()
							if not channicks: 
								time.sleep(2)
								channicks = getChatters()
							if not channicks:
								fightsend("hold on the irc server is being a dick and something errored on the back end.  try again later.")
								continue
							i = 0
							for j in channicks:
								if challenger.strip(' \r\n').lower() == j.strip(' \r\n').lower(): i += 1
							if i == 0: 
								fightsend("i dont kno who that is")
								continue
							with open('fightsongoing', 'r') as f:
								for line in f:
									initiator = line.split('[-]')[0]
									who = line.split('[-]')[1]
									accepted = line.split('[-]')[2]
									if fighter.lower() == initiator.lower():
										if int(accepted) == 1:
											fightsend("youre already fighting {0}. go finish that fight ok bye".format(who))
											readytofight = 0
											break
										else:
											fightsend("you have to wait for {0} to accept your other fight before starting a new one".format(who))
											readytofight = 0
											break
									if fighter.lower() == who.lower():
										if int(accepted) == 1:
											fightsend("youre already fighting {0}. go finish that fight ok bye".format(initiator))
											readytofight = 0
											break
										else:
											fightsend("{0} has already challenged you to a fight. if you accept this challenge type %fight yes, if you dont, type %fight no".format(initiator))
											readytofight = 0
											break
									if challenger.lower() == initiator.lower() or challenger.lower() == who.lower():
										fightsend("everyone hates {0} and theyre already in a fight so wait your turn".format(challenger))
										readytofight = 0
										break
							f.close()
							if readytofight == 1:
								f = open('memos', 'a')
		                                                f.write("{0}[-]{1}[-]Wanna fight? Come to {2} and type '%fight yes' or '%fight no'\n".format(fighter,challenger,fightchan))
                		                                f.close()
								f = open('fightsongoing','a')
								stopper = ''
								f.write("{0}[-]{1}[-]0[-]{2}[-]0[-]{3}[-]{4}\r\n".format(fighter,challenger,challenger,time.time(),stopper))
								f.close()
								fightsend("ok i will ask {0} to accept your challenge.  i wanna see blood gais".format(challenger))

						elif act[0].lower() == "rematch":
							foundamatch = 0
							readytofight = 1
							with open('fighters','r') as f:
								lines = f.readlines()
								f.seek(0)
								for line in lines:
									thisline = line.split('[-]')
									if thisline[0] == getNick(data):
										foundamatch = 1
										try:
											rematch = thisline[17]
										except:
											fightsend("i dont know who the last person you fought is. i must have been asleep or something idk")
											continue
										rematch = rematch.strip('\r\n')
										if not rematch: # Nobody
											fightsend("i dont know who the last person you fought is. i must have been asleep or something idk")
											continue
										if FIGHT_VERBOSE: log("{0} wants a rematch against {1}!".format(thisline[0],rematch))
										with open('fightsongoing', 'r') as g:
			                                                                for gline in g:
			                                                                        initiator = gline.split('[-]')[0]
			                                                                        who = gline.split('[-]')[1]
			                                                                        accepted = gline.split('[-]')[2]
                		                                                        	if thisline[0].lower() == initiator.lower():
		                                                                                	if int(accepted) == 1:
			                                                                                        fightsend("youre already fighting {0}. go finish that fight ok bye".format(who))
                        			                                                                readytofight = 0
                                                		        	                                break
                 		                                               		                else:
														if initiator.lower() == rematch.lower():
	        	                       	                                                		        fightsend("you already send a fight request to {0} so whats with the rematch request?".format(who))
														else:
															fightsend("you send a fight request to {0} already, so either cancel or wait before asking to rematch {1}".format(initiator,rematch))
			                       	                                                                readytofight = 0
                                                			                                        break
				                                                                if thisline[0].lower() == who.lower():
			                                                                                if int(accepted) == 1:
                        			                                                                fightsend("youre already fighting {0}. go finish that fight ok bye".format(initiator))
                                                			                                        readytofight = 0
                                                                        			                break
			                                                                                else:
                        			                                                                fightsend("{0} has already challenged you to a fight. if you accept this challenge type %fight yes, if you dont, type %fight no".format(initiator))
			                                                                                        readytofight = 0
                        			                                                                break
                                                			                        if rematch.lower() == initiator.lower() or rematch.lower() == who.lower():
			                                                                                fightsend("everyone hates {0} and theyre already in a fight so wait your turn".format(rematch))
                        			                                                        readytofight = 0
                                                		                                break
										g.close()
			                                                        if readytofight == 1:
				                                                	g = open('memos', 'a')
                                				                        g.write("{0}[-]{1}[-]Let's rematch! You'd better type '%fight yes' and not '%fight no'\n".format(thisline[0],rematch))
                                                                			g.close()
				                                                        g = open('fightsongoing','a')
                                				                        stopper = ''
                                                                			g.write("{0}[-]{1}[-]0[-]{2}[-]0[-]{3}[-]{4}\r\n".format(thisline[0],rematch,rematch,time.time(),stopper))
				                                                        g.close()
				                                                        fightsend("ok i will ask {0} if they want a rematch.".format(rematch))
								if foundamatch == 0:
									fightsend("um, did you ever fight before because i dont even know who you are. %fight help")
							f.close()

						elif act[0].lower() == "yes":
							# Let's make sure this person has a spec sheet now...
							challenger = getNick(data)
							checkStats = getFighterStats(challenger)
							winner = "test"
							if not checkStats or checkStats is False:
								setFighterStats(fname=challenger)
								if VERBOSE: log("Created a fighting statsheet for {}".format(challenger))
							else:
								if VERBOSE: log("Stats for {0}:\n{1}".format(challenger,checkStats))
							with open('fightsongoing', 'r+') as f:
								lines = f.readlines()
								f.seek(0)
								for line in lines:
									initiator = line.split('[-]')[0]
									opponent = line.split('[-]')[1]
	                                                                who = line.split('[-]')[3]
                	                                                accepted = line.split('[-]')[2]
									stopper = line.split('[-]')[6].strip('\r\n')
									if opponent.lower() == stopper.lower(): winner = initiator
									if initiator.lower() == stopper.lower(): winner = opponent
									if (stopper and stopper.lower() == challenger.lower()) and int(accepted) == 1:
										fightsend("seriously why do i even bother. fight canceled.")
										p1=getFighterStats(winner)
										p2=getFighterStats(stopper)
										fighting = 0
		                                                                if FIGHT_VERBOSE: log("{1} quit, so {0} wins!".format(p1[0],p2[0]))
		                                                                xp = getXPGain(p1[0],p1[0])
		                                                                setFighterStats(fname=winner,tmpstat='',tmpbuff=0,xp=int(p1[7]) - int(xp[0]),hp=getMaxHPByLevel(int(p1[1])),wins=(int(p1[8])+1))
		                                                                setFighterStats(fname=stopper,tmpstat='',tmpbuff=0,hp=getMaxHPByLevel(int(p2[1])))
										writeHistory(winner,stopper,"{0} canceled the fight! {1} won by default![-]==========================================[-]".format(stopper,winner))
		                                                                fightsend("{0} wins by default!".format(winner))
		                                                                fightsend("{0} gains {1} xp from the battle".format(winner,int(xp[0])))
		                                                                fightsend("{0} gains nothing because theyre a coward".format(stopper))
										p1 = getFighterStats(winner)
			                                                        if int(p1[7]) <= 0:
			                                                                fightsend("{0} leveled up!".format(winner))
											if FIGHT_VERBOSE: log("{0} leveled!".format(winner))
			                                                                results = levelUp(winner)
			                                                                newstats = getFighterStats(winner)
			                                                                privsend("hooray you leveled up.  heres a breakdown:",winner)
			                                                                for i in results:
			                                                                        privsend(i,winner)
			                                                                privsend("here are your new stats:",winner)
			                                                                privsend("level: {0}, attack: {1}, guard: {2}".format(newstats[1],newstats[2],newstats[3]),winner)
			                                                                privsend("magic attack: {0}, magic guard: {1}, total hp: {2}".format(newstats[4],newstats[5],newstats[6]),winner)
			                                                                privsend("xp to next level: {0}, total wins: {1}".format(newstats[7],newstats[8]),winner)
			                                                                setFighterStats(fname=winner,atksincelvl=0,satksincelvl=0,fatksincelvl=0,magatksincelvl=0,grdsincelvl=0,mgrdsincelvl=0)
										continue
									if (stopper and stopper.lower() != challenger.lower()) and (opponent.lower() == challenger.lower() or initiator.lower() == challenger.lower()) and int(accepted) == 1:
										fightsend("no you dont get to choose this.  this is between me and {0}".format(winner))
										f.write(line)
										continue
									if who.lower() == challenger.lower() and int(accepted) == 0:
										stopper = ''
										whofirst = [initiator,who]
										whofirst = whofirst[(xOrShift() % 2)]
										setFighterStats(fname=initiator,lastfought=who)
										setFighterStats(fname=who,lastfought=initiator)
										with open('fights.log','r+') as g:
											lines = g.readlines()
											g.seek(0)
											for line in lines:
												if who in line or initiator in line:
													continue
												else: g.write(line)
											g.truncate()
											g.close()
										writeHistory(initiator,who,"{0} began a fight against {1}!".format(initiator,who))
										f.write("{0}[-]{1}[-]1[-]{2}[-]1[-]{3}[-]{4}\r\n".format(initiator,who,whofirst,time.time(),stopper))
										fightsend("ok cool, i randomly pick {0} to go first. type %fight help actions if you dont know what to do".format(whofirst))
									else:
										f.write(line)
										continue
								f.truncate()
								f.close()

						elif act[0].lower() == "no" or act[0].lower() == "cancel" or act[0].lower() == "stop" or act[0].lower() == "quit":
							with open('fightsongoing','r+') as f:	
								lines = f.readlines()
								f.seek(0)
								for line in lines:
									initiator = line.split('[-]')[0]
									opponent = line.split('[-]')[1]
                                                                        who = line.split('[-]')[3]
                                                                        accepted = line.split('[-]')[2]
									stopper = line.split('[-]')[6].strip('\r\n')
									print "STOPPER: {0}".format(stopper)
									if getNick(data).lower() == initiator.lower(): person = opponent
									if getNick(data).lower() == opponent.lower(): person = initiator
                                                                        if (initiator.lower() == getNick(data).lower() or opponent.lower() == getNick(data).lower()) and int(accepted) == 0:
										with open('memos','r+') as g:
											glines = g.readlines()
											g.seek(0)
											for gline in glines:
												h = gline.split('[-]')[1]
												p = gline.split('[-]')[2]
												if who == h and "%fight yes" in p:
													continue
												else:
													g.write(gline)
											g.truncate()
											g.close()
										fightsend("wow. youre boring. ok then")
                                                                        	continue
									elif act[0].lower() != "no" and (initiator.lower() == getNick(data).lower() or opponent.lower() == getNick(data).lower()) and int(accepted) == 1 and not stopper:
										fightsend("what seriously?  if you stop the fight now {0} will still get full credit for winning. are you sure you want to stop? %fight yes or %fight no".format(person))
										f.write("{0}[-]{1}[-]1[-]{2}[-]1[-]{3}[-]{4}\r\n".format(initiator,opponent,who,time.time(),getNick(data)))
										continue
									elif act[0].lower() != "no" and (initiator.lower() == getNick(data).lower() or opponent.lower() == getNick(data).lower()) and int(accepted) == 1 and (stopper and stopper.lower() != getNick(data).lower()):
                                                                                fightsend("{0} is already trying to give you a victory, just shh ok?".format(stopper))
                                                                                f.write(line)
									elif act[0].lower() == "no" and (stopper and stopper.lower() == getNick(data).lower()) and (initiator.lower() == getNick(data).lower() or opponent.lower() == getNick(data).lower()):
										fightsend("stop flip floppin like a politician")
										stopper = ''
										f.write("{0}[-]{1}[-]1[-]{2}[-]1[-]{3}[-]{4}\r\n".format(initiator,opponent,who,time.time(),stopper))
									elif act[0].lower() == "no" and (stopper and stopper != getNick(data)) and (initiator == getNick(data) or who == getNick(data).lower()):
										fightsend("no you dont get a say in this.")
										f.write(line)
                                                                        else:
                                                                        	f.write(line)
								f.truncate()
								f.close()		

						elif act[0].lower() == "stats":
							try:
								whostats = act[1]
							except IndexError:
								whostats = getNick(data)
							checkStats = getFighterStats(whostats)
							if not checkStats or checkStats is False:
								fightsend("that person doesnt have a statsheet yet because they are a coward or idle.  probably a coward.")
								continue
							else:
								fightsend("stats for {0}:".format(whostats))
								fightsend("lvl: {0}, atk: {1}, grd: {2}, mag: {3}, mdef: {4}, hp: {5}, xp to next lvl: {6}, wins: {7}".format(checkStats[1],checkStats[2],checkStats[3],checkStats[4],checkStats[5],checkStats[6],checkStats[7],checkStats[8]))
						
						elif act[0].lower() == "history" and FIGHT_HISTORY:
							name = getNick(data)
							if VERBOSE: log("Getting fight history for {0}".format(name))
							fightlog = getHistory(name)
							if not fightlog or fightlog is None:
								fightsend("nothing. theres nothing here. youve fought no one. you lose. good day sir.")
								if VERBOSE: log("No history.")
								continue
							try:	
								fightlog = fightlog.split('[-]')
								p1=fightlog[0]
								p2=fightlog[1]
								lines = len(fightlog)
								for i in range(2,lines):
									fightlog[i] = fightlog[i] + "\r\n"
								fightlog.remove(fightlog[1])
								fightlog.remove(fightlog[0])
								fightlog = "".join(fightlog)
								pbin_vars = {'api_dev_key':PASTEBIN_DEV_KEY,'api_option':'paste','api_paste_code':fightlog,'api_paste_private':1,'api_paste_name':'Fight between {0} and {1}'.format(p1,p2),'api_paste_expire_date':'N'}
								response = urllib.urlopen('http://pastebin.com/api/api_post.php', urllib.urlencode(pbin_vars))
								url = response.read()
								fightsend("ok go here: {0}".format(url))
								if VERBOSE: log("Fight history uploaded to: {0}".format(url))
								continue
							except:
								fightsend("super. i think ive temporarily forgotten how to read. try again later.")
								if VERBOSE: log("Couldn't get history.")
								continue
	
						elif len(act[0]) == 1:
							name = getNick(data)
							canattack = 0
							inafight = 0
							with open('fightsongoing', 'r') as f:
                                                                for line in f:
									if name.lower() in line: inafight = 1
									if name.lower() == line.split('[-]')[3].lower() and int(line.split('[-]')[2]) == 1:
                                                                        	attacker = line.split('[-]')[3]
										if attacker == line.split('[-]')[1]:
											defender = line.split('[-]')[0]
										else:
											defender = line.split('[-]')[1]
										canattack = 1
										fighting = 1
							if 1 <= int(act[0]) <= 6 and canattack == 1:
								results = resolveAttack(int(act[0]),attacker,defender)
								if results is False or not results: 
									fightsend("not implemented, sorry")
									continue
								fightsend(results[2])
							else:	
								if canattack == 0: 
									if inafight == 1: fightsend("it isnt your turn stop being impatient")
									else: fightsend("you arent even fighting or anything.")
								else: fightsend("youre not making any sesne. use %fight help if you need, you know, help")
                                                                continue
							
							p1 = getFighterStats(attacker)
							p2 = getFighterStats(defender)
							if int(p2[6]) <= 0:
								fighting = 0
								if FIGHT_VERBOSE: log("{0} wins!".format(p1[0]))
								xp = getXPGain(attacker,defender)
								setFighterStats(fname=attacker,tmpstat='',tmpbuff=0,xp=int(p1[7]) - int(xp[0]),hp=getMaxHPByLevel(int(p1[1])),wins=(int(p1[8])+1))
								setFighterStats(fname=defender,xp=int(p2[7]) - int(xp[1]),tmpstat='',tmpbuff=0,hp=getMaxHPByLevel(int(p2[1])))
								fightsend("{0} died!  better luck next time.".format(defender))
								fightsend("{0} gains {1} xp from the battle".format(attacker,int(xp[0])))
								fightsend("{0} gains {1} xp for pity".format(defender,int(xp[1])))
								writeHistory(attacker,defender,"{0} died! {0} got {2}xp, {1} got {3}xp![-]=============================================[-]".format(defender,attacker,xp[1],xp[0]))
								with open('fightsongoing', 'r+') as f:
									lines = f.readlines()
									f.seek(0)
		                                                       	for line in lines:
                		                                               	initiator = line.split('[-]')[0]
                                		                                who = line.split('[-]')[1]
                                                              		        if attacker.lower() == initiator.lower() or attacker.lower() == who.lower():
											continue
										else:
											f.write(line)
									f.truncate()
									f.close()
							if int(p1[6]) <= 0:
                                                                fighting = 0
                                                                if FIGHT_VERBOSE: log("{0} wins!".format(p2[0]))
                                                                xp = getXPGain(defender,attacker)
                                                                setFighterStats(fname=defender,xp=int(p2[7]) - int(xp[0]),tmpstat='',tmpbuff=0,hp=getMaxHPByLevel(int(p2[1])),wins=(int(p2[8])+1))
                                                                setFighterStats(fname=attacker,xp=int(p1[7]) - int(xp[1]),tmpstat='',tmpbuff=0,hp=getMaxHPByLevel(int(p1[1])))
                                                                fightsend("{0} died!  better luck next time.".format(attacker))
                                                                fightsend("{0} gains {1} xp from the battle".format(defender,int(xp[0])))
                                                                fightsend("{0} gains {1} xp for pity".format(attacker,int(xp[1])))
								writeHistory(attacker,defender,"{0} died! {0} got {2}xp, {1} got {3}xp![-]=============================================[-]".format(attacker,defender,xp[1],xp[0]))
                                                                with open('fightsongoing', 'r+') as f:
                                                                        lines = f.readlines()
                                                                        f.seek(0)
                                                                        for line in lines:
                                                                                initiator = line.split('[-]')[0]
                                                                                who = line.split('[-]')[1]
                                                                                if attacker.lower() == initiator.lower() or attacker.lower() == who.lower():
                                                                                        continue
                                                                                else:
                                                                                        f.write(line)
                                                                        f.truncate()
                                                                        f.close()
							if fighting == 1:
								p1 = getFighterStats(attacker)
								p2 = getFighterStats(defender)
								fightsend("hp remaining --==-- {0}: {1}, {2}: {3}".format(p1[0],p1[6],p2[0],p2[6]))
							p1 = getFighterStats(attacker)
							p2 = getFighterStats(defender)
							if int(p1[7]) <= 0:
								fightsend("{0} leveled up!".format(attacker))
								results = levelUp(attacker)
								newstats = getFighterStats(attacker)
								privsend("hooray you leveled up.  heres a breakdown:",attacker)
								for i in results:
									privsend(i,attacker)
								privsend("here are your new stats:",attacker)
								privsend("level: {0}, attack: {1}, guard: {2}".format(newstats[1],newstats[2],newstats[3]),attacker)
								privsend("magic attack: {0}, magic guard: {1}, total hp: {2}".format(newstats[4],newstats[5],newstats[6]),attacker)
								privsend("xp to next level: {0}, total wins: {1}".format(newstats[7],newstats[8]),attacker)
								zero=0
								setFighterStats(fname=attacker,atksincelvl=zero,satksincelvl=zero,fatksincelvl=zero,magatksincelvl=zero,grdsincelvl=zero,mgrdsincelvl=zero)
							if int(p2[7]) <= 0:
								fightsend("{0} leveled up!".format(defender))
								results = levelUp(defender)
								newstats = getFighterStats(defender)
								privsend("hooray you leveled up. heres a breakdown:",defender)
								for i in results:
									privsend(i,defender)
								privsend("here are your new stats:",defender)
								privsend("level: {0}, attack: {1}, guard: {2}".format(newstats[1],newstats[2],newstats[3]),defender)
                                                                privsend("magic attack: {0}, magic guard: {1}, total hp: {2}".format(newstats[4],newstats[5],newstats[6]),defender)
                                                                privsend("xp to next level: {0}, total wins: {1}".format(newstats[7],newstats[8]),defender)
								zero = 0
								setFighterStats(fname=defender,atksincelvl=zero,satksincelvl=zero,fatksincelvl=zero,magatksincelvl=zero,grdsincelvl=zero,mgrdsincelvl=zero)
							if fighting == 1:
								updateFight(attacker)
						else:
							fightsend("maybe you need to look at %fight help.  or learn how to read.  one of the two.")
						
				else:
					lastMessage = getMessage(data).strip('\r\n')
					lastPerson = getNick(data)
					lastTime = time.time()
					if data.lower().find(botname.lower() + ':') != -1 and getChannel(data) == defchannel: # Did someone say "botname: "?
						msg = getMessage(data)
						msg = msg.lower().split(botname.lower())[1:]
						msg = " ".join(msg)
						msg = msg.strip(' \t\r\n')
						msg = msg.replace(':', '', 1)
						if VERBOSE: log("{0} >> {1}: {2}".format(getNick(data),botname,msg))
						msg = msg.lower()
						if VERBOSE: log("Attempting to reply with cleverbot...")
						try:
							msg = convo.think(msg); # Trigger a cleverbot response
						except:
							if VERBOSE: log("Hmm.. something is wrong on cleverbot's side..")
							continue
						msg = msg.lower()
						msg = "".join(c for c in msg if c not in ('\'','"','!',':',';'))
						send("{0}".format(msg))
						if VERBOSE: log("{0}: {1}".format(botname, msg))
						# END FIGHT

			# Below is the YouTube info method.
			if YOUTUBE_LINKS and getChannel(data) == defchannel:
				try:
					youtube = re.findall(r'(https?://)?(www\.)?((youtube\.(com))/watch\?v=([-\w]+)|youtu\.be/([-\w]+))', getMessage(data))
				except:
					continue
				if youtube:
					vidid = [c for c in youtube[0] if c]
					print vidid
					vidid = vidid[len(vidid)-1]
					print vidid
					try:
						vidinfo = getVideo(vidid)
					except:
						send("fake video alert fake video alert fake video alert.")
						continue
					send("that video is titled \"{0}\" and it is {1} in length. just fyi".format(vidinfo[0],vidinfo[1]))

			#-- 
			# Below is the Gimli subroutine.
			# It looks for two back-to-back instances of the word "and" beginning a sentence
			# If it sees that, it prints "AND MY AXE!"
			#
			# Fun fact: This is the only thing the bot returns in its own voice that contains a capital letter.
			# This is by design.
			#--
			if getChannel(data) == defchannel:
				gimli = getMessage(data)
				try: 
					gimli = gimli.split(' ')[0:]
				except AttributeError:
					gimli = "Nope"
				if gimli[0].lower() == 'and' and gimli[1].lower() == 'my':
					andcount+=1
					if VERBOSE: log("Gimli = {0}".format(andcount))
					if andcount == 2:
						send("AND MY AXE!")
						andcount=0
						if VERBOSE: log("Gimli subroutine triggered!")
				else:
					andcount=0
			#-- END GIMLI
	
			#--
			# Below is the process to tell someone a memo that was left for them,
			# and then remove that memo from the memo file.
			# This will send to either the main bot channel or the fighting channel,
			# depending on where the user goes active.
			#--
			memnick = getNick(data) # Get the nickname of the person who last said something.
			f = open('memos', 'r+')
			lines = f.readlines()
			f.seek(0) # Go to the beginning of the file
			for line in lines:
				if memnick == line.split('[-]')[1]: # If the nickname we got earlier is the second name in the line, they have a memo
					if getChannel(data) == defchannel:
						send("hey {0}, {1} said >> tell {2} {3}".format(line.split('[-]')[1],line.split('[-]')[0],line.split('[-]')[1],line.split('[-]')[2]))
					else:
						fightsend("hey {0}, {1} said >> tell {2} {3}".format(line.split('[-]')[1],line.split('[-]')[0],line.split('[-]')[1],line.split('[-]')[2]))
					if VERBOSE: log("Told {0} {1}".format(line.split('[-]')[1],line.split('[-]')[2]))
					continue
				else:
					# if the nickname doesn't match, just write the same line again
					f.write(line)
			f.truncate()
			f.close()
			#-- END MEMO
		
		#--
		# This is the random chatter algorithm.
		# Basically, grab a random number between 1000 and 99991231 and adds an XOR Shift (see fightbot.py).
		# Mod that number by 300.  This returns a number between 0 and 299.
		# If that number is less than or equal to 5, say something.
		# 
		# This usually works out to the bot saying something every hour on average.
		# Sometimes it says two things back to back.
		# Sometimes it takes 5 hours between an idle talk.
		# It's all random.
		#--
		if (random.randint(1000, 99991231) + xOrShift()) % 300 < 1:
			saysomething = random.randint(1,101)
			if saysomething < 15:
				afile = open('overlord.txt', 'rb')
				thisline = rline(afile)
				thisline = "".join(c for c in thisline if c not in ('\'','"','!','?',':',';'))
				send("when i am an evil overlord, {0}".format(thisline))
				if VERBOSE: log("Random Chatter: when i am an evil overlord, {0}".format(thisline))
			if 15 < saysomething < 30:
				afile = open('marvin.txt', 'rb')
				thisline = rline(afile)
				thisline = "".join(c for c in thisline if c not in ('\'','"','!','?',':',';'))
				send("{0}".format(thisline))
				if VERBOSE: log("Random Chatter: {0}".format(thisline))
			if 30 < saysomething <= 45 and TWITTER_ENABLED:
				followAll()
				try:
		                        fol = getRandomFollower()
	                        except tweepy.error.TweepError as e:
	                                print "error"
	                                if e.message[0]['code'] == 88:
	                                	print "rate limit: {0}".format(getRateLimit())
	                                        send("you guys are all farts")
	                                        continue
	                        try:
					send("lets see what one of my followers, {0}, is doing on twitter...".format(fol))
				except UnboundLocalError:
					log("Something is wrong with twitter.")
					continue
	                        time.sleep(1)
	                        mag = getTweet(fol)
				if mag == "-*404":
                                	send("not sure how this happened, but that person doesnt exist anymore.  this is an error that no one should ever see.  please send msg to bgm and let him know i broke")
                                        if VERBOSE: log("Doesn't Exist")
                                        continue
                                if mag == "-*501":
                                	send("nevermind.  @{0} is a buttface and wont accept my follow request".format(tweetnick))
                                        if VERBOSE: log("Not Authorized")
                                        continue
	                        for tweet in mag:
	                        	try:
	                                	mag = tweet.retweeted_status.text
	                                        getrt = tweet.text.encode('utf-8','ignore')
	                                        getrt = getrt.split('@')[1].split(':')[0]
	                                        mag = "RT @{0}: {1}".format(getrt,mag)
	                                except AttributeError:
	                                        mag = tweet.text.encode('utf-8', 'ignore')
	                                        mag = "".join(c for c in mag if c not in ('\t'))
	                                mag = mag.replace('\r', ' ')
	                                mag = mag.replace('\n', ' ')
	                                send("@{0} >> {1}".format(fol,mag))
					if VERBOSE: log("Random Chatter: @{0} >> {1}".format(fol, mag))
	                                send("follow {} to get your tweets in here".format(twittername))
			if 45 < saysomething <= 100:
				# Let's make sure the variables are initialized.
				try:
					lastMessage
				except:
					lastMessage = "Hi"
				try:
					lastPerson
				except:
					lastPerson = "bgm"
				try:
					lastTime
				except:
					lastTime = time.time()
				# If the last thing said was over two hours ago, just forget about it.
				if ((time.time() - lastTime) / 60) > 120: 
					continue
				# Otherwise, let's generate a CleverBot response.
				if VERBOSE: log("Attempting to make an idle cleverbot response...")
				try:
					msg = convo.think(lastMessage)
				except:
					if VERBOSE: log("Hmm.. something went wrong.  Probably on cleverbot's side.")
					continue
                                msg = msg.lower()
				msg = "".join(c for c in msg if c not in ('\'','"','!',':',';'))
				if VERBOSE: 
					log("Random Chatter: Last message from {0} was {1}.".format(lastPerson,lastMessage))
					log("Random Chatter: Replying to {0} with: {1}".format(lastPerson,msg))
				send("{}".format(msg))
                        if 100 < saysomething:
				#--
				# Have a really, really small chance of singing the DK rap because why not.
				#
				# This is an even smaller chance than the above rate.
				# This grabs a number between 1 and 99991231, mods it by 300,
				# then it multiplies 246 times a random number between 3 and 37,
				# then it multiplies THAT number by the modded number we got previously (which
				# is between 0 and 299), and THEN it mods that number by 1999.
				# If, after all that, the result is 64, it sings the DK rap.
				#
				# Some info behind those seemingly random choices for numbers:
				# 246 = The touchtone code for bgm
				# 1999 = The year DK 64 came out.
				# 64 = The second best Nintendo console ever.
				#--
				if (((random.randint(1, 99991231) % 300) * (246*random.randint(3,37))) % 1999) == 64:
					if VERBOSE: log("It sang the DK rap!")
					send("here here here here here we go")
					time.sleep(.5)
					send("well theyre finally here, performing for you")
					time.sleep(.5)
					send("and if you know the words you can join in too")
					time.sleep(.5)
					send("put your hands together if you want to clap")
					time.sleep(.5)
					send("as we take you through this monkey rap")
					time.sleep(.5)
					send("d-k.  donkey kong.")
					time.sleep(.5)
					send("d-k.  DONKEYKONGISHERE.")
	
#-- Make sure this is the main script
if __name__ == '__main__':
	if not CONFIGURED:
		print("Please configure the bot first.")
		sys.exit()
	main(0)
else:
        print("You can't import this script.")
        sys.exit()
#--
