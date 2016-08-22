#!usr/bin/env python
# encoding=utf-8
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
#		- A creepy stalker subrouting (I'm a horror fan)
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
from gr3ysql import Gr3ySQL
from chatterbotapi import ChatterBotFactory, ChatterBotType
from fightbot import *
from difflib import SequenceMatcher
from confessions import *
from os import path
from decimal import *
from time import sleep, strftime, localtime
from pytz import timezone
import socket, struct, select, string
import sys, random, math, signal
import threading, urllib, urllib2, urlparse
import json, pytz, datetime, feedparser, re
import parsedatetime as pdt
if YOUTUBE_LINKS: from bottube import *
if URBANDICT_ENABLED: from urbandict import *
if GOOGLE_ENABLED: from googlebot import *
if TWITTER_ENABLED: from twitbot import *
if TWITCH_NOTIFICATIONS_ENABLED: from twitchbot import getIsTwitchStreaming
if YELP_ENABLED: from yelpbot import *
if WEATHER_ENABLED: from weatherbot import *
if NEWS_LINKS: from summarize import *
if WIKIPEDIA_ENABLED: from wiki import wiki
if QR_ENABLED: import qrtools
if WOLFRAM_ENABLED: from wolfbot import *
if TELEGRAM_ENABLED: from telebot import Pinger

#-- Version, and AI initialization, and variables
random.seed()

os.environ['TZ'] = LOCALTZ
reload(sys)
sys.setdefaultencoding('utf8')

AI = ChatterBotFactory()
botAI = AI.create(ChatterBotType.CLEVERBOT)
convo = botAI.create_session()
dbInit = Gr3ySQL().init(checkEq=True)
con = Gr3ySQL()
pinger = Pinger()
pinger.bot.message_loop(pinger.addNewUser)

andcount = 0 #for gimli
creepfactor = 0 #for creep
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
def setSocket():
	global irc
	(fam, socktype, protocol, j, address) = socket.getaddrinfo(server, port)[0]
	irc = socket.socket (fam, socktype, protocol)
	irc.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
	irc.setsockopt(socket.SOL_TCP, socket.TCP_KEEPIDLE, 1)
	irc.setsockopt(socket.SOL_TCP, socket.TCP_KEEPINTVL, 1)
	irc.setsockopt(socket.SOL_TCP, socket.TCP_KEEPCNT, 5)
	print "Connecting to {0}:{1}".format(server,port)
	irc.connect((server,port))
	if len(channelpw) > 1:
		irc.send ( 'PASS {0} \r\n'.format(channelpw) )
	print "Setting nickname to {0}...".format(botname)
	irc.send ( 'NICK {0}\r\n'.format(botname) )
	print "Identifying the bot..."
	irc.send ( 'USER {0} {1} {2} :Python-powered IRC bot to help moderate #pub, the official channel of the Greynoise podcast\r\n'.format(botname,botname,botname) )
	print "Joining the channels..."
	channel = channels[0]
	for c in channels:
		irc.send ( 'JOIN {0}\r\n'.format(c))
	if len(fightchan) > 0:
		irc.send ( 'JOIN {0}\r\n'.format(fightchan))
#--

#-- Send a message upon joining the channel
def joinmsg(chan, dcd=1):
	if dcd == 1:
		irc.send ( 'PRIVMSG {0} :hey type %help if youre dumn\r\n'.format(chan))
	else:
		irc.send ( 'PRIVMSG {0} :im back bitches.  you thought you could kill me but ive only become stronger\r\n'.format(chan))
#--

#-- Perform actions when the server sends a PING message
def pingActions(chan):
#--
# Since IRC servers send out a PING message at fixed intervals, I use it for timed functions.
#
# Reset the fight history flood protection...

        # Check to see if anyone tweeted at the bot...
        if TWITTER_ENABLED: checkTwits(chan)
        checkReminders(chan)

        # Have a 30% chance to shift the XOR bits in the fightbot RNG (this is to try to make it more random)
        if (random.randint(1,99193) * int(time.time())) % 100 < 30:
        	shift = xOrShift()
                if LOGLEVEL >= 1: log("XOR bits shifted to: {0}".format(shift))


#-- Identify with NICKSERV
def ident():
	print "Identifying with NICKSERV..."
	irc.send ( 'PRIVMSG NICKSERV :IDENTIFY {0}\r\n'.format(password) )
#--

#-- Functions
def log(text):
	localnow = datetime.datetime.now(timezone(LOCALTZ))
	with open(LOGFILE, 'a+') as g:
		g.write("{0} --==-- {1}\r\n".format(localnow.strftime(timeformat),text))
		if ECHO_LOG: print "{0} --==-- {1}".format(localnow.strftime(timeformat),text)
	g.close()

def addToSearchDb(nick,msg):
	q = con.db.cursor()
	try:
		q.execute("""
			SELECT * FROM Log WHERE user = ? """, (nick,))
		count = len(q.fetchall())
		if not count or count is None or count < MSG_HISTORY:
			q.execute("""
				INSERT INTO Log (dateTime, user, text) VALUES (?, ?, ?) """, (time.time(), nick, msg))
		if count == MSG_HISTORY:
			q.execute("""
				SELECT id FROM Log WHERE user = ? ORDER BY id ASC """, (nick,))
			firstId = int(q.fetchone()[0])
			q.execute("""
				DELETE FROM Log WHERE id = ? """, (firstId,))
			q.execute("""
				INSERT INTO Log (dateTime, user, text) VALUES (?, ?, ?) """, (time.time(), nick, msg))
		con.db.commit()
	except Exception as e:
		if LOGLEVEL >= 1: log("ERROR: Cannot fetch last {0} user messages: {1}".format(MSG_HISTORY, str(e)))
		q.rollback()

def pingAll(fromuser, msg):
	print "pingall reached"
	q = con.db.cursor()
	try:
		q.execute(""" SELECT * FROM TelegramIDs """)
		n = q.fetchall()
		for pinger in n:
			print pinger
			sendPing(fromuser,pinger[0],msg)
	except:
		if LOGLEVEL >= 2: log("Couldn't send ping to everyone.")

def admins(nick, host):
	if LOGLEVEL >= 1: log("Call for an admin check.  Is {} an admin?".format(host))
	rawbuff = ""
	for thing in ADMINLIST:
		isAdmin = re.compile(thing+'@.+')
		if (re.match(isAdmin, host)):
			if LOGLEVEL >= 1: log("Found a matching admin nick ({}).  Are they identified?".format(nick))
			sendraw('PRIVMSG NickServ :STATUS {0}'.format(nick))
                	time.sleep(1)
			try:
		                rawbuff = rawbuff + irc.recv(1024)
				f = rawbuff.split('\n')
				rawbuff = f.pop()
			except Exception as e:   
				if LOGLEVEL >= 1: log("ERROR: Couldn't fetch admin status.")
				return 0
			for thing in f:
				if ':NickServ!NickServ' in thing[0:18] and 'NOTICE {0} :STATUS {1} 3'.format(botname,nick) in thing:
					return 1
				else:
					return 2
	return 0

def getHost(host):
	host = host.split('!')[1]
	host = host.split(' ')[0]
	return host

def utc2loc(utctime):
	utct = datetime.datetime.strptime(utctime,'%Y-%m-%dT%H:%M:%S')
	localDt = utct.replace(tzinfo=pytz.utc).astimezone(timezone(LOCALTZ))
	return timezone(LOCALTZ).normalize(localDt)

def getChannel(data):
	try:
		chan = data.split('#')[1]
		chan = chan.split(':')[0]
		chan = '#' + chan
		chan = chan.translate(None, "\t\r\n")
	except IndexError:
		chan = defchannel
	return chan

def getNick(data):
	nick = data.split('!')[0]
	nick = nick.replace(':', '')
	nick = nick.translate(None, "\t\r\n")
	return nick

def getChatters(rawdata="",chan=channel):
	if LOGLEVEL >= 1: log("Call for list of names in {0}".format(chan))
	names = False
	sendraw("NAMES {0}".format(chan))
        time.sleep(1)
        rawdata = rawdata+irc.recv(1024)
	f = rawdata.split('\n')
	rawdata = f.pop()
	for data in f:
		if '353' in data:
			names = data.split('353')[1]
			names = names.split(':')[1]
			names = names.split(' ')
			names = [i.replace('@', "").replace("~","").strip('\r\n') for i in names]
			try:
				names.remove(botname)
			except ValueError: names = names
			if LOGLEVEL >= 1:
				log("People in the channel:")
				for i in names:
					log(i)
	if names == False or names is None:
		return "lonely"
	if len(names) == 0:
		return "lonely"
	return names

def getRandomPerson(chan=channel):
	names = getChatters(chan=chan)
	if not names or len(names) == 0: return False
	if names == "lonely": return "lonely"
	else: person = names[random.randint(0,len(names) - 1)]
	return person

def makeEncode(text):
	try:
		text = unicode(text, encoding='utf8')
		return text
	except UnicodeDecodeError:
		try:
			text = unicode(text, encoding='cp1252')
			return text
		except UnicodeDecodeError:
			try:
				text = unicode(text, encoding='iso8859-1')
				return text
			except UnicodeDecodeError:
				try:
					text = unicode(text, encoding='ascii')
					return text
				except Exception as e:
					if LOGLEVEL >= 1: log("ERROR: Couldn't display text: {}".format(str(e)))
					return False

def strTranslate(text):
	text = str(text).translate(None, "\r\n")
	return text

def makeBotText(text, tell):
	if not tell:
		text = str(text).translate(None, "'")
		if len(re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)) < 1:
			text = str(text).translate(None, "?")
	text = text.lower()
	return text
	
def cleanText(text, tell=False):
	if len(text) > 490: text = text[:485] + '[CUT]'
	text = strTranslate(text)
	text = makeBotText(text, tell)
	text = makeEncode(text)
	return text

def bufferData(data):
	if "\r" not in data or "\n" not in data: return False
	data = data[:data.index("\r\n")+len("\r\n")]
	return data
	
def sendPing(fromuser, touser, msg):
	try:
		pinger.sendPing(fromuser,touser,msg)
		return "Sent!"
	except:
		return "Error"
	

def getMessage(data):
	try:
		msg = data.split('#',1)[1]
	except IndexError:
		msg = None

	if msg is not None:
		msg = msg.split(':',1)[1:]
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

def join(chan):
	irc.send('JOIN ' + chan + '\r\n')

def quit(chan):
	irc.send('PART ' + chan + '\r\n')

def send(msg,chan=channel,tell=False,s=0,u=None):
	if s == 1:
		privsend(msg,u)
		return
	msg = cleanText(msg,tell)
	if msg != False: irc.send('PRIVMSG ' + chan + ' :{0}\r\n'.format(msg))

def fightsend(msg,tell=False):
	msg = cleanText(msg,tell)
	irc.send('PRIVMSG ' + fightchan + ' :{0}\r\n'.format(msg))

def sendraw(msg):
	irc.send((msg + '\n').encode('utf-8'))

def privsend(msg, nick):
	msg = cleanText(msg)
	irc.send('PRIVMSG ' + nick + ' :{0}\r\n'.format(msg))

def op(opuser,chan=channel):
	if isinstance(opuser, list):
		for i in opuser:
			irc.send('MODE {0} +o {1}\r\n'.format(chan,i.strip('\r\n')))
	else:
		irc.send('MODE {0} +o {1}\r\n'.format(chan,opuser))

def deop(opuser,chan=channel):
	if isinstance(opuser, list):
		for i in opuser:
			irc.send('MODE {0} -o {1}\r\n'.format(chan,i.strip('\r\n')))
	else:
		irc.send('MODE {0} -o {1}\r\n'.format(chan,opuser))

def kick(user, reason, chan=channel):
	reason = reason.translate(None, "\t\r\n")
	irc.send('KICK ' + chan + ' ' + user + ' :{0}'.format(reason))

def rline(f):
	line = next(f)
	for n, randline in enumerate(f):
		if random.randrange(n+2): continue
		line = randline
	return line

def regexp(search, string):
	try:
		if re.search(r"\b{}(\S?)\b".format(search), string, re.IGNORECASE):
			return 1
	except Exception as e:
		return 0

def searchAndReplace(u, s, r, chan):
	q = con.db.cursor()
	try:
		q.execute("""
			SELECT * FROM Log WHERE user = ? AND text REGEXP ? ORDER BY id DESC LIMIT 1""", (u, s))
		row = q.fetchall()
		if len(row) == 1:
			row = row[0]
			search = re.compile(re.escape(s), re.IGNORECASE)
			send("{0} is dumb and probably meant to say: \"{1}\"".format(row[2],search.sub(r, row[3])),chan)
		if LOGLEVEL >= 1: log("Made a search and replace request")
	except Exception as e:
		if LOGLEVEL >= 1: log("ERROR: Unable to perform search and replace: {}".format(str(e)))
		pass

def checkTwits(chan=channel):
	#--
	# Let's check to see if someone tweeted at the bot every so often.
	# If so, post the message in chat.
	#--
	if LOGLEVEL >= 1: log("Checking for tweets @ the bot...")
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
	#		if LOGLEVEL >= 1: log("Twitter has reached a bandwidth limit and kicked back no response.")
	#	return False
	except Exception as e:
		if LOGLEVEL >= 1: log("Error with twitter: {0}".format(str(e)))
		return False
	try:
		if twts != False:
			if len(twts) > 0:
				j = 0
			      	send("ive got some new tweets @ me...",chan)
			        if LOGLEVEL >= 1: log("Someone tweeted at {0}!".format(botname))
			        for i,msg in enumerate(twts):
			              	mag = getTweet(0,checkids=msg)
					if '@' + mag.user.screen_name.lower() == twittername.lower():
						send("oh nm its just me for some reason",chan)
						continue
					send("@{0} >> {1}".format(mag.user.screen_name,mag.text,chan),tell=True)
			        if LOGLEVEL >= 1: log("@{0} >> {1}".format(mag.user.screen_name,mag.text))
				q = convo.think(mag.text.encode('utf-8')); # Trigger a cleverbot response
		                q = q.translate(None, "'\"!:;")
				q = "@{0} {1}".format(mag.user.screen_name,q)
				if "@{}".format(mag.user.screen_name) != "{}".format(twittername):
					send("i think ill reply with: {0}".format(q),chan)
					try:
						postTweet(q.lower())
					except Exception as e:
						if LOGLEVEL >= 1: log("Couldn't post tweet: {0}".format(str(e)))
						pass
				else:
					send("making me talk to myself. clever.",chan)
			else: 
				if LOGLEVEL >= 1: log("None found!")
		else: 
			if LOGLEVEL >= 1: log("None found!")
	except Exception as e:
	       	if LOGLEVEL >= 1: log("ERROR: Couldn't fetch tweet: {}".format(str(e)))
			
