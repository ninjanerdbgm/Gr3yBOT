# Let's make sure this is configured.
import sys
import time

#===============================================#
# -- Please configure the following settings -- #
#===============================================#

## timeformat indicates how the date will appear in the logs.
timeformat = "%m/%d/%y %H:%M:%S"

## The following are your irc settings
server = ''
port = 6667
channelpw = ''
botname = 'Gr3yBot'
version = "1.97. Version Name: Yes Man Junior"

# Set channels to join.  The first channel will be
# set as the main channel.  
# NOTE:
#	Do not put the fight channel in here (if separate).
#	You'll specify that later on.
channels = [
	'#somechannel',
	'#starwars'
	]

## Define Admins here.  These are the people that can run
## the admin commands.
ADMINLIST = [
	'bgm'
	]
	
### password is really only necessary if your bot is registered.
### But I recommend registering the bot's nick as well as giving it auto-ops 
### in your channel for full functionality.
password = ''

### server_slug is the text that appears when you connect to your server.
### This is used to determine when the bot joins the channels.
server_slug = ''



#-- Please configure these logging variables:
#       LOGFILE
#               Name of the bot's log.  Defaults to bot.log because
#               I'm really fucking clever.  This file gets recreated every time
#               the bot is re-run, so if you want backups, stop the bot process,
#               cp the log file, then start the bot process.
#       ECHO_LOG
#               Set this to True if you'd like to have the script echo the bot lot
#               as it runs.
#       LOCALTZ
#               Set to your local timezone, for logging.  More info:
#               http://stackoverflow.com/questions/13866926/python-pytz-list-of-timezones
#	LOGLEVEL
#		Set the verbosity of the bot's log.
#		0 - No logging.
#		1 - Basic action logging
#		2 - Basic action and chat logging
#		3 - Basic actions, chat, and the entire data stream logging
#       FIGHT_VERBOSE
#               Set this to True if you want to see the fight dice rolls and
#               damage calculations.
#	FIGHTLOG
#		The name of the fight log file. If set to None, it defaults to the 
#		bot's log.
LOGFILE = 'bot.log'
ECHO_LOG = True
LOCALTZ = 'US/Pacific'

LOGLEVEL = 1

FIGHT_VERBOSE = True
FIGHTLOG = 'fightinfo.log'

#-- Please configure the following features
#	YOUTUBE_LINKS
#		Set this to true if you'd like the bot to detect YouTube links
#		in the chat and display their length and title.  Set this to False
#		if you don't have any YouTube developer API keys.
#	NEWS_LINKS
#		Set this to true if you'd like the bot to try to detect news 
#		articles and attempt to provide a summary for them.
#	SUMMARY_COUNT
#		If NEWS_LINKS is True, how many sentences do you want to generate
#		for your summary?
#	*_ENABLED
#		Enable or disable the bot's various features.
#		If you don't have developer API keys for Yelp, YouTube,
#		Slack, Pastebin (Fight History), or Twitter, and don't 
#		plan on getting any, then make sure to disable those features.
YOUTUBE_LINKS = True
NEWS_LINKS = True
SUMMARY_COUNT = 3
TWITTER_ENABLED = True
YELP_ENABLED = True
PING_ENABLED = True
URBANDICT_ENABLED = True
WIKIPEDIA_ENABLED = True
WOLFRAM_ENABLED = True
QR_ENABLED = True
#--

# Fight Settings:
#	fightchan
#		Set this to the channel you wish to constrain the fights to.
#		If this is set to None, it defaults to the same as your main channel.
#	FIGHT_HISTORY
#		Set this to True if you want people to be able to get a paste of 
#		their last fight posted to Pastebin.  You'll need to have a Pastebin
#		API key for this to work.
fightchan = None
#fightchan = "#thefighting"
FIGHT_HISTORY = True

# Help
#	help_keywords:
#		This contains a list of words that the bot will look for after the %
#		in order to deliver help to the users.
help_keywords = [
	"help",
	"commands"
	]

