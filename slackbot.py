#!/usr/bin/env python

from gr3ybot_settings import SLACK_API_TOKEN
from slacker import Slacker

slack = Slacker(SLACK_API_TOKEN)

def sendPing(fromuser,touser,msg):
	userlist = slack.users.list()
	userlist = userlist.body['members']
	for i in userlist:
		#-- Modify the usernames here:
		#
		if touser.lower() == "d0xy": touser = "doxy"
		if touser.lower() == "|bgm|": touser = "ninjanerdbgm"
		if touser.lower() == i["name"].lower():
			slack.chat.post_message(username='Gr3yBOT',link_names=1,channel='#general',text='{0} - @{1}: {2}'.format(fromuser,touser,msg))
			return "Sent!"
	return "i dont know who dat is."
3