def checkReminders(chan=channel):
	#--
	# Check the reminders file to see if anyone needs to be reminded
	# of anything...
	#--
	q = con.db.cursor()
	q.execute("""
		SELECT * FROM Reminders WHERE atTime < ? """, (time.time(),))
	for row in q:
		send("hey {0}, heres a reminder for you: {1}".format(row[1],row[3]),chan)
                privsend("hey {0}, heres a reminder for you: {1}".format(row[1],row[3]),row[1])
                sendPing("GreyBot","{}".format(row[1]),"heres your reminder: {0}".format(row[3]))
                q.execute("""
			INSERT INTO Memos (fromUser, toUser, message, dateTime) VALUES (?, ?, ?, ?) """, (botname, row[1], row[3], time.time()))
		q.execute("""
			DELETE FROM Reminders WHERE id = ? """, (row[0],))
		con.db.commit()
                if LOGLEVEL >= 1: log("Sent a reminder to {0}!".format(row[1]))
	#--

#-- Main Function
def main(joined):
	setSocket()
	ident()
	con.db.create_function("regexp", 2, regexp)
	disconnected = 0
	isStreaming = 0
	joined = False
	threshold = 15 * 60
	lastPing = time.time()
	readBuffer = ""
	dataRetries = 3
	while True:
		time.sleep(0.05)
		try:
			if len(f) > 0: f.pop() # Flush data
		except: pass
		special = 0
		action = 'none'
		dataReady = select.select([irc], [], [], 10)
		for s in dataReady[0]:
			if s == sys.stdin:
				k = sys.stdin.readline()
				continue
			else:
				try:
					raw = irc.recv(1024)
					# Reply to PING
					if raw[0:4] == 'PING':
						try:
							if LOGLEVEL >= 1: log("Receiving a PING.")
							lastPing = time.time()
							tellinghistory = 0
							time.sleep(1)
							irc.send('PONG ' + raw.split()[1] + '\r\n')
							dataRetries = 3
							if LOGLEVEL >= 1: log("Sent a PONG: 'PONG {}\\r\\n'".format(raw.split()[1]))
							pingActions(getChannel(raw))
						except Exception as e:
							if LOGLEVEL >= 1: log("Couldn't send PONG response: {}".format(str(e)))
		                                	continue
		
					readBuffer = readBuffer + raw
					f = readBuffer.split('\n')
					readBuffer = f.pop()
				except socket.error as e:
					print str(e)
					continue
		connected = "Thu"
		#if (time.time() - lastPing) > threshold and len(raw) == 0:
		if len(raw) == 0 and dataRetries > 0:
			time.sleep(5)
			if LOGLEVEL >= 1: log("Lost connection. Awaiting reply from server...")
			dataRetries = dataRetries - 1
		if len(raw) == 0 and dataRetries <= 0:
			if LOGLEVEL >= 1: 
				log("\n============================================\nFATAL ERROR:\n============================================")
				log("The bot has been disconnected from the server.  Reconnecting...")
				log("\n============================================\nEND OF ERROR\n============================================")
			try:
				#sendPing("Gr3yBot","bgm","The bot died.  Check the logs for info.")
				lastPing = time.time()
			except Exception as e:
				log("Could not send ping to bgm for reason: {}".format(str(e)))
			disconnected=True
			irc.close()
			setSocket()
			ident()
			#sys.exit()

		for data in f:
			if LOGLEVEL == 3: 
				log(raw)
			elif LOGLEVEL >= 2:
				log(data)
			
			try:
				if joined == False:
					if disconnect == 0:
						for chan in channels:
							join(chan)
							joinmsg(chan, 1)
						ident()
					else:
						for chan in channels:
							join(chan)
							joinmsg(chan, 2)
					joined = True
					disconnected=False
					ident()
			except NameError:
				if joined == False:
					for chan in channels:
						join(chan)
						joinmsg(chan, 1)
					ident()
					joined = True
			
		
			if data.find('#') != -1:
				action = data.split('#')[0]
				action = action.split(' ')[1]
				connected = connected + "nderf"
			try:
				name = getNick(data)
				host = getHost(data)
				if data.startswith(':{0}!{1} PRIVMSG {2}'.format(name,host,botname)):
					action = 'PRIVMSG'
					special = 1
			except:
				action = 'none'
				special = 0

			if data.find('NICK') != -1:
				if data.find('#') == -1:
					action = 'NICK'

			if action != 'none':
				sender = getNick(data)
				connected = connected + "ury, Bless"
				defchannel = channels[0]
				checkReminders(getChannel(data))
				if action == 'JOIN': joined = 1
				if action == 'PRIVMSG':
					if getChannel(data) == fightchan:
						channel = fightchan
					else:
						channel = getChannel(data)
					if data.find('%') != -1: # Change the % here to be ! or whatever you want the command trigger to be
						x = data.split(':',2)[2:] # let's make sure to get all the text
						x = " ".join(x)
						x = x.split('%',1)[1:] # Do the same as before, but with any other commands later on in the line
						x = " ".join(x)
						info = x.split(' ') # Now let's turn it back into a list
						info[0] = info[0].translate(None, "\t\r\n")
						info[0] = ''.join(c for c in info[0] if c not in ('.',',','!','?',':','"','\''))
						if len(info[0]) == 0: continue
						#--
						# Separate fights from normal stuff
						#
						if channel == fightchan and info[0].lower() != 'fight' and fightchan != defchannel:
							fightsend("sorry bud, i only do fights here.  if you want the other stuff, /join {0}".format(defchannel))
							continue
						#--
						if LOGLEVEL >= 1: log("Command found: %{0}".format(info[0]))

						#--
						# info[0] gets set to whatever the first thing after % is in chat.
						# info[1:] refers to all other text after it.
						#--
					
						###===================================###
						#                                       #
						#       START ADMIN ONLY COMMANDS       #
						#                                       #
						###===================================###					
		
						#--
						# IDENT COMMAND
						if info[0].lower() == 'ident' and special == 0:
							nick = getNick(data)
							host = getHost(data)
							status = admins(nick, host)
							if status == 1:
								ident()
								continue
							elif status == 2:
								send("i mean, you look like an admin but can you identify like an admin",getChannel(data))
								continue
							else:
								send("you dont know what youre talking about",getChannel(data))
								continue

						# OPER COMMAND
						if info[0].lower() == 'op' and special == 0:
							nick = getNick(data)
							host = getHost(data)
							status = admins(nick, host)
							try:
								who = info[1].translate(None, "\t\r\n")
							except:
								send("who do you wanna op",getChannel(data))
								continue
							if status == 1:
								try:
									op(who,getChannel(data))
									if LOGLEVEL >= 1: log("Opped {0}".format(who))
								except TypeError:
									send("who do you wanna op, dumb dumn",getChannel(data))
									continue
							elif status == 2:
								send("i mean, you look like an admin but can you identify like an admin",getChannel(data))
								continue
							else:
								send("you dont know what youre talking about",getChannel(data))
								continue
						#--

						# KICK COMMAND
						if info[0].lower() == 'kick' and special == 0:
							nick = getNick(data)
							host = getHost(data)
							status = admins(nick, host)
							if "".join(info[1]).rstrip().lower() == botname.lower():
								send("nah",getChannel(data))
								continue
							reason = " ".join(info[2:]).rstrip()
							if not reason or reason is None:
								reason = "sorry i hit the wrong key and now youve been kicked"
							if status == 1:
								try:
									sendraw("KICK {0} {1} :{2}".format(defchannel,"".join(info[1]).rstrip(),reason))
									if LOGLEVEL >= 1: log("Kicked {0}.".format(info[1]))
								except Exception as e:
									send("nah",getChannel(data))
									if LOGLEVEL >= 1: log("Failed to kick {0} for reason {1}. Error message: {2}".format(info[1].translate(None, "\t\r\n"),reason,str(e)))
							elif status == 2:
								send("i mean, you look like an admin but can you identify like an admin",getChannel(data))  
								continue
							else:
								send("you dont know what youre talking about.",getChannel(data))
						#--

						#--
						# JOIN COMMAND
						if info[0].lower() == 'join' and special == 0:
							nick = getNick(data)
							host = getHost(data)
							status = admins(nick, host)
							try:
								info[1].rstrip()
							except:
								send("i am joined iddiot",getChannel(data))
								continue
							if status == 1 and '#' in info[1].rstrip():
								send("ok",getChannel(data))
								sendraw('JOIN {0}'.format(info[1].rstrip()))
							elif status == 2 and '#' in info[1].rstrip():
								send("you look like an admin but can you identify like an admin",getChannel(data))
								continue
							else:
								send("ill join my fist to your face",getChannel(data))
								continue
						#--

						#--
						# QUIT COMMAND
						if info[0].lower() in ('quit','leave','part') and special == 0:
							nick = getNick(data)
							host = getHost(data)
							status = admins(nick,host)
							if status == 1:
								send("ok",getChannel(data))
								time.sleep(1)
								quit(getChannel(data))
							elif status == 2:
								send("mmmmmmmm if you identify yourself as an admin first i might take you seriously",getChannel(data))
								continue
							else:
								send("no",getChannel(data))
								continue

						# ANNOUNCE (MUST HAVE TELEGRAM ENABLED)
						if TELEGRAM_ENABLED and (info[0].lower() in ('announce','tellall','pingall')) and special == 0:
							nick = getNick(data)
							host = getHost(data)
							status = admins(nick, host)
							try:
								msg = info[1].translate(None, "\t\r\n")
							except:
								send("what are you announcing idiot",getChannel(data))
								continue
							if status == 1:
								try:
									pingAll("The Greynoise Podcast",msg)
									if LOGLEVEL >= 1: log("{0} made an announcement.".format(nick))
								except:
									send("announcements might be broken",getChannel(data))
									continue
							elif status == 2:
								send("i mean, you look like an admin but can you identify like an admin",getChannel(data))
                                                                continue
                                                        else:
                                                                send("you dont know what youre talking about",getChannel(data))
                                                                continue

						#--
						# DEOP COMMAND
						if info[0].lower() == 'deop' and special == 0:
							nick = getNick(data)
							host = getHost(data)
							status = admins(nick, host)
							try:
								who = info[1].translate(None, "\t\r\n")
							except:
								send("who do you want to deop tho",getChannel(data))
								continue
							if status == 1:
								try:
									deop(who,getChannel(data))
									if LOGLEVEL >= 1: log("Deopped {0}".format(who))
								except TypeError:
									send("who do you wanna deop, dumb dumn",getChannel(data))
									continue
							elif status == 2:
								send("i mean, you look like an admin but can you identify like an admin",getChannel(data))
								continue
							else:
								send("you dont know what youre talking about",getChannel(data))
								continue
						#--

						# TOPIC COMMAND
						if info[0].lower() == 'topic' and special == 0:
							nick = getNick(data)
							host = getHost(data)
							status = admins(nick, host)
							if status == 1:
								try:
									topic = info[1:]
									topic = " ".join(topic)
									topic = topic.replace('http //','http://').translate(None, "\t\r\n")
									send("the new topic is butts.  discuss, everyone.",getChannel(data))
									time.sleep(2)
									irc.send("TOPIC {0} :{1}\n".format(getChannel(data),topic))
									if LOGLEVEL >= 1: log("Topic changed to: {0}".format(topic))
								except:
									sendraw("TOPIC {0}".format(getChannel(data)))
									time.sleep(.5)
									topic = irc.recv(2056)
									topic.split("{0}: ".format(getChannel(data)))
									send(topic[1],getChannel(data))
							elif status == 2:
								send("i mean, you look like an admin but can you identify like an admin",getChannel(data))
								continue
							else:
								send("you dont know what youre talking about",getChannel(data))
								continue

						# SHOW START/STOP COMMAND
						if info[0].lower() == 'show' and special == 0:
							try:
								started
							except:
								started = None
							nick = getNick(data)
							host = getHost(data)
							status = admins(nick, host)
							try:
								cmd = info[1].rstrip()
							except:
								send("%show?  what?  do you want to start or stop a show? dont be dumn",getChannel(data))
								continue
							if status == 1:
								if cmd == 'start':
									if started == False or started is None:
										started = True
										questions = []
										if LOGLEVEL >= 1: log("Show has Started!")
										send("ok folks the show has started.  ask a question starting with %q and the hosts will answer them at the end of the show",getChannel(data))
										send("so like: %q why does my butt smell so bad",getChannel(data))
										continue
									else:
										send("the show already started doe",getChannel(data))
										continue
								elif cmd == 'stop':
									if started == True:
										if LOGLEVEL >= 1: log("Show stopped, sending questions to the hosts...")
										send("ok shows over folks nothing to see here go home.",getChannel(data))
										send("wait no what i meant was ive sent your questions to the hosts",getChannel(data))
										if len(questions) > 0:
											for thing in questions:
												for admin in ADMINLIST:
													privsend(thing,admin)
											questions = []
										else:
											send("nobody asked questions?  boooo",getChannel(data))
										started = False
										continue
									else:
										send("the show hasnt been started yet doe",getChannel(data))
										continue		

							elif status == 2:
								send("are you really a host.  i mean.  can you identify like a host.",getChannel(data))
								continue
							else:
								send("{0}".format("i think only a host can {0} a show tho.  ill ask hold on".format(cmd)) if "start" == cmd.lower() or "stop" == cmd.lower() else "what go away",getChannel(data))
								continue
	
						# ASK A QUESTION TO THE SHOW HOSTS
						if info[0].lower() == 'q':
							try:
								questions
							except NameError: 
								if LOGLEVEL >= 1: log("{0} tried to ask a question outside of the show boundries.".format(getNick(data)))
								continue
							try:
								query = info[1:]
							except:
								send("you need to actually ask a question",getChannel(data)) if special == 0 else privsend("you need to actually ask a question",getNick(data))
								continue
							query = " ".join(query)
							if started == True:
								questions.append("{0} asks: {1}".format(getNick(data),query))
								send("ok got it",getChannel(data)) if special == 0 else privsend("ok got it",getNick(data))

						###===================================###
						#					#
						#	END ADMIN ONLY COMMANDS		#
						#					#
						###===================================###
					
						# VERSION COMMAND
						if info[0].lower() == 'version':
							if special == 0: send("Gr3yBOT by bgm: version {0}. You know you wanna fork me: https://github.com/ninjanerdbgm/Gr3yBOT".format(version),getChannel(data))
							else: name = getNick(data); privsend("Gr3yBOT by bgm: version {0}. You know you wanna fork me: https://github.com/ninjanerdbgm/Gr3yBOT".format(version),name)
							if LOGLEVEL >= 1: log("Version: {0}".format(version))

						# BIRTHDAY PROBLEM
						if info[0].lower() == 'room':
							try:
								roomSize = info[1]
								roomSize = math.ceil(float(roomSize))
							except:
								send("yo u gotta tell me how many people are in the room tho. \"%room 10\" for example",getChannel(data))
								continue
							if roomSize <= 0:
								send("hah look at this friendless loser",getChannel(data))
								continue
			
							if roomSize > 365:
								send("there is a 100% chance that two people share a birthday. go make friends",getChannel(data))
								continue

							if roomSize > 80:
								send("theres a 99.99% chance that two people share a birthday. go make friends",getChannel(data))
								continue
							try:
								a = Decimal(math.factorial(366))
								b = Decimal(366 ** roomSize)
								c = Decimal(math.factorial(366 - roomSize))
								bday = 1 - (a / (b * c))
							except:
								send("nobody has that many friends.")
								continue
			
							if bday > 1: bday = 1
							send("theres a {0}% chance that two people share a birthday. go make friends".format(format(bday * 100, '.2f')),getChannel(data))
							continue
							
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
							if LOGLEVEL >= 1: log("The next {0} events at SynShop:".format(end))
							if special == 0: send("geez fine, check your pms",getChannel(data))
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
								if LOGLEVEL >= 1: log("Sent the following info to {0}:\n{1} - {2}\nWhen: {3}\nMore Info: {4}".format(nick, name, desc, gettime.strftime("%A, %B %d %Y"), url))
								time.sleep(2)
								i = i + 1
							privsend("visit synshop: 1075 american pacific drive suite c, henderson, nv, 89074", nick)
							privsend("-- done, ok thx bai --", nick)					
		
						# BREAKFAST, BRUNCH, LUNCH, DINNER COMMANDS	
						if (info[0].lower() in yelp_keywords) and YELP_ENABLED:
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
							except (TypeError, Exception) as e:
								if LOGLEVEL >= 1: log("Non-fatal Yelp error: {0}".format(str(e)))
								if special == 0: send("what?  did a cat walk all over your keyboard just now?",getChannel(data))
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
							if LOGLEVEL >= 1: log("Suggesting: {0} ({1} stars from {2} reviews).  URL: {3}".format(name,rating,reviews,url))
							if special == 0: send("maybe you should try {0}? ({1} stars from {2} reviews). more info: {3}".format(name,rating,reviews,url),getChannel(data))
							else: usernick = getNick(data); privsend("maybe you should try {0}? ({1} stars from {2} reviews). more info: {3}".format(name,rating,reviews,url),usernick)

						# QR DECODE
						if info[0].lower() == 'qr' and QR_ENABLED:
							try:
								qrurl = str(info[1])
							except IndexError:
								send("give me the exact link you want decoded",getChannel(data)) if special == 0 else privsend("give me the exact link you want decoded",getNick(data))
								continue
							regex = (r'(?:([^:/?#]+):)?(?://([^/?#]*))?([^?#]*\.(?:jpg|gif|png|jpeg))(?:\?([^#]*))?(?:#(.*))?')
							if len(qrurl) > 0 and re.match(regex, qrurl):
								send("ok let me get my phone out real quick",getChannel(data)) if special == 0 else privsend("ok let me get my phone out real quick",getNick(data))
								qr = qrtools.QR()
								try:
									path = urlparse.urlparse(qrurl).path
									ext = os.path.splitext(path)[1]
									ext = ext.translate(None, '\r\n')
									urllib.urlretrieve(qrurl, 'lastqr'+ext)
									qr.decode('lastqr'+ext)
									send("i think it says: {}".format(qr.data),getChannel(data)) if special == 0 else privsend("i think it says: {}".format(qr.data),getNick(data))
								except Exception as e:
									if LOGLEVEL >= 1: log("ERROR: Can't decode QR code: {}".format(str(e)))
									send("oops i dropped my phone and now i cant read qr codes sorry",getChannel(data)) if special == 0 else privsend("oops I dropped my phone and now i cant read qr codes sorry",getNick(data))
									continue
							else:
								send("thats not a qr code",getChannel(data)) if special == 0 else privsend("thats not a qr code",getNick(data))
								continue
							

						# URBAN DICTIONARY
						if info[0].lower() == 'define' and URBANDICT_ENABLED:
							try:
								mean = info[1:]
							except IndexError:
								if special == 0: send("i dont kno how to define nothing, guy",getChannel(data))
								else: usernick = getNick(data); privsend("what",usernick)
								continue
							word = " ".join(mean)
							word = "".join(c for c in word if c not in ('\n','\r','\t')) # Rebuild the string letter by letter to strip out certain things.  You'll see this a lot in this script
							if LOGLEVEL >= 1: log("Define {0}:".format(word))
							meaning, example, url = getWord(word)
							if meaning is None:
								if special == 0: send("that doesnt seem to be a thing.",getChannel(data))
								else: usernick = getNick(data); privsend("that doesnt seem to be a thing",usernick)
								if LOGLEVEL >= 1: log("Nothing Found.")
								continue
							if example is None:
								if LOGLEVEL >= 1: log("Nothing Found.")
								send("aint nothing found. go away.",getChannel(data),special,getNick(data))
								continue
							if special == 0:
								try:
									send("first thing i could find:",getChannel(data))
									send("{0} - {1}".format(word, meaning),getChannel(data))
									send("example: {0}".format(example),getChannel(data))
									send("this is where you can get more definitions: {0}".format(url),getChannel(data))					
								except Exception as e:
									if LOGLEVEL >= 1: log("Error with urban dictionary: {0}".format(str(e)))  
									send("i found something but i cant read it because im not alive nor am i literate",getChannel(data))
									continue
							else:
								name = getNick(data)
								privsend("first thing i could find:",name)
								privsend("{0} - {1}".format(word, meaning),name)
								privsend("example: {0}".format(example),name)
								privsend("this is where you can get more definitions: {0}".format(url),name)
								if LOGLEVEL >= 1: log("{0} - {1}\nExample: {2}\nMore Info: {3}".format(word,meaning,example,url))

						# WEATHER
						if info[0].lower() == 'weather':
							if WEATHER_ENABLED == False:
								continue
							usernick = getNick(data)
							degrees = 'F'
							try:
								where = info[1:]
							except IndexError:
								if special == 0: send("the weather of space is cold and dark",getChannel(data))
								else: privsend("the weather of space is cold and dark",usernick)
								continue
							where = " ".join(where)
							where = "".join(c for c in where if c not in ('\n','\r','\t'))
							if LOGLEVEL >= 1: log("Get weather for {0}".format(where))
							weather = getWeather(where)
							if weather == "~*404" or weather is None:
								if special == 0: send("i dont know where dat iz",getChannel(data))
								else: privsend("i dont know where dat iz",usernick)
								if LOGLEVEL >= 1: log("Nothing found.")
								continue
							if special == 0:
								local = timezone(LOCALTZ)
								send("weather for {0}:".format(weather['location']),getChannel(data))
								send("currently {0} at {1}{2}. precipitation: {5} {6}. humidity is currently {3}%, with an atmospheric pressure of {4}".format(weather['cloudcover'],weather['temp'],degrees,weather['humidity'],weather['pressure'],weather['visibility'],weather['windchill']),getChannel(data))
								send("wind is blowing {0} at {1}mph. sunrise today is at {2} and sunset is at {3}".format(weather['winddirection'],weather['windspeed'],utc2loc(weather['sunrise']).strftime("%I:%M%p"),utc2loc(weather['sunset']).strftime('%I:%M%p')),getChannel(data))
							elif special == 1:
								local = timezone(LOCALTZ)
                                                                privsend("weather for {0}:".format(weather['location']),usernick)
                                                                privsend("currently {0} at {1}{2}. precipitation: {5} {6}. humidity is currently {3}%, with an atmospheric pressure of {4}".format(weather['cloudcover'],weather['temp'],degrees,weather['humidity'],weather['pressure'],weather['visibility'],weather['windchill']),usernick)
                                                                privsend("wind is blowing {0} at {1}mph. sunrise today is at {2} and sunset is at {3}".format(weather['winddirection'],weather['windspeed'],utc2loc(weather['sunrise']).strftime("%I:%M%p"),utc2loc(weather['sunset']).strftime('%I:%M%p')),usernick)

						# FORECAST
						if info[0].lower() == 'forecast':
							if WEATHER_ENABLED == False:
								continue
							usernick = getNick(data)
							degrees = 'F'
							try:
								where = info[1:]
							except IndexError:
								if special == 0: send("i see a shitstorm in your future",getChannel(data))
								else: privsend("i see a shitstorm in your future",usernick)
								continue
							where = " ".join(where)
							where = "".join(c for c in where if c not in ('\n','\r','\t'))
							if len(where) < 2: 
								if special == 0: send("i see a shitstorm in your future",getChannel(data))
                                                                else: privsend("i see a shitstorm in your future",usernick)
                                                                continue
							if LOGLEVEL >= 1: log("Get forecast for {0}".format(where))
							forecast = getForecast(where)
							if forecast == "~*404":
								send("i dunno go look outside dumby",getChannel(data))
								continue
							loc = str(forecast[0][8])
							loc = loc.replace("<name>","").replace("</name>","")
							if LOGLEVEL >= 1: log("Sent weather for {0} to {1}".format(loc,usernick))
							if special == 0: send("forecast for {0}".format(loc),getChannel(data))
							if special == 1: privsend("forecast for {0}".format(loc),usernick)
							for i in forecast:
								if special == 0: send("from {0} to {1} (PST) you can expect {2}{3}. temperature will be {4}{5} with a {6} coming from the {7} at {8}mph.".format(utc2loc(i[0]).strftime('%I:%M%p'),utc2loc(i[1]).strftime('%I:%M%p'),i[2],i[3],i[4],degrees,i[5],i[6],i[7]),getChannel(data))
								else: privsend("from {0} to {1} (PST) you can expect {2}{3}. temperature will be {4}{5} with a {6} coming from the {7} at {8}mph.".format(utc2loc(i[0]).strftime('%I:%M%p'),utc2loc(i[1]).strftime('%I:%M%p'),i[2],i[3],i[4],degrees,i[5],i[6],i[7]),usernick)
									

						# WOLFRAM ALPHA
						if info[0].lower() == 'calc':
							try:
								eq = info[1:]
							except IndexError:
								if special == 0: 
									if "vindiesel" in getNick(data).replace('_','').lower(): send("i cant divide by zero.  only you can.",getChannel(data))
									else: send("only vin diesel can divide by zero",getChannel(data))
								else:
									if "vindiesel" in getNick(data).replace('_','').lower(): privsend("i cant divide by zero.  only you can.",getNick(data))
									else: privsend("only vin diesel can divide by zero",getNick(data))
								continue
							eq = " ".join(eq)
							eq = "".join(c for c in eq if c not in ('\n','\r','\t'))
							if LOGLEVEL >= 1: log("Wolfram Calculation for: {0}".format(eq))
							send("ok let me put on my thinking cap one sec..",getChannel(data))
							calcAnswers,calcURL = addTwoPlusTwo(eq)
							if not calcAnswers or calcAnswers is None:
								send("im not going to even bother calculating that.",getChannel(data))
								continue
							else:
								if LOGLEVEL >= 1: log("Answers:")
								for thing in calcAnswers:
									try:
										if LOGLEVEL >= 1: log(thing)
										send(thing,getChannel(data))
									except:
										pass
								send("more info: {0}".format(calcURL),getChannel(data))

						# PODCAST INFO
						if (info[0].lower() in podcast_keywords):
							if special == 0: send("ok one sec...",getChannel(data))
							else: usernick = getNick(data); privsend("one sec",usernick)
							time.sleep(1.5)
							feed = feedparser.parse("https://greynoi.se/feed")
													
							if special == 0:
								send("latest episode: {0}".format(feed["entries"][0]["title_detail"]["value"]),getChannel(data))
								time.sleep(1.5)
								send("description: {0}".format(feed["entries"][0]["summary_detail"]["value"]),getChannel(data))
								time.sleep(1.5)
								send("more info: {0}".format(feed["entries"][0]["id"]),getChannel(data))
								time.sleep(1.5)
								send("ok im done now thx",getChannel(data))
							else:
								name = getNick(data)
								privsend("latest episode: {0}".format(feed["entries"][0]["title_detail"]["value"]),name)
								time.sleep(1.5)
								privsend("description: {0}".format(feed["entries"][0]["summary_detail"]["value"]),name)
								time.sleep(1.5)
								privsend("more info: {0}".format(feed["entries"][0]["id"]),name)
								time.sleep(1.5)
								privsend("ok im done now thx",name)
							if LOGLEVEL >= 1: log("Episode: {0}\nDescription: {1}\nURL: {2}".format(feed["entries"][0]["title_detail"]["value"],feed["entries"][0]["summary_detail"]["value"],feed["entries"][0]["id"]))
							
						# HELP
						if (info[0].lower() in help_keywords):
							name = getNick(data)
							if len(info) == 1:
								if special == 0: send("geez {} are you slow or something god.  check your pms".format(name),getChannel(data))
								privsend("%op <user> -=- allows you to op the specified <user>. only works if youre a podcaster.", name)
								time.sleep(.5)
								privsend("%topic <topic> -=- allows you to change the <topic>.  only works if youre a podcaster.", name)
								time.sleep(.5)
								privsend("%tell <nick> <message> -=- stores a <message> for <nick> and sends it to them when they become active again.", name)
								if TELEGRAM_ENABLED: privsend("%ping <nick> <message> -=- send a message to <nick> via telegram.  this should ping their phone.  message is optional.  want to be able to be pinged? type %help ping", name)
								privsend("%remindme <timeframe> - <message> -=- remind yourself to do something in the future. %help reminders for more info", name)
								time.sleep(.5)
								if TWITTER_ENABLED: privsend("%tweet <message> -=- make   send a tweet containing <message>.", name)
								if TWITTER_ENABLED: privsend("%twit <user> -=- <user> is optional.  retrieves the last tweet from <user> or from a random follower", name)
								time.sleep(.5)
								if YELP_ENABLED: 
									privsend("%breakfast/%brunch/%lunch/%dinner <location> -=- gives you a random restaurant suggestion for the provided location.",name)
									privsend("  ===  ==  = <location> is optional (default is las vegas), and can be a city, state or a zip code.",name)
								if WIKIPEDIA_ENABLED: privsend("%wiki/%wikipedia/%lookup/%search <string> -=- search wikipedia for <string> and return a quick summary.", name)
								if URBANDICT_ENABLED: privsend("%define <word(s)> -=- define stuff from urbandictionary.", name)
								if WEATHER_ENABLED:
									privsend("%weather <location> -=- get the current weather for <location>", name)
									privsend("%forecast <location> -=- get the weather forecast for <location>", name)
								if QR_ENABLED: privsend("%qr <url> -=- supply a url to a qr code image and ill try to see what it says",name)
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
								if LOGLEVEL >= 1: log("Sent help to {0}".format(name))
							if len(info) > 1 and info[1].strip('\r\n').lower() == 'ping' and TELEGRAM_ENABLED:
								privsend("%ping <user> <message>",name)
								privsend("this sends a message to a specified user via telegram. telegram will notify a users phone when it receives a message.",name)
								privsend("if you want to be able to be pinged, download the telegram app on your phone and send \"/addme {0}\" to @gr3ybot.",name)
								privsend("----------------------",name)
								privsend("<user> - someone in chat.",name)
								privsend("<message> - optional. can be any message.",name)
								privsend("----------------------",name)
								privsend("PING SELF COMMANDS AND REMINDERS",name)
								privsend("%ping me <message>",name)
								privsend("ping yourself with an optional message.",name)
								privsend("----------------------",name)
								privsend("<message> - optional. can be any message.",name)
								privsend("----------------------",name)
								privsend("%ping me when <name> <command>",name)
								privsend("set yourself a ping reminder",name)
								privsend("----------------------",name)
								privsend("<name> - the username of someone else in chat.",name)
								privsend("<command> - commands could be the following:",name)
								privsend(" -> 'is alive' - sends you a ping when <name> unidles in chat.",name)
								privsend(" -> 'joins' - sends you a ping when <name> joins the chat.",name)
								privsend("example: %ping me when bgm is alive",name)
								privsend("this will send you a ping when bgm unidles in chat.",name)
								privsend("----------------------",name)
							if len(info) > 1 and info[1].strip('\r\n').lower() == 'reminders':
								privsend("%remindme/%remind me <timeframe> - <message>",name)
								privsend("set yourself a reminder for some time	to do something. when the time comes, youll be notified in here 3 different ways, and if you have pings",name)
								privsend("enabled, it will send you a notification to your phone. due to the way irc sockets are handled, the reminder may be off by a minute or two, so",name)
								privsend("dont use it as a cooking timer unless you mind a few minutes extra cooking. check out how to set up pings if youre interested in this.",name)
								privsend("----------------------",name)
								privsend("<timeframe> - make it plain english. examples: %remindme in five minutes, %remindme on the second tuesday of march, %remindme 9/1/16, etc",name)
								privsend("<message> - message is required, and must be separated from the <timeframe> by a single dash (-).",name)

						# OVERLORD
						if (info[0].lower() in overlord_keywords):
							sender = getNick(data)
							afile = open('overlord.txt', 'rb')
							line = rline(afile)
							afile.close()
							send("when i am an evil overlord, {0}".format(line),getChannel(data)) if special == 0 else privsend("when i am an evil overlord, {0}".format(line),sender)
							if LOGLEVEL >= 1: log("Overlord: {0}".format(line))
		
						# MEMOS
						if (info[0].lower() in memo_keywords):
							#--
							# This is the Memos feature.  It allows a user to set a memo for another inactive user.
							# It stores the memo in an external file.
							# When the target user becomes active again, it sends the memo from the file and then
							# deletes the line so it never resends.  The message sending is handles at the very
							# bottom of this script.  This is just to set the memo:
							#--
							if special == 1: name = getNick(data); privsend("you can only leave a memo in a public channel.  try this in {0}".format(defchannel),name); continue
							message = info[1:]
							fromnick = getNick(data)
							try:
								tellnick = message[0]
							except IndexError:
								send("{0} you dickmunch you need to specify a person".format(fromnick),getChannel(data))
								continue
							if tellnick.lower() == botname.lower():
								send("why would i want to leave myself a memo tho",getChannel(data))
								continue
							if tellnick.lower() == fromnick.lower():
								send("ok sure thing.",getChannel(data))
								time.sleep(3)
								send("hey {0}, {1} says youre an idiot.".format(fromnick,botname.lower()),getChannel(data))
								continue
							try:
								message = " ".join(message[1:])
								message = message.translate(None, "\t\r\n")
								message = message.encode("utf-8")
							except IndexError:
								send("{0} get some %help.  actually, learn to read first, then get some %help.".format(fromnick),getChannel(data))
								time.sleep(.1)
								continue
							if not message: 
								send("{0} get some %help.  actually, learn to read first, then get some %help.".format(fromnick),getChannel(data))
								time.sleep(.1)
								continue
							q = con.db.cursor()
							q.execute("""
								INSERT INTO Memos (fromUser,toUser,message,dateTime) VALUES (?, ?, ?, ?) """, (fromnick,tellnick,unicode(message),time.time()))
							con.db.commit()
							if LOGLEVEL >= 1: log("{0} says \"Tell {1} {2}\"".format(fromnick, tellnick, message))
							send("ok ill tell {0} that you hate everything about them forever.".format(tellnick),getChannel(data))
		
						# GOOGLE SEARCH
						if info[0].lower() == 'g' and GOOGLE_ENABLED:
							try:
								term = info[1:]
							except:
								continue
							term = " ".join(term)
							term = "".join(c for c in term if c not in ('\n','\r','\t')).split(" ")
							if len(term) == 0:
								# ADD QUIP HERE
								continue
							send("sec",getChannel(data),s=special,u=getNick(data))
							if "-f" in term or "-first" in term:
								term = " ".join(w for w in term if (w != "-f" and w != "-first"))
								res = retFirstResult(term)
								if res == "~*403":
									send("how about you google {0} for yourself".format(term),getChannel(data),s=special,u=getNick(data))
									continue
								send("first result: '{0}' -- {1}".format(res["title"],res["url"]),getChannel(data),s=special,u=getNick(data))
								if len(res["blob"]) > 0:									
									send("'{0}'".format(res["blob"][:490]),getChannel(data),s=special,u=getNick(data))						
							elif "-r" in term or "-random" in term or "-rand" in term:
								term = " ".join(w for w in term if (w != "-r" and w != "-random" and w != "-rand"))
                                                                res = retRandomResult(term)
                                                                if res == "~*403":
                                                                        send("how about you google {0} for yourself".format(term),getChannel(data),s=special,u=getNick(data))
                                                                        continue
                                                                send("i randomly gave you result number {2}: '{0}' -- {1}".format(res["title"],res["url"],res["resNum"]),getChannel(data),s=special,u=getNick(data))
                                                                if len(res["blob"]) > 0:
                                                                        send("'{0}'".format(res["blob"][:490]),getChannel(data),s=special,u=getNick(data))	
							else:
								term = " ".join(w for w in term)
								res = retResults(term)
								if res == "~*403":
									send("how about you google {0} for yourself".format(term),getChannel(data),s=special,u=getNick(data))
									continue
								for i in res:
									send("'{0}' -- {1}".format(res[i]["title"],res[i]["url"]),getChannel(data),s=special,u=getNick(data))
				
						# ROLL DICE
						if info[0].lower() == 'roll':
							try:
								totalroll = info[1]
							except:
								if special == 0: send("you need to specify a roll, like d20 or 2d10 or something.",getChannel(data))
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
								sides =	int(totalroll[1].strip('\r\n'))
							except:
								if special == 0: send("you need to specify the amount of sides, like d20 or d10",getChannel(data))
								else: usernick = getNick(data); privsend("you need to specify the amount of sides, like d20 or d10",usernick)
								continue
							if rolls < 1: 
								if special == 0: send("im assuming you want at least one roll",getChannel(data))
								else: usernick = getNick(data); privsend("im assuming you want at least one roll",usernick)
								rolls = 1
							if sides < 1:
								if special == 0: send("ok let me just break the space-time continuum for you.",getChannel(data))
								else: usernick = getNick(data); privsend("ok let me just break the space-time continuum for you.")
								continue
							equation = []
							total = 0
							try:
								if rolls < 1000:
									for i in range(0,rolls):
										roll = (xOrShift() % sides) + 1
										total = total + roll
										if rolls < 20 and rolls > 1: equation.append(roll)
								else:
									send("im not smart enough to do that. go here: http://www.wolframalpha.com/input/?i=roll%201%20{1}-sided%20dice%20{2}%20times".format(sides,rolls))
									continue
								if rolls >= 20: equation = "thats too many numbers for my digital fingers to type. just trust me that this is the total roll: {0}".format(total)
								elif rolls > 1: 
									lowest=equation[(equation.index(min(equation)))]
									if '-nolow' in printlow: equation[(equation.index(min(equation)))] = '({0})'.format(equation[(equation.index(min(equation)))])
									equation = " + ".join(map(str, equation))
									equation = '{0} = {1}'.format(equation,total)
									if '-nolow' in printlow: equation = '{0}. without the lowest roll: {2} - {3} = {1}'.format(equation,total-int(lowest),total,int(lowest))
								elif rolls == 1: equation = "heres your roll: {0}".format(total)
								if special == 0: send(equation,getChannel(data))
								else: usernick = getNick(data); privsend(equation,usernick)
							except Exception as e:
								if special == 0: send("lets just say you rolled a natural 20",getChannel(data))
								else: usernick = getNick(data); privsend("lets just say you rolled a natural 20", usernick)
								if LOGLEVEL >= 1: log("ERROR: Couldn't display dice roll: {}".format(str(e)))
								continue
					
						# GET A TWITTER FEED
						if (info[0].lower() in showtwitter_keywords and info[0].lower() != "tweet") and TWITTER_ENABLED:
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
								except (Exception, tweepy.error.TweepError) as e:
									if LOGLEVEL >= 1: log("Tweepy error: {0}".format(str(e)))
									#sendPing('Gr3yBot','bgm','Gr3ybot Error.  Check logs for more info: {0}'.format(str(e)))
									if e.message[0]['code'] == 88:
										send("im making too many calls to twitter and the twitter hates when i do that.  try again later.",getChannel(data))
									continue
								send("lets see what one of my followers, {0}, is doing on twitter...".format(fol),getChannel(data))
								time.sleep(1)
								mag = getTweet(fol)
								for tweet in mag:
									try: # Is the message a retweet?  Let's grab it and specify that it's an RT
										mag = tweet.retweeted_status.text
										getrt = tweet.text.split('@')[1].split(':')[0]
										mag = "RT @{0}: {1}".format(getrt,mag)									
									except AttributeError as e:
										if LOGLEVEL >= 1: log("Non-fatal issue with tweet: {0}".format(str(e)))
										mag = tweet.text
									fol = fol.encode('utf-8')
									send("@{0} >> {1}".format(fol,mag),getChannel(data))
									if LOGLEVEL >= 1: log("@{0} >> {1}".format(fol,mag))
									send("follow {} to get your tweets in here".format(twittername),getChannel(data))
								continue
							tweetnick = "".join(c for c in tweetnick if c not in ('@','\r', '\n', '\t')) # Strip any weird formatting in the user name.  Yes, this is a thing that happens.
							msg = getTweet(tweetnick)
							if LOGLEVEL >= 1: log("Twitter Handle: @{0}".format(tweetnick))
							if msg == "-*404":
								send("that person doesnt really exist tho",getChannel(data))
								if LOGLEVEL >= 1: log("Doesn't Exist")
								continue
							if msg == "-*501":
								send("@{0}'s profile is private and bigoted and hates me because they wont let me follow them, so i cant see their tweets".format(tweetnick),getChannel(data))
								if LOGLEVEL >= 1: log("Not Authorized")
								continue
							if len(msg) == 0:
								send("@{0} doesnt have no tweets yet".format(tweetnick),getChannel(data))
								if LOGLEVEL >= 1: log("Doesn't have any tweets")
								continue
							for tweet in msg:
								try:
									msg = tweet.retweeted_status.text
									getrt = tweet.text.split('@')[1].split(':')[0]
									msg = "RT @{0}: {1}".format(getrt,msg)
								except (AttributeError, UnicodeEncodeError) as e:
									if LOGLEVEL >= 1: log("Non-fatal issue with tweet: {0}".format(str(e)))
									msg = tweet.text
								tweetnick = tweetnick.encode('utf-8')
								send("@{0} >> {1}".format(tweetnick,msg),getChannel(data))
								if LOGLEVEL >= 1: log("@{0} >> {1}".format(tweetnick, msg))
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
								send("you need to actually tweet something",getChannel(data)) if special == 0 else privsend("you need to actually tweet something",sender)
								continue
							if len(q) == 0:
								send("you didnt tweet anything dumby",getChannel(data)) if special == 0 else privsend("you didnt tweet anything dumby",sender)
								continue
							if q[0] == '%overlord\r\n':	# Did the user want to tweet an overlord quote?
								afile = open('overlord.txt', 'rb')
								q = "{0}".format(rline(afile))
							else:
								q = " ".join(q)
							q = "{0}: {1}".format(fromnick,q)
							q = (q[:137] + '...') if len(q) > 140 else q
							if postTweet(q) == "DUPLICATE":
								send("you already said that dummy",getChannel(data))
								continue 
							if LOGLEVEL >= 1: log("{0} tweeted: {1}".format(fromnick, q))
							person = getRandomPerson(getChannel(data))
							send("ok i tweeted that. i hope i didnt sound like {0}.".format(person),getChannel(data)) if special == 0 else privsend("ok i tweeted that i hope i didnt sound like you",sender)
							time.sleep(1)

						# SET A REMINDER
						if (info[0].lower() in reminder_keywords):
							if len(info) < 3 or "-" not in info:
								if special == 0: send("ok so %help reminders is probably more your thing.",getChannel(data))
								else: usernick = getNick(data); privsend("ok so %help reminders is probably more your thing.",usernick)
								continue							
							try:
								if info[0].lower() == 'remind' and info[1].lower() != 'me':
									if special == 0: send("you might want to check %help reminders",getChannel(data))
									else: usernick = getNick(data); privsend("you might want to check %help reminders",usernick)
									continue
							except:
								if special == 0: send("ok so %help reminders is probably more your thing.",getChannel(data))
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
								if special == 0: send("heres your reminder: 1) learn to read, 2) read %help",getChannel(data),tell=True)
								else: usernick = getNick(data); privsend("heres your reminder: 1) learn to read, 2) read %help",usernick)
								continue
							message = " ".join(message)
							try:
								reminddate = message.split('-',1)[0].strip()
								message = message.split('-',1)[1:]
							except:
								if special == 0: send("did you put in a date for the reminder? %help reminders",getChannel(data))
								else: usernick = getNick(data); privsend("did you put in a date for the reminder? %help reminders",usernick)
								continue
							message = " ".join(message)
							try:
								reminddate = cal.parse(reminddate)
							except:
								if special == 0: send("did you put in a date for the reminder? %help reminders",getChannel(data))
								else: usernick = getNick(data); privsend("did you put in a date for the reminder? %help reminders",usernick)
								continue
							try:
								checkdate = datetime.datetime.fromtimestamp(time.mktime(reminddate[0]))
							except OverflowError:
								if special == 0: send("no youll be dead by then",getChannel(data))
								else: usernick = getNick(data); privsend("no youll be dead by then",usernick)
								continue
							timefloat = time.mktime(reminddate[0])
							if timefloat <= time.time():
								if special == 0: send("ok let me just go hop in my time machine",getChannel(data))
								else: usernick = getNick(data); privsend("ok let me just go hop in my time machine",usernick);
								continue
							try:
								reminddate = checkdate
							except:
								if special == 0: send("that doesnt make any sense.",getChannel(data))
								else: usernick = getNick(data); privsend("that doesnt make any sense",usernick)
								continue

							q = con.db.cursor()
							q.execute("""
								SELECT * FROM Reminders WHERE user = ? """, (getNick(data),))
							thisline = q.fetchone()
							try:
								if timefloat < float(thisline[2]) < timefloat + 30.0:
									if special == 0: send("are you reminding me to remind you or do you have short-term memory loss?",getChannel(data))
									else: usernick = getNick(data); privsend("are you reminding me to remind you or do you have short-term memory loss?")
									alreadyset = 1
									continue
								if time.time() < float(thisline[4]) + 120.0:
									if special == 0: send("hey calm down with the reminders, guy",getChannel(data))
									else: usernick = getNick(data); privsend("hey calm down with the reminders, guy",usernick)
									alreadyset = 1
									continue
							except:
								alreadyset = 0
								
	
							if alreadyset == 0:
								if LOGLEVEL >= 1: log("{0} set a reminder for {1}: {2}".format(getNick(data),reminddate.strftime("%m/%d/%y %H:%M:%S"),message.lstrip()))
								q.execute("""
									INSERT INTO Reminders (user, atTime, message, dateTime) VALUES (?, ?, ?, ?) """, (getNick(data), timefloat, message.lstrip().strip('\r\n'), time.time()))
								if special == 0: send("k reminder set for {0}".format(reminddate.strftime("%m/%d/%y %H:%M:%S")),getChannel(data))
								else: usernick = getNick(data); privsend("k reminder set for {0}".format(reminddate.strftime("%m/%d/%y %H:%M:%S")),usernick)

						# LAST SEEN
						if (info[0].lower() == 'seen'):
							actChan = getChannel(data)
							try:
								who = info[1].rstrip()
							except:
								send("you gotta specify a name sister",actChan)
								continue
							if who.lower() == botname.lower():
								send("im here now",actChan)
								continue
							q = con.db.cursor()
							q.execute("""
								SELECT Time,Channel,Msg FROM LastSeen WHERE User = ? """, (who,))
							ls = q.fetchone()
							try:
								localnow = datetime.datetime.now(timezone(LOCALTZ))
								send("i think i saw {0} active in {1} around {2} at {3}".format(who,ls[1].rstrip(),datetime.datetime.fromtimestamp(ls[0]).strftime("%b %d"),datetime.datetime.fromtimestamp(ls[0]).strftime("%-I:%M %p")),actChan)
								send("iirc, they said: {0}".format(ls[2]),actChan)
								continue
							except:
								send("i havent seen that bro(ette) yet.",actChan)
								continue
	
						# PING
						if info[0].lower() == 'ping' and TELEGRAM_ENABLED:
							try:
								touser = info[1]
							except:
								send("ping who now?",getChannel(data),False,special,getNick(data))
								continue
							touser = touser.strip('@')
							touser = touser.translate(None, "\t\r\n")
							if touser.lower() == "me":
								touser = getNick(data)
							if special == 1:
								for thing in info[2:]:						
									if thing[0] == "#":
										channicks = getChatters(chan=thing)
										info.remove(thing)
								try:
									channicks
								except:
									privsend("what channel tho",getNick(data))
									continue
							else:
								channicks = getChatters(chan=getChannel(data))
							for i in channicks:
								if touser.lower() in i.lower(): touser = i
							try:
								msg = " ".join(info[2:])
							except:
								msg = "alive?"
							msg = msg.strip('\r\n')
							q = con.db.cursor()
							if msg.split(' ')[0].lower() == "when" and (" ".join(msg.split(' ')[2:]).lower() == "is alive" or msg.split(' ')[2].lower() == "joins"):
								if msg.split(' ')[1] == touser or msg.split(' ')[1] == botname:
									send("dont be dumn",getChannel(data),False,special,getNick(data))
									continue
								else:
									found = 0
									compline = "{0}[-]{1}\n".format(touser,msg.split(' ')[1])
									q.execute("""
										SELECT * FROM Pings WHERE toUser = ? AND checkUser = ? """, (touser, msg.split(' ')[1]))
									checkPing = q.fetchone()
									try:
										checkPing[0]
										send("you already asked me to let you know when {0} stops being a chump.  go away".format(msg.split(' ')[1]),getChannel(data),False,special,getNick(data))
										found = 1
										continue
									except:
										pass

									if touser == getNick(data):
										if (" ".join(msg.split(' ')[2:]).lower() == "is alive"):
											channicks = getChatters(chan=getChannel(data))
											found = 0
											for i in channicks:
												if (msg.split(' ')[1].translate(None, "\t\r\n").lower() in i.lower()) and found == 0:
													q.execute("""
														INSERT INTO Pings (toUser, checkUser, quiet) VALUES (?, ?, ?) """, (touser, msg.split(' ')[1], special))
													con.db.commit()
													send("ok you got it boss",getChannel(data),False,special,getNick(data))
													found = 1
											if found == 0:
												send("i dont know who dat is",getChannel(data),False,special,getNick(data))
										else:
											channicks = getChatters(chan=getChannel(data))
											found = 0
											for i in channicks:
												if msg.split(' ')[1].translate(None, "\t\r\n").lower() in i.lower():
													send("that person already joined dumby. ill let you know when they arent idle instead",getChannel(data),False,special,getNick(data))
													found = 1
											if found == 0:
												send("ok you got it boss",getChannel(data),False,special,getNick(data))
												q.execute("""
                                                                                                                INSERT INTO Pings (toUser, checkUser, quiet) VALUES (?, ?, ?) """, (touser, msg.split(' ')[1], special))
                                                                                                con.db.commit()
											else:
												send("dont make me be the bad guy. you spam {0}s cell phone with your dumb requests.".format(touser),getChannel(data),False,special,getNick(data))
							else:	
								if not msg: msg = "alive?"
								message = sendPing(getNick(data),touser,msg)
								if message != "Sent!":
									send(message,getChannel(data),False,special,getNick(data))
									if LOGLEVEL >= 1: log("Error sending ping: {}".format(message))
									continue
								if LOGLEVEL >= 1: log("Ping request sent from: {0}, to: {1}, with this message: {2}".format(getNick(data),touser,msg))
								send("ok i pinged {0} for you now pay me $1.".format(touser),getChannel(data),False,special,getNick(data))
				
						# WIKIPEDIA
						if (info[0].lower() in wiki_keywords) and WIKIPEDIA_ENABLED:
							# the url to the article and other things to search for.
							#--
							sender = getNick(data)
							try:
								q = info[1:]
							except IndexError:
								send("whatchuwanna wiki, friend",getChannel(data)) if special == 0 else privsend("whatchuwanna wiki, friend",sender)
								continue
							q = " ".join(q)
							if LOGLEVEL >= 1: log("Wiki: {0}".format(q))
							result = wiki(q) # See wiki.py for more info on is and other wiki functions.
							if result == "-*e":
								send("that clearly doesnt exist",getChannel(data)) if special == 0 else privsend("that clearly doesnt exist",sender)
								continue
							if special == 0: send("ok one sec",getChannel(data))
							else: name = getNick(data); privsend("ok one sec",name)
							time.sleep(1)
							if result[0] == "-*d":
								if len(result) > 10:
									result = result[1:10]
									result.append("etc...")
								result = ", ".join(result)
								if special == 0:
									send("theres a lot of stuff you could mean by that.",getChannel(data))
									time.sleep(.5)
									send("stuff like: {0}".format(result),getChannel(data))
								else: 
									name = getNick(data)
									privsend("theres a lot of stuff you could mean by that.",name)
									time.sleep(.5)
									privsend("stuff like: {0}".format(result),name)
									continue
							else:					
								url = result[0]
								desc = result[1]
								try:
									search = result[2]
								except IndexError:
									search = 0
								time.sleep(.5)
								try:
									send(desc,getChannel(data)) if special == 0 else privsend(desc,sender)
								except:
									pass
								time.sleep(.5)
								try:
									send("more info here: {0}".format(url),getChannel(data)) if special == 0 else privsend("more info here: {0}".format(url),sender)
								except:
									pass
								if search != 0:
									search = "".join(a for a in search if (a.isalnum() or a in (",",".","'","\"","?","!","@","#","$","%","^","&","*","(",")","_","+","=","-","\\","|","]","}","{","[",";",":","/",">","<","`","~"," ")))
									time.sleep(1)
