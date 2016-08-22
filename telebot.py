from gr3ybot_settings import *
from gr3ysql import Gr3ySQL
import telepot

class Pinger(object):

        def __init__(self):
                self.bot = telepot.Bot(TELEGRAM_API_TOKEN)
		self.fromid = None
		self.fromuser = None
                self.con = Gr3ySQL()

	def addNewUser(self, msg=None):
		self.fromid = msg['from']['id']
		try:
			self.command = msg['text'].split()
		except:
			self.bot.sendMessage(fromuser, "what")
			return
	
		if self.command[0] == '/addme':
			try:
				self.fromuser = self.command[1]
			except:
				self.bot.sendMessage(self.fromid, "yo u need to specify your irc username. like /addme greybot")

	def userToDb(self, username, userid):
		q = self.con.db.cursor()
		q.execute(""" SELECT * FROM TelegramIDs WHERE ircUser = ? """, (username,))
		n = q.fetchall()
		if len(n) > 0:
			self.bot.sendMessage(userid, "youre already set up. dont worry about it pal.")
			self.con.db.commit()
		else:
			q.execute("""
	        	      	INSERT INTO TelegramIDs (ircUser,telegramId) VALUES (?, ?) """, (username,userid))
		        self.con.db.commit()
		        self.bot.sendMessage(userid, "ok ive added you. youll now get pings")
	
	def sendPing(self, fromuser, touser, msg):
		sql = self.con.db.cursor()
		n = sql.execute(""" SELECT * FROM TelegramIDs WHERE ircUser = ? """, (touser,))
		user = n.fetchall()
	        for person in user:
			if fromuser == touser: self.bot.sendMessage(person[1], "hey {0}, here's your requested ping: {1}".format(touser,msg))
			elif fromuser == "The Greynoise Podcast": self.bot.sendMessage(person[1], "Announcement: {0}".format(msg))
			else: self.bot.sendMessage(person[1], "hey {0}, {1} is asking for you in irc: {2}".format(touser,fromuser,msg))
	        self.con.db.commit()

	def tgGetMessage(self):
		return self.fromuser, self.fromid
