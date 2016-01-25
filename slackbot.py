#!/usr/bin/env python

from gr3ybot_settings import SLACK_API_TOKEN
from slacker import Slacker

slack = Slacker(SLACK_API_TOKEN)

def sendPing(fromuser,touser,msg):
	userlist = slack.users.list()
	userlist = userlist.body['members']
	for i in userlist:
		with open('slack_aliases','r') as f:
			f.seek(0)
			lines = f.readlines()
			for line in lines:
				line = line.strip(' \r\n')
				names=line.split('[-]')[1:]
				for name in names:
					if touser.lower() == line.split('[-]')[0].lower():
						if i["name"].lower() == name.lower():
							slack.chat.post_message(username='Gr3yBOT',link_names=1,channel='#general',text='{0} - @{1}: {2}'.format(fromuser,i["name"],msg))
							return "Sent!"
			f.close()
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
