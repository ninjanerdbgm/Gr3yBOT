#!/usr/bin/env python
from gr3ysql import Gr3ySQL
from gr3ybot_settings import SLACK_API_TOKEN
from slacker import Slacker

slack = Slacker(SLACK_API_TOKEN)
con = Gr3ySQL()

def sendPing(fromuser,touser,msg):
	userlist = slack.users.list()
	userlist = userlist.body['members']
	sql = con.db.cursor()
	n = sql.execute("SELECT * FROM SlackAliases")
	names = n.fetchall()
	for i in userlist:
		for name in names:
			if touser.lower() == name[0].lower():
				if i["name"].lower() == name[1].lower():
					slack.chat.post_message(username='Gr3yBOT',link_names=1,channel='#general',text='{0} - @{1}: {2}'.format(fromuser,i["name"],msg))
					con.db.commit()
					return "Sent!"
	con.db.commit()
	return "i dont know who dat is."

def findSlacker(username):
	userlist = slack.users.list()
	userlist = userlist.body['members']
	found = 0
	for i in userlist:
		print i["name"]
		if i["name"].lower() == username.lower():
			found = 1
	if found == 1:
		return True
	return False