# Memos
#	memo_keywords:
#               This contains a list of words that the bot will look for after the %
#               in order to set memos.
memo_keywords = [
	"tell",
	"memo",
	"memos"
	]

# Overlord
#	overlord_keywords:
#               This contains a list of words that the bot will look for after the %
#               in order to display an evil overlord quote.
overlord_keywords = [
        "overlord",
        "over",
        "ol",
        "lord"
        ]

# Pastebin
#       Pastebin is used to store fight history, if the chatters so choose.
#
#       PASTEBIN_DEV_KEY
#               You can get a dev key by signing up for a pastebin.com account and going
#               here: http://pastebin.com/api#1
PASTEBIN_DEV_KEY = ''

# Podcast Info
#	podcast_keywords:
#               This contains a list of words that the bot will look for after the %
#               in order to deliver podcast info to the users.
podcast_keywords = [
        "info",
        #"show",
        "podcast",
        "podcastinfo",
        "latest"
        ]

# Reminders
#	reminder_keywords:
#               This contains a list of words that the bot will look for after the %
#               in order to set reminders for the users.
reminder_keywords = [
	"remindme",
	"remind"
	]

# Slacker
#	API TOKEN:
#		You can get an api token from here: https://api.slack.com/web#authentication
#		Scroll down to Authentication.
SLACK_API_TOKEN = ''

# Twitter						
#-----------------------------------------------------------------------------------------------#	
#	twittername										#
#		Set this to your bot's twitter handle (or your twitter handle).			#
#		You need Twitter API keys for this to work.					#
twittername = '@Gr3yBOT'									#
												#
												#
#	API KEYS										#
#		You can get these from: https://apps.twitter.com/				#
TWIT_CONSUMER_KEY = ''										#
TWIT_CONSUMER_SECRET = ''									#
TWIT_ACCESS_KEY = ''										#
TWIT_ACCESS_SECRET = ''										#
												#
#	showtwitter_keywords:									#
#               This contains a list of words that the bot will look for after the %		#
#               in order to grab tweets from twitter.						#
showtwitter_keywords = [									#
        "twit",											#
        "getweet",										#
        "showtweet",										#
        "gettweet"										#
        ]											#
#-----------------------------------------------------------------------------------------------#

# Wikipedia
#	wiki_keywords:                                                                   
#               This contains a list of words that the bot will look for after the %
#               in order to search wikipedia.  
wiki_keywords = [
	"wiki",
	"wikipedia",
	"search",
	"lookup"
	]

# Yelp
#-------------------------------------------------------------------------------------------------------#
#	API KEYS											#
#		Yelp OAuth creds can be obtained here: https://www.yelp.com/developers/get_access	#
YELP_CONSUMER_KEY = ''											#
YELP_CONSUMER_SECRET = ''										#
YELP_TOKEN = ''												#
YELP_TOKEN_SECRET = ''											#
													#
#	yelp_keywords:											#
#               This contains a list of words that the bot will look for after the %			#
#               in order to search Yelp.								#
yelp_keywords = [											#
        "lunch",     # Returns lunch restaurants 							#
        "dinner",	 # Returns dinner restaurants							#
        "breakfast", # Returns breakfast restaurants							#
        "brunch"	 # Returns brunch restaurants							#
        ]												#
#-------------------------------------------------------------------------------------------------------#


# YouTube Settings
#	DEVELOPER KEY
#		A YouTube Developer Key can be obtained here: https://developers.google.com/youtube/v3/
YOUTUBE_DEVELOPER_KEY = ''
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'

# Wolfram Alpha Settings
#	API KEY
WOLFRAM_KEY = ''

#====================================================================================================###
#
#
#====================================================================================================###
# All finished?  If so, set the following variable to True:

CONFIGURED = False

#
#====================================================================================================###
#
#
#====================================================================================================###