#									try:
#										send("see also: {0}".format(search),getChannel(data)) if special == 0 else privsend("see also: {0}".format(search),sender)
#									except:
#										pass
								if LOGLEVEL >= 1: log("{0}\nMore Info: {1}\nSee Also: {2}".format(desc,url,search))
						
						# FIGHT
						if info[0].lower() == 'fight':
							#--
							# This is the chat fight subroutine.
							#--
							if (SequenceMatcher(None, getChannel(data).lower(), fightchan.lower()).ratio() < 0.92) and special == 0:
								send("no we have a fight fightchan for this: /join {0}".format(fightchan),getChannel(data))
								continue
							channel = fightchan
							q = con.db.cursor()
							try:
								act = info[1:]
							except IndexError:
								name = getNick(data)
								q.execute("""
									SELECT * FROM FightsOngoing WHERE (playerOne = ? OR playerTwo = ?) """, (name, name))
								try:
									status = q.fetchone()
								except:
									fightsend("you arent fighting anyone right now. try typing %fight challenge {}.".format(getRandomPerson(fightchan)))
									continue
								if status[2] == 0 and status[0] == name:
									fightsend("you sent an invite to fight to {0}, but they havent accepted it yet.".format(status[1]))
									continue
								if status[2] == 0 and status[1] == name:
									fightsend("{} wants to fight you but you haven't replied.  Type %fight yes or %fight no to accept or decline the challenge.".format(status[0]))
									continue
								if status[2] == 1:
									fightsend("youre in a fight with {0} and its {1} turn.".format(status[1] if status[0] == name else status[0],"your" if status[3] == name else "their"))
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
                                                                q.execute("""
                                                                        SELECT * FROM FightsOngoing WHERE (playerOne = ? OR playerTwo = ?) """, (name, name))
                                                                status = q.fetchone()
								try:
									status[0]
                                                                except:
									someone = getRandomPerson(fightchan)
                                                                        fightsend("{}".format("you arent fighting anyone right now. try typing %fight challenge {}.".format(someone) if someone != "lonely" else "youre alone in this chat. get some friends"))
                                                                        continue
                                                                if status[2] == 0 and status[0] == name:
                                                                        fightsend("you sent an invite to fight to {0}, but they havent accepted it yet.".format(status[1]))
                                                                        continue
                                                                if status[2] == 0 and status[1] == name:
                                                                        fightsend("{} wants to fight you but you haven't replied.  Type %fight yes or %fight no to accept or decline the challenge.".format(status[0]))
                                                                        continue
                                                                if status[2] == 1:
                                                                        fightsend("youre in a fight with {0} and its {1} turn.".format(status[1] if status[0] == name else status[0],"your" if status[3] == name else "their"))
                                                                        continue
							except Exception as e:
								fightsend("i decided not to work today. i just let bgm know how lazy i am.")
								#sendPing("Gr3yBot","bgm",'Gr3ybot Error.  Check logs for more info: {0}'.format(str(e)))
								continue

							if act[0].lower() == "help":
								name = getNick(data)
								if LOGLEVEL >= 1: log("Helping out this guy with fighting: {0}".format(name))
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
									privsend("%fight stats (<name>) [-noitems] - get the stats of <name>, if no <name> specified, then get your own stats.  if you specify -noitems, then youll see the stats of the person without their equipped items",name)
									privsend("%fight cancel - cancel a fight. if the fight hasnt been accepted, theres no penalty, otherwise your opponent gets a win",name)
									privsend("------",name)
									privsend("heres some stuff about inventories:",name)
									privsend("%fight inventory <name> - list the inventory of <name>, if no <name> specified, then list your own inventory.",name)
									privsend("%fight (un)equip <ItemNumber> - equip or unequip <ItemNumber>.  you must have the item in your inventory to equip it.",name)
									privsend("%fight drop <ItemNumber> - drop an item.",name)
									privsend("------",name)
									privsend("theres additional help available by typing one of the following commands:",name)
									privsend("%fight help actions - get more info on what each fight action does",name)
									privsend("%fight help stats - get more info on what each stat does",name)
									continue

							elif act[0].lower() == "inventory":
								try:
									checkPerson = act[1]
								except:
									checkPerson = getNick(data)
								person = getNick(data)
								inventory = getInventory(checkPerson)
								equippedItems = getEquipment(checkPerson)
								if inventory == False and equippedItems == False: 
									fightsend("{} pockets are empty. maybe fighting more will fill them up".format(checkPerson + '\'s' if checkPerson != person else "your")) if special == 0 else privsend("{} pockets are empty. maybe fighting more will fill them up".format(checkPerson + '\'s' if checkPerson != person else "your"),person)
									continue
								if special == 0: fightsend("k check your pms")
								privsend("{} equipped items:".format(checkPerson + '\'s' if checkPerson != person else "your"),person)
								if equippedItems == False: privsend("none",person)
								else:
									weapon = getItemByItemNo(equippedItems[0])
									armor = getItemByItemNo(equippedItems[1])
									boot = getItemByItemNo(equippedItems[2])
									acc1 = getItemByItemNo(equippedItems[3])
									acc2 = getItemByItemNo(equippedItems[4])
									privsend("weapon: {0} (atk: {1} || def: {2} ||  magatk: {3} || magdef: {4} || hp gain: {5}). --== {6}. ==-- Item number: {7}".format(weapon[1],weapon[3],weapon[4],weapon[5],weapon[6],weapon[7],weapon[8],weapon[0]),person) if weapon != False else privsend("weapon: none",person)
									privsend("armor: {0} (atk: {1} || def: {2} ||  magatk: {3} || magdef: {4} || hp gain: {5}). --== {6}. ==-- Item number: {7}".format(armor[1],armor[3],armor[4],armor[5],armor[6],armor[7],armor[8],armor[0]),person) if armor != False else privsend("armor: none",person)
									privsend("boots: {0} (atk: {1} || def: {2} ||  magatk: {3} || magdef: {4} || hp gain: {5}). --== {6}. ==-- Item number: {7}".format(boot[1],boot[3],boot[4],boot[5],boot[6],boot[7],boot[8],boot[0]),person) if boot != False else privsend("boots: none",person)
									privsend("accessory 1: {0} (atk: {1} || def: {2} ||  magatk: {3} || magdef: {4} || hp gain: {5}). --== {6}. ==-- Item number: {7}".format(acc1[1],acc1[3],acc1[4],acc1[5],acc1[6],acc1[7],acc1[8],acc1[0]),person) if acc1 != False else privsend("accessory 1: none",person)
									privsend("accessory 2: {0} (atk: {1} || def: {2} ||  magatk: {3} || magdef: {4} || hp gain: {5}). --== {6}. ==-- Item number: {7}".format(acc2[1],acc2[3],acc2[4],acc2[5],acc2[6],acc2[7],acc2[8],acc2[0]),person) if acc2 != False else privsend("accessory 2: none",person)
								privsend("{} unequipped items:".format(checkPerson + '\'s' if checkPerson != person else "your"),person)
								if inventory is None: privsend("none",person)
								for thing in inventory.split(','):
									if len(thing.rstrip()) == 4:
										item = getItemByItemNo(thing.rstrip())
										privsend("--== {0} ==-- (atk: {1} || def: {2} || magatk: {3} || magdef: {4} || hp gain: {5}). --== {6}. ==-- Item number: {7}".format(item[1],item[3],item[4],item[5],item[6],item[7],item[8],item[0]),person)
								if checkPerson == person: privsend("To (un)equip an item, type %fight (un)equip <ItemNumber> so like: %fight equip 0669 or %fight unequip 2129",person)

							elif act[0].lower() == "equip":
								person = getNick(data)
								if getIsFighting(person) == 1: 
									fightsend("you cant equip stuff while youre fighting") if special == 0 else privsend("you cant equip stuff while youre fighting",person)
									continue
								try:
									itemNum = act[1]
								except:
									fightsend("what item do you want to equip.  do %fight inventory to see your inventory") if special == 0 else privsend("what item do you wanna equip.  do %fight inventory to see your inventory",person)
									continue
								out = equipItem(person,itemNum)
								item = getItemByItemNo(itemNum)
								if special == 0:
									if out == 2: fightsend("um i dont think you have that item")
									if out == 1: fightsend("ok your {} is equipped".format(item[1]))
									if len(str(out)) == 5:
										oldItem = getItemByItemNo(str(out)[1:5])
										fightsend("ok i equipped the {0}, but i had to unequip the {1} first".format(item[1],oldItem[1]))
									if out == 3: fightsend("you already have 2 accessories equipped.  unequip one of them first")
								if special == 1:
									if out == 2: privsend("um i dont think you have that item",person)
                                                                        if out == 1: privsend("ok your {} is equipped".format(item[1]),person)
                                                                        if len(str(out)) == 5:
                                                                                oldItem = getItemByItemNo(str(out)[1:5])
                                                                                privsend("ok i equipped the {0}, but i had to unequip the {1} first".format(item[1],oldItem[1]),person)
                                                                        if out == 3: privsend("you already have 2 accessories equipped.  unequip one of them first",person)
								continue

							elif act[0].lower() == "unequip":
                                                                person = getNick(data)
								if getIsFighting(person) == 1:
                                                                        fightsend("you cant unequip stuff while youre fighting") if special == 0 else privsend("you cant unequip stuff while youre fighting",person)
                                                                        continue									
                                                                try:
                                                                        itemNum = act[1]
                                                                except:
                                                                        fightsend("what item do you want to unequip.  do %fight inventory to see your inventory") if special == 0 else privsend("what item do you wanna unequip.  do %fight inventory to see your inventory",person)
                                                                        continue
                                                                out = unequipItem(person,itemNum)
								item = getItemByItemNo(itemNum)
                                                                if special == 0:
                                                                        if out == 1: fightsend("ok the {} was unequipped".format(item[1]))
                                                                        if out == 2: fightsend("i dont think you have anything equipped yet")
                                                                        if out == 3: fightsend("you dont have anything equipped in that slot")
									if out == 4: fightsend("you dont have {} equipped".format(item[1]))
									if out == 5: fightsend("you dont even have an inventory tho")
                                                                if special == 1:
									if out == 1: privsend("ok the {} was unequipped".format(item[1]),person)
                                                                        if out == 2: privsend("i dont think you have anything equipped yet",person)
                                                                        if out == 3: privsend("you dont have anything equipped in that slot",person)
                                                                        if out == 4: privsend("you dont have {} equipped".format(item[1]),person)
									if out == 5: privsend("you dont even have an inventory tho",person)
                                                                continue

							elif act[0].lower() == "drop":
								person = getNick(data)
								if getIsFighting(person) == 1:
									fightsend("you cant drop anything while youre fighting") if special == 0 else privsend("you cant drop anything while youre fighting",person)
									continue
								try:
									itemToDrop = act[1]
								except:
									itemToDrop = None
								out = dropItem(person,itemToDrop)
								if out == 0: 
									if LOGLEVEL >= 1: log("Something went wrong when attempting to drop an item. Error: {}".format(out))
								if out == 1:
									fightsend("ok i took that item away from you.") if special == 0 else privsend("ok i took that item away from you",person)
								if str(out).startswith('2'):
									item = getItemByItemNo(str(out)[1:5])
									fightsend("ok i got rid of the {} for you".format(item[1])) if special == 0 else privsend("ok i got rid of the {} for you".format(item[1]),person)
								if out == 3:
									fightsend("you dont have that item") if special == 0 else privsend("you dont have that itme",person)
								if out == 4:
									if LOGLEVEL >= 1: log("Something went wrong when attempting to drop an item. Error: {}".format(out))
								if out == 5:
									if LOGLEVEL >= 1: log("Something went wrong when attempting to drop an item. Error: {}".format(out))
								if out == 6:
									fightsend("what do you want to drop?") if special == 0 else privsend("what do you want to drop?",person)
								if str(out).startswith('7'):
									item = getItemByItemNo(str(out)[1:5])
									fightsend("ok its gone and i added the {} to your inventory".format(item[1])) if special == 0 else privsend("ok its gone and i added the {} to your inventory".format(item[1]),person)

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
									if LOGLEVEL >= 1: log("Created a fighting statsheet for {}".format(fighter))
								else:
									if LOGLEVEL >= 1: log("Specs for {0}:\n{1}".format(fighter,checkStats))
								readytofight = 1
								try:
									challenger = act[1]
								except IndexError:
									fightsend("you need to specify a challenger dumny")
									continue
								if challenger.lower() == botname.lower(): fightsend("im more of a lover than a fighter"); continue
								if challenger.lower() == fighter.lower(): fightsend("no masochism allowed in chat thats like rule 3 or something."); continue
								channicks = getChatters(chan=fightchan)
								if not channicks: 
									time.sleep(2)
									channicks = getChatters(chan=fightchan)
								if not channicks:
									fightsend("hold on the irc server is being a dick and something errored on the back end.  try again later.")
									continue
								i = 0
								for j in channicks:
									if challenger.translate(None, "\t\r\n").lower() == j.translate(None, "\t\r\n").lower(): i += 1
								if i == 0: 
									fightsend("i dont kno who that is")
									continue
								q = con.db.cursor()
								q.execute("""
									SELECT * FROM FightsOngoing WHERE (playerOne = ? OR playerTwo = ? OR playerOne = ? OR playerTwo = ?) """, (fighter, fighter, challenger, challenger))
								ogFight = q.fetchone()
								try: 
									if ogFight[0].lower() == fighter.lower():
										if ogFight[2] == 1:
											fightsend("youre already fighting {0}. go finish that fight ok bye".format(who))
                                                                                        readytofight = 0
                                                                                        break
                                                                                else:
                                                                                	fightsend("you have to wait for {0} to accept your other fight before starting a new one".format(who))
                                                                                        readytofight = 0
                                                                                        break
									if ogFight[1].lower() == fighter.lower():
										if int(accepted) == 1:
                                                                                        fightsend("youre already fighting {0}. go finish that fight ok bye".format(initiator))
                                                                                        readytofight = 0
                                                                                        break
                                                                                else:
                                                                                        fightsend("{0} has already challenged you to a fight. if you accept this challenge type %fight yes, if you dont, type %fight no".format(initiator))
                                                                                        readytofight = 0
                                                                                        break
									if ogFight[0].lower() == challenger.lower() or ogFight[1].lower() == challenger.lower():
										fightsend("everyone hates {0} and theyre already in a fight so wait your turn".format(challenger))
                                                                                readytofight = 0
                                                                                break

								except:
									pass

								if readytofight == 1:
									q = con.db.cursor()
									q.execute("""
										INSERT INTO Memos (fromUser,toUser,message,dateTime) VALUES (?, ?, ?, ?) """, (fighter,challenger,"Wanna fight?  Come to {0} and type %fight yes or %fight no".format(fightchan),time.time()))
	
									q.execute("""
										SELECT * FROM FightsOngoing WHERE (playerOne = ? OR playerTwo = ?)""", (getNick(data), getNick(data)))
									alreadyFighting = q.fetchone()
									try:
										fightsend("youre already fighting {0} and it's {1} turn.".format(alreadyFighting[0] if getNick(data) != alreadyFighting[0] else alreadyFighting[1],"their" if alreadyFighting[3] != getNick(data) else "your"))
										con.db.rollback()
										continue
									except:
										q.execute("""
											INSERT INTO FightsOngoing (playerOne,playerTwo,accepted,whoseTurn,turnTotal,lastAction,stopper) VALUES (?, ?, 0, ?, 0, ?, ?) """, (fighter, challenger, challenger, time.time(), ''))
										con.db.commit()

										fightsend("ok i will ask {0} to accept your challenge.  i wanna see blood gais".format(challenger))

							elif act[0].lower() == "rematch":
								fighter = getNick(data)
								foundamatch = 0
								readytofight = 1
								q = con.db.cursor()
								q.execute("""
									SELECT lastFought FROM Fighters where name = ? """, (fighter,))
								try:
									rematch = q.fetchone()[0]
								except:
									fightsend("idk who you last fight go talk to a historyan or something")
									continue

								q = con.db.cursor()
                                                                q.execute("""
                                                                        SELECT * FROM FightsOngoing WHERE (playerOne = ? OR playerOne = ? OR playerTwo = ? OR playerTwo = ?) """, (fighter, rematch, fighter, rematch))
                                                                ogFight = q.fetchone()
                                                                try:
                                                                        if ogFight[0].lower() == fighter.lower():
                                                                                if ogFight[2] == 1:
                                                                                        fightsend("youre already fighting {0}. go finish that fight ok bye".format(rematch))
                                                                                        readytofight = 0
                                                                                        break
                                                                                else:
                                                                                	fightsend("you have to wait for {0} to accept your other fight before starting a new one".format(rematch))
                                                                                        readytofight = 0
                                                                                        break
                                                                        if ogFight[1].lower() == fighter.lower():
                                                                                if int(accepted) == 1:
                                                                                        fightsend("youre already fighting {0}. go finish that fight ok bye".format(rematch))
                                                                                        readytofight = 0
                                                                                        break
                                                                                else:
                                                                                	fightsend("{0} has already challenged you to a fight. if you accept this challenge type %fight yes, if you dont, type %fight no".format(rematch))
                                                                                        readytofight = 0
                                                                                        break
                                                                        if ogFight[0].lower() == rematch.lower() or ogFight[1].lower() == rematch.lower():
                                                                                fightsend("everyone hates {0} and theyre already in a fight so wait your turn".format(rematch))
                                                                                readytofight = 0
                                                                                break

								except:
									pass

                                                                if readytofight == 1:
                                                                        q = con.db.cursor()
                                                                        q.execute("""
                                                                                INSERT INTO Memos (fromUser,toUser,message,dateTime) VALUES (?, ?, ?, ?) """, (fighter,rematch,"Wanna fight?  Come to {0} and type %fight yes or %fight no".format(fightchan),time.time()))
                                                                        con.db.commit()

                                                                        q.execute("""
                                                                                INSERT INTO FightsOngoing (playerOne,playerTwo,accepted,whoseTurn,turnTotal,lastAction,stopper) VALUES (?, ?, 0, ?, 0, ?, ?) """, (fighter, rematch, rematch, time.time(), ''))
                                                                        con.db.commit()

                                                                        fightsend("ok i will ask {0} to accept your challenge.  i wanna see blood gais".format(rematch))
									foundamatch = 1
								if foundamatch == 0:
									fightsend("um, did you ever fight before because i dont even know who you are. %fight help")

							elif act[0].lower() == "yes":
								# Let's make sure this person has a spec sheet now...
								challenger = getNick(data)
								checkStats = getFighterStats(challenger)
								winner = "test"
								if not checkStats or checkStats is False:
									setFighterStats(fname=challenger)
									if LOGLEVEL >= 1: log("Created a fighting statsheet for {}".format(challenger))
								else:
									if LOGLEVEL >= 1: log("Stats for {0}:\n{1}".format(challenger,checkStats))
	
								q = con.db.cursor()
								q.execute("""
									SELECT * FROM FightsOngoing WHERE playerOne = ? OR playerTwo = ? """, (challenger,challenger))
								stopFight = q.fetchone()
								try:
									initiator = stopFight[0]
									opponent = stopFight[1]
									who = stopFight[3]
									accepted = stopFight[2]
									stopper = stopFight[6]
								except:
									continue
								try:
									stopper.lower()
								except:
									fightsend("yes what")
									continue
								if opponent.lower() == stopper.lower(): winner = initiator
								if initiator.lower() == stopper.lower(): winner = opponent
								if (stopper and stopper.lower() == challenger.lower()) and int(accepted) == 1:
									q.execute("""
										DELETE FROM FightsOngoing WHERE playerOne = ? or playerTwo = ? """, (challenger, challenger))
									con.db.commit()
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
										for i in results: privsend(i,winner)
										privsend("here are your new stats:",winner)
										privsend("level: {0}, attack: {1}, guard: {2}".format(newstats[1],newstats[2],newstats[3]),winner)
										privsend("magic attack: {0}, magic guard: {1}, total hp: {2}".format(newstats[4],newstats[5],newstats[6]),winner)
										privsend("xp to next level: {0}, total wins: {1}".format(newstats[7],newstats[8]),winner)
										setFighterStats(fname=winner,atksincelvl=0,satksincelvl=0,fatksincelvl=0,magatksincelvl=0,grdsincelvl=0,mgrdsincelvl=0)
									continue
								if (stopper and stopper.lower() != challenger.lower()) and (opponent.lower() == challenger.lower() or initiator.lower() == challenger.lower()) and int(accepted) == 1:
									fightsend("no you dont get to choose this.  this is between me and {0}".format(winner))
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
									q.execute("""
										UPDATE FightsOngoing SET playerOne = ?, playerTwo = ?, accepted = 1, whoseTurn = ?, turnTotal = 1, lastAction = ?, stopper = ? WHERE playerOne = ? or playerTwo = ? """, (initiator,who,whofirst,time.time(),stopper,challenger,challenger))
									con.db.commit()
									fightsend("ok cool, i randomly pick {0} to go first. type %fight help actions if you dont know what to do".format(whofirst))

							elif act[0].lower() == "no" or act[0].lower() == "cancel" or act[0].lower() == "stop" or act[0].lower() == "quit":
								q = con.db.cursor()
								q.execute("""
									SELECT * FROM FightsOngoing WHERE playerOne = ? or playerTwo = ? """, (getNick(data), getNick(data)))
								gotFight = q.fetchone()
								try:
									gotFight[0]
								except:
									fightsend("are you fighting anyone tho")
									continue
								else:
									if gotFight[0] == getNick(data): oppo = gotFight[1]
									else: oppo = gotFight[0]
									if gotFight[2] == 0:
										fightsend("wow youre boring. ok then")
										q.execute("""
											DELETE FROM FightsOngoing WHERE (playerOne = ? or playerTwo = ?) AND accepted = 0 """, (getNick(data), getNick(data)))
										con.db.commit()
									elif act[0].lower() != "no" and gotFight[2] == 1 and (not gotFight[6] or gotFight[6] is None):
										fightsend("what seriously?  if you stop the fight now {0} will still get full credit for winning. are you sure you want to stop? %fight yes or %fight no".format(oppo))

										q.execute("""
											UPDATE FightsOngoing SET stopper = ? WHERE playerOne = ? or playerTwo = ? """, (getNick(data),getNick(data),getNick(data)))
										con.db.commit()
										continue
									elif act[0].lower() != "no" and gotFight[2] == 1 and (gotFight[6] and gotFight[6] != getNick(data)):
										fightsend("{0} is already trying to give you a victory, just shh ok?".format(gotFight[6]))
									elif act[0].lower() == "no" and (gotFight[6] and gotFight[6] == getNick(data)):
										fightsend("stop flip floppin like a politician")
										q.execute("""
											UPDATE FightsOngoing SET stopper = NULL WHERE playerOne = ? or playerTwo = ? """, (getNick(data),getNick(data)))
										con.db.commit()
									elif act[0].lower() == "no" and (gotFight[6] and gotFight[6] != getNick(data)):
										fightsend("no you dont get a say in this.")
									else:
										continue

							elif act[0].lower() == "stats":
								noitems = False
								try:
									whostats = act[1]
									if whostats == "-noitems":
										try:
											whostats = act[2]
											noitems = True
										except:
											whostats = getNick(data)
											noitems = True
								except IndexError:
									whostats = getNick(data)
									try:
										if act[2] == "-noitems":
											noitems = True
									except:
										noitems = False
								if noitems == False: checkStats = getFighterStats(whostats) 
								else: checkStats = getFighterStats(whostats,True)
								if not checkStats or checkStats is False:
									fightsend("that person doesnt have a statsheet yet because they are a coward or idle.  probably a coward.")
									continue
								else:
									fightsend("stats for {0}:".format(whostats)) if special == 0 else privsend("stats for {0}:".format(whostats),getNick(data))
									fightsend("lvl: {0}, atk: {1}, grd: {2}, mag: {3}, mdef: {4}, hp: {5}, xp to next lvl: {6}, wins: {7}".format(checkStats[1],checkStats[2],checkStats[3],checkStats[4],checkStats[5],checkStats[6],checkStats[7],checkStats[8])) if special == 0 else privsend("lvl: {0}, atk: {1}, grd: {2}, mag: {3}, mdef: {4}, hp: {5}, xp to next lvl: {6}, wins: {7}".format(checkStats[1],checkStats[2],checkStats[3],checkStats[4],checkStats[5],checkStats[6],checkStats[7],checkStats[8]),getNick(data))

							elif act[0].lower() == "history" and FIGHT_HISTORY:
								name = getNick(data)
								if LOGLEVEL >= 1: log("Getting fight history for {0}".format(name))
								fightlog = getHistory(name)
								if not fightlog or fightlog is None:
									fightsend("nothing. theres nothing here. youve fought no one. you lose. good day sir.")
									if LOGLEVEL >= 1: log("No history.")
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
									if LOGLEVEL >= 1: log("Fight history uploaded to: {0}".format(url))
									continue
								except Exception as e:
									fightsend("super. i think ive temporarily forgotten how to read. try again later.")
									if LOGLEVEL >= 1: log("Couldn't get history: {0}".format(str(e)))
									continue
		
							elif len(act[0]) == 1:
								name = getNick(data)
								canattack = 0
								inafight = 0
								q = con.db.cursor()
								q.execute("""
									SELECT * FROM FightsOngoing WHERE playerOne = ? or playerTwo = ? """, (getNick(data), getNick(data)))
								gotFight = q.fetchone()
								try:
									gotFight[0]
								except:
									continue
								else:
									inafight = 1
									if name == gotFight[3] and gotFight[2] == 1:
										attacker = name
									else:
										fightsend("it isnt your turn stop being impatient")
										continue
									if attacker == gotFight[1]:
										defender = gotFight[0]
									else:
										defender = gotFight[1]
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
									q.execute("""
										DELETE FROM FightsOngoing WHERE playerOne = ? or playerTwo = ? """, (attacker,attacker))
									con.db.commit()	
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
									q.execute("""
										DELETE FROM FightsOngoing WHERE playerOne = ? or playerTwo = ? """, (attacker,attacker))
									con.db.commit()
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
								else: # Check if someone gets an item
									itemPerson = 0
									seed = ((time.time() + xOrShift()) % 100) + 1
									if seed <= 20: itemPerson = attacker
									if seed >= 80: itemPerson = defender
									if itemPerson != 0:
			                                                        itemNo = getRandomItem()
			                                                	if itemNo == False: # still a chance to not get an item
				                                                        continue
			                                                        itemNo = itemNo[random.randint(0,len(itemNo)-1)]
			                                                        item = getItemByItemNo(itemNo)
			                                                        if item == False: # STILL a chance to not get an item
			                                                                continue
										if LOGLEVEL >= 1: log("{0} got an item from the fight! They got: {1}".format(itemPerson,item[0]))
			                                                        privsend("After the fight, you found a treasure chest.",itemPerson)
			                                                        privsend("In the chest was: --== {0} ==-- (Atk: {1} || Def: {2} || MagAtk: {3} || MagDef: {4} || HP Gain: {5}). --== {6}. ==--  Item number: {7}".format(item[1],item[3],item[4],item[5],item[6],item[7],item[8],itemNo),itemPerson)
			                                                        updateInventory(itemPerson,itemNo)
			                                                        privsend("It's been added to your inventory.  To see your inventory, type %fight inventory",itemPerson)
										privsend("To equip it now, type %fight equip {}".format(itemNo),itemPerson)
							else:
								fightsend("maybe you need to look at %fight help.  or learn how to read.  one of the two.")
							act = None
							f.pop()		
					else:
						try:
							lastMessage = getMessage(data)
							lastMessage = lastMessage.translate(None, "\t\r\n")
						except:
							lastMessage = "hi"
						lastPerson = getNick(data)
						lastTime = time.time()
						if data.lower().find(botname.lower() + ':') != -1: # Did someone say "botname: "?
							person = getNick(data)
							msg = getMessage(data)
							try:
								msg = msg.lower().split(botname.lower())[1:]
							except Exception as e:
								if LOGLEVEL >= 1: log("ERROR: Couldn't fetch message: {}".format(str(e)))
								continue
							msg = " ".join(msg)
							msg = msg.translate(None, "\t\r\n")
							msg = msg.replace(':', '', 1)
							if LOGLEVEL >= 1: log("{0} >> {1}: {2}".format(person,botname,msg))
							msg = msg.lower()
							if LOGLEVEL >= 1: log("Attempting to reply with cleverbot...")
							try:
								msg = convo.think(msg); # Trigger a cleverbot response
							except Exception as e:
								if LOGLEVEL >= 1: log("Cleverbot f'd up: {0}".format(str(e)))
								continue
							msg = msg.translate(None, "'\"!:;").lower()
							send("{0}: {1}".format(person,msg),getChannel(data))
							if LOGLEVEL >= 1: log("{0} replies => {1}: {2}".format(botname, person, msg))
							# END FIGHT

				# Below is the YouTube info method.
				if YOUTUBE_LINKS and action == 'PRIVMSG':
					try:
						youtube = re.findall(r'(https?://)?(www\.)?((youtube\.(com))/watch\?v=([-\w]+)|youtu\.be/([-\w]+))', getMessage(data))
					except:
						continue
					if youtube:
						vidid = [c for c in youtube[0] if c]
						vidid = vidid[len(vidid)-1]
						try:
							vidinfo = getVideo(vidid)
						except Exception as e:
							send("fake video alert fake video alert fake video alert.",getChannel(data))
							if LOGLEVEL >= 1: log("Couldn't get video information: {0}".format(str(e)))
							continue
						send("that video is titled \"{0}\" and it is {1} in length. just fyi".format(vidinfo[0],vidinfo[1]),getChannel(data))

				# Let's try to auto summarize some stuff
				if NEWS_LINKS and action == 'PRIVMSG':
					try:
						newsSummary
					except NameError:
						pass
					else:
						newsSummary = None
					findurl=re.compile("""((?:[a-z][\w-]+:(?:/{1,3}|[a-z0-9%])|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'".,<>?]))""")
					for url in re.findall(findurl, data):
						newsurl = url[0]
						if not newsurl.startswith('http'):
							newsurl = 'http://'+newsurl
						try:
							newsSummary,newsTitle,movies = whoHasTimeToRead(newsurl)
						except Exception as e:
							try:
								newsSummary
							except NameError:
								pass # Ignore name errors for now.
							except Exception as e:
								if LOGLEVEL >= 1: log("Summary error: {0}".format(str(e)))
								send("idk how to read the words on this page",getChannel(data))
								#sendPing('Gr3yBot','bgm','Gr3ybot Error.  Check logs for more info: {0}'.format(str(e)))
								continue
							else:
								pass
						try:
							if newsSummary is not None:
								if len(newsSummary) < SUMMARY_COUNT: continue
								if LOGLEVEL >= 1: 
									log("Found a news article!")
									log("Title: {0}, Related video: {1}".format(newsTitle.encode('utf-8','ignore'),movies))
									log("Summary: {0}".format(" ".join(newsSummary).translate(None, "\t\r\n")))
									try:
										send("title: \"{0}\". related video: {1}.  heres the jist:".format(newsTitle.lower().encode('utf-8','replace'),movies),getChannel(data))
									except Exception as e:
										if LOGLEVEL >= 1: log("Error in displaying article title: {}".format(str(e)))
										send("something about the title of this article is anti-bot. send this site an email and tell them to use utf-8 encoding.",getChannel(data))
								for thing in newsSummary:
									try:
										thing = thing.translate(None, "\t\r\n").encode('utf-8','replace')
										send("{0}".format(thing.lower()),getChannel(data))
									except:
										try:
											thing = thing.translate(None, "\t\r\n")
											send("{0}".format(thing.lower()),getChannel(data))
										except Exception as e:	
											if LOGLEVEL >= 1: log("Error in displaying article summary: {}".format(str(e)))
											break
						except Exception as e:
							# Something went wrong.  Log it.
							if LOGLEVEL >= 1: log("WARNING: {}".format(str(e)))
				connected = connected + "ed Blad"
				#--
				# Let's try to get a posted twitter status...
				#--
				if TWITTER_LINKS and action == 'PRIVMSG':
                                        findurl=re.compile("https?:\/\/twitter\.com\/(?:#!\/)?(\w+)\/status(es)?\/(\d+)")
                                        for url in re.findall(findurl, data):
                                                tid = url[2]
                                                person,tweet = getTweetFromID(tid)
						try:
	                                         	if tweet == "~501":
								send("that looks like a twitter url but i cant access prudish timelines",getChannel(data))
								continue
							elif tweet == "~404":
								send("404 twitter not found",getChannel(data))
								continue
							else:
								send("oh! a twitter!  heres what it says: @{0} >> {1}".format(person,tweet),getChannel(data),tell=True)
								continue
						except Exception as e:
							if LOGLEVEL >= 1: log("ERROR: Couldn't fetch tweet: {}".format(str(e)))
							continue
				#-- 
				# Below is the Gimli subroutine.
				# It looks for two back-to-back instances of the word "and" beginning a sentence
				# If it sees that, it prints "AND MY AXE!"
				#
				# Fun fact: This is the only thing the bot returns in its own voice that contains a capital letter.
				# This is by design.
				#--:
				gimli = getMessage(data)
				connected = connected + "e of the w"
				try: 
					gimli = gimli.split(' ')[0:]
				except AttributeError:
					gimli = "Nope"
				if gimli[0].lower() == 'and' and gimli[1].lower() == 'my':
					andcount+=1
					if LOGLEVEL >= 1: log("Gimli = {0}".format(andcount))
					if andcount == 2:
						send("AND MY AXE!",getChannel(data))
						andcount=0
						if LOGLEVEL >= 1: log("Gimli subroutine triggered!")
				else:
					andcount=0
				#-- END GIMLI

				#-- What? Did somebody say..
				connected = connected + "indseeker"
				if connected.lower() in data.lower():
					send("did somebody say [{}]?!".format(connected),getChannel(data),tell=True)
				#-- Who? 

				if "/rant" in data.lower():
					send("geez take a breath dude its ok",getChannel(data))
		
				#--
				# Below is the process to tell someone a memo that was left for them,
				# and then remove that memo from the memo file.
				# This will send to either the main bot channel or the fighting channel,
				# depending on where the user goes active.
				#--
				memnick = getNick(data) # Get the nickname of the person who last said something.
				if special == 0 and action != "JOIN":
					q = con.db.cursor()
					q.execute("""
						SELECT * FROM Memos WHERE toUser = ? """, (memnick,))
					for tellMsg in q.fetchall():
						try:
							if getChannel(data) != fightchan:
								send("{1} said >> tell {2} {3}".format(memnick,tellMsg[1],memnick,tellMsg[3].encode('utf-8','ignore')),getChannel(data),tell=True)
							else:
								fightsend("{1} said >> tell {2} {3}".format(memnick,tellMsg[1],memnick,tellMsg[3].encode('utf-8','ignore')),tell=True)
							if LOGLEVEL >= 1: log("Told {0} {1}".format(memnick,tellMsg[3]))
							q.execute("""
								DELETE FROM Memos WHERE id = ? """, (tellMsg[0],))
						except:
							pass
					con.db.commit()
				#-- END MEMO

				#--
				# Check to see if we're live on Twitch
				if getIsTwitchStreaming() == "Yes" and isStreaming == 0:
					if LOGLEVEL >= 1: log("We're live on twitch.  Notifying chat...")
					isStreaming = 1
					for chan in channels:
						send(twitchnotifmsg,chan)
					pingAll("The Greynoise Podcast","The Greynoise Podcast has gone live on Twitch!  Visit https://greynoi.se/live to watch!")
				if getIsTwitchStreaming() == "No" and isStreaming == 1:
					if LOGLEVEL >= 1: log("Live stream over.  Notifying chat...")
					isStreaming = 0
					for chan in channels:
						send("ok the live stream is over", chan)

				#--
				# Let's log when the active user was last seen
				if len(memnick) > 0 and memnick != botname:
					if "." in memnick: continue
					try:
						q.execute("""
							INSERT OR REPLACE INTO LastSeen(User,Time,Channel,Msg) VALUES (?, ?, ?, ?)""", (memnick, time.time(), getChannel(data), unicode(getMessage(data), encoding='utf8')))
						con.db.commit()
					except: continue

				# Now let's see if someone wants a ping when someone else is alive in chat.
				q.execute("""
					SELECT * FROM Pings WHERE checkUser = ? """, (memnick,))
				for pingMsg in q.fetchall():
						try:
							sendPing('GreyBot',pingMsg[2],"{0} is chatting it up in {1}".format(memnick,defchannel))
							if pingMsg[3] == 0: send("hey {0}, {1} told me to let them know when you start chatting. and i did.  so you have like 20 seconids to go idle again".format(memnick,pingMsg[2]),getChannel(data))
							q.execute("""
								DELETE FROM Pings WHERE id = ? """, (pingMsg[0],))
							con.db.commit()
						except Exception as e:
							if LOGLEVEL >= 1: log("ERROR: Couldn't send ping: {}".format(str(e)))
							continue
						if LOGLEVEL >= 1: log("Triggering a ping: {0} wanted to know if {1} joined or unidled.".format(pingMsg[2],memnick))
						continue
	
				# Finally, let's see if someone wants to correct themselves.
				if len(memnick) > 0 and memnick != botname:
					searchReplace = re.compile("s/((\\\\\\\\|(\\\\[^\\\\])|[^\\\\/])+)/((\\\\\\\\|(\\\\[^\\\\])|[^\\\\/])*)((/(.*))?)")
					match = searchReplace.match(getMessage(data))
				
					if match:
						s = match.groups()[0]
						r = match.groups()[3]
						searchAndReplace(getNick(data), s, r, getChannel(data))
					else:
						chatter = getNick(data)
				                message = getMessage(data)
				                if (' ' in chatter) == False:
				                	try:
				                        	if len(message.rstrip()) > 0 and message[:1] != "s/":
		                 		                	addToSearchDb(chatter,message)
			                                except Exception as e:
			                                        pass
					
			
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
				saysomething = random.randint(1,121)
				if saysomething < 15:
					afile = open('overlord.txt', 'rb')
					thisline = rline(afile)
					thisline = "".join(c for c in thisline if c not in ('\'','"','!','?',':',';'))
					send("when i am an evil overlord, {0}".format(thisline),getChannel(data))
					if LOGLEVEL >= 1: log("Random Chatter: when i am an evil overlord, {0}".format(thisline))
				if 15 < saysomething < 30:
					afile = open('marvin.txt', 'rb')
					thisline = rline(afile)
					thisline = "".join(c for c in thisline if c not in ('\'','"','!','?',':',';'))
					send("{0}".format(thisline),getChannel(data))
					if LOGLEVEL >= 1: log("Random Chatter: {0}".format(thisline))
				if 30 < saysomething <= 45 and TWITTER_ENABLED:
					followAll()
					try:
						fol = getRandomFollower()
					except (Exception, tweepy.error.TweepError) as e:
						if LOGLEVEL >= 1: log("Error with tweepy: {0}".format(str(e)))
						if e.message[0]['code'] == 88:
							send("you guys are all farts",getChannel(data))
						continue
					try:
						send("lets see what one of my followers, {0}, is doing on twitter...".format(fol),defchannel)
						if LOGLEVEL >= 1: log("Idle chatter: Checking @{}'s Twitter feed for latest status.".format(fol))
					except Exception as e:
						if LOGLEVEL >= 1: log("Can't retrieve twitter followers: {0}".format(str(e)))
						continue
					time.sleep(1)
					mag = getTweet(fol)
					if mag == "-*404":
						send("not sure how this happened, but that person doesnt exist anymore.  this is an error that no one should ever see.  please send msg to bgm and let him know i broke",getChannel(data))
						if LOGLEVEL >= 1: log("Doesn't Exist")
						continue
					if mag == "-*501":
						send("nevermind.  @{0} is a buttface and wont accept my follow request".format(tweetnick),getChannel(data))
						if LOGLEVEL >= 1: log("Not Authorized")
						continue
					if len(mag) == 0:
						send("huh i guess @{} never tweeted anything befote in their life ever".format(fol),getChannel(data))
						if LOGLEVEL >= 1: log("No tweets found!")
						continue
					for tweet in mag:
						try:
							msg = tweet.retweeted_status.text
							getrt = tweet.text.split('@')[1].split(':')[0]
							msg = "RT @{0}: {1}".format(getrt,msg)
						except (Exception, AttributeError) as e:
							if LOGLEVEL >= 1: log("Non-fatal issue with tweet: {0}".format(str(e)))
							msg = tweet.text
						send("@{0} >> {1}".format(fol,msg),defchannel)
						if LOGLEVEL >= 1: log("Random Chatter: @{0} >> {1}".format(fol, msg))
						send("follow {} to get your tweets in here".format(twittername),defchannel)
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
					if LOGLEVEL >= 1: log("Attempting to make an idle cleverbot response...")
					try:
						msg = convo.think(lastMessage)
					except Exception as e:
						if LOGLEVEL >= 1: log("Cleverbot error: {0}".format(str(e)))
						continue
					if LOGLEVEL >= 1: 
						log("Random Chatter: Last message from {0} was {1}.".format(lastPerson,lastMessage))
						log("Random Chatter: Replying to {0} with: {1}".format(lastPerson,msg))
					send("{}".format(msg),getChannel(data))
				if 100 < saysomething <= 119:
					msg = weirdBotOutput()
					send("{}".format(msg),getChannel(data))	
					if LOGLEVEL >= 1: log("Random Chatter: Confession - {0}".format(msg))
				if 120 < saysomething:
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
						if LOGLEVEL >= 1: log("It sang the DK rap!")
						send("here here here here here we go",getChannel(data))
						time.sleep(.5)
						send("well theyre finally here, performing for you",getChannel(data))
						time.sleep(.5)
						send("and if you know the words you can join in too",getChannel(data))
						time.sleep(.5)
						send("put your hands together if you want to clap",getChannel(data))
						time.sleep(.5)
						send("as we take you through this monkey rap",getChannel(data))
						time.sleep(.5)
						send("d-k.  donkey kong.",getChannel(data))
						time.sleep(.5)
						send("d-k.  DONKEYKONGISHERE.",getChannel(data))

		if pinger.tgGetMessage()[0] is not None and pinger.tgGetMessage()[1] is not None:
			tgUser = pinger.tgGetMessage()[0]
			tgId = pinger.tgGetMessage()[1]
			pinger.fromuser = None
			pinger.fromid = None
			pingerFound = "No"
			if LOGLEVEL >= 1: log("Request to add {0} to Telegram list.".format(tgUser))
			for c in channels:
				chatusers = getChatters(chan=c)
				for k in chatusers:
					if tgUser == k:
						pinger.userToDb(tgUser, tgId)
						pingerFound = "Yes"
						break
				if pingerFound == "Yes": break
						

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
