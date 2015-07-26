#-- Please configure these general settings:

## timeformat indicates how the date will appear in the logs.
timeformat = "%m/%d/%y %H:%M:%S"

## The following are your irc settings
server = 'irc.freenode.net'
port = 6667
channel = '#gr3ynoise'
botname = 'Gr3yBot'
### password is really only necessary if your bot is registered.
### But I recommend registering the bot's nick as well as giving it auto-ops 
### in your channel for full functionality.
password = ''

### server_slug is the text that appears when you connect to your server.
### This is used to determine when the bot joins the channels.
server_slug = 'Welcome to freenode - supporting the free and open source'



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
#       VERBOSE
#               Set this to True if you want to output all of the bot's calls and
#               processes to the screen.
#               Set to False if you don't want to see any of that nonsense.
#       CHATLOG
#               Set this to True if you want to display the chatlog as the bot runs.
#               Set to False if you don't.
#       FIGHT_VERBOSE
#               Set this to True if you want to see the fight dice rolls and
#               damage calculations.
#       YOUTUBE_LINKS
#               Set this to True to have the bot auto-retrieve info about
#               YouTube links posted in chat.
LOGFILE = 'bot.log'
ECHO_LOG = True

LOCALTZ = 'US/Pacific'

VERBOSE = True
CHATLOG = False
FIGHT_VERBOSE = True

#-- Please configure the following features
#	YOUTUBE_LINKS
#		Set this to true if you'd like the bot to detect YouTube links
#		in the chat and display their length and title.  Set this to False
#		if you don't have any YouTube developer API keys.
#	*_ENABLED
#		Enable or disable the bot's various features.
#		If you don't have developer API keys for Yelp, YouTube,
#		Slack, or Twitter, and don't plan on getting any,
#		then make sure to disable those features.
YOUTUBE_LINKS = True
TWITTER_ENABLED = True
YELP_ENABLED = True
PING_ENABLED = True
URBANDICT_ENABLED = True
WIKIPEDIA_ENABLED = True
#--

# Fight Settings:
#	fightchan
#		Set this to the channel you wish to constrain the fights to.
#		If this is set to None, it defaults to the same as your main channel.
#fightchan = "#gr3yfights"
fightchan = None

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
#	Pastebin is used to store fight history, if the chatters so choose.
#
#	PASTEBIN_DEV_KEY
#		You can get a dev key by signing up for a pastebin.com account and going
#		here: http://pastebin.com/api#1
PASTEBIN_DEV_KEY = ''

# Podcast Info
#	podcast_keywords:
#               This contains a list of words that the bot will look for after the %
#               in order to deliver podcast info to the users.
podcast_keywords = [
        "info",
        "show",
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
#twittername = '@Gr3yBOT'									#
twittername = ''										#
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
        "lunch",											#
        "dinner",											#
        "breakfast",											#
        "brunch"											#
        ]												#
#-------------------------------------------------------------------------------------------------------#


# YouTube Settings
#	DEVELOPER KEY
#		A YouTube Developer Key can be obtained here: https://developers.google.com/youtube/v3/
YOUTUBE_DEVELOPER_KEY = ''
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'

# All finished?  If so, set the following variable to True:
CONFIGURED = False