if not CONFIGURED:
        print("\n===========")
	print("You haven't yet configured the bot.  Please open gr3ybot_settings.py and do so now.")
        print("If you have configured the bot and are still seeing this message, please set the CONFIGURED variable to True.")
        sys.exit()

affirmative = ["yes","ya","y","yep","sure","ok","sounds good","fine","uh huh","yea","yeah"]

if CONFIGURED:
	channel = channels[0]
	print("\n==========")
	print("Validating configuration.  Please wait...\n")
	time.sleep(1)
        if FIGHT_HISTORY and len(PASTEBIN_DEV_KEY) < 5:
                print("You've enabled Fight History, but didn't supply a valid Pastebin API dev key.")
                print("Do you want to disable Fight History?")
                if raw_input().lower() in affirmative:
                        FIGHT_HISTORY = False
		else:
			print("Script misconfiguration.  Exiting now...")
			sys.exit()
	if YOUTUBE_LINKS and len(YOUTUBE_DEVELOPER_KEY) < 5:
		print("You've enabled YouTube Link Translation, but didn't supply a valid YouTube API dev key.")
                print("Do you want to disable YouTube Link Translation?")
		if raw_input().lower() in affirmative:
                        YOUTUBE_LINKS = False
                else:
                        print("Script misconfiguration.  Exiting now...")
                        sys.exit()
	if TWITTER_ENABLED and (len(TWIT_CONSUMER_KEY) < 5 or len(TWIT_ACCESS_KEY) < 5 or len(TWIT_CONSUMER_SECRET) < 5 or len(TWIT_ACCESS_SECRET) < 5):
		print("You've enabled Twitter functions, but didn't supply valid Twitter API keys.")
                print("Do you want to disable Twitter functionality?")
		if raw_input().lower() in affirmative:
                        TWITTER_ENABLED = False
                else:
                        print("Script misconfiguration.  Exiting now...")
                        sys.exit()
	if YELP_ENABLED and (len(YELP_CONSUMER_KEY) < 5 or len(YELP_CONSUMER_SECRET) < 5 or len(YELP_TOKEN) < 5 or len(YELP_TOKEN_SECRET) < 5):
		print("You've enabled Yelp functionality, but didn't supply valid Yelp API keys.")
                print("Do you want to disable Yelp functionality?")
		if raw_input().lower() in affirmative:
                        YELP_ENABLED = False
                else:
                        print("Script misconfiguration.  Exiting now...")
                        sys.exit()
	if PING_ENABLED and len(SLACK_API_TOKEN) < 5:
		print("You've enabled Ping functionality, but didn't supply a valid Slack API token.")
                print("Do you want to disable Ping functionality?")
		if raw_input().lower() in affirmative:
                        PING_ENABLED = False
                else:
                        print("Script misconfiguration.  Exiting now...")
                        sys.exit()
	if WOLFRAM_ENABLED and len(WOLFRAM_KEY) < 5:
		print("You've enabled Wolfram Alpha functionality, but didn't supply a valid Wolfram Alpha key.")
		print("Do you want to disable Wolfram functionality?")
		if raw_input().lower() in affirmative:
			WOLFRAM_ENABLED = False
		else:
			print("Script misconfiguration.  Exiting now...")
			sys.exit()
	
	print("Current settings:")
	print("Fight History: {0}\nYouTube Links: {1}\nTwitter functions: {2}\nNews Links: {3}".format(FIGHT_HISTORY,YOUTUBE_LINKS,TWITTER_ENABLED,NEWS_LINKS))
	print("Yelp: {0}\nPing: {1}\nWolfram Alpha: {4}\nUrban Dictionary: {2}\nWikipedia: {3}".format(YELP_ENABLED,PING_ENABLED,URBANDICT_ENABLED,WIKIPEDIA_ENABLED,WOLFRAM_ENABLED))
	if raw_input("\nIs this look okay? (y/n): ").lower() in affirmative:
                pass
        else:
        	print("User halted. Exiting now...")
                sys.exit()
