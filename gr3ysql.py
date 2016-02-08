#!/usr/bin/env python

# This is mostly used for fighting for now.  I may come up with
# other things this could be used for later on down the road.

from gr3ybot_settings import botname, SLACK_ENABLED, TWITTER_ENABLED
import sqlite3

class Gr3ySQL(object):

	def __init__(self):
		self.db = sqlite3.connect(botname + '_db.db')
		self.init()

	def init(self,checkEq=False):
		try:
			# Init the db
			create = self.db.cursor()
			
			# Create the tables if they don't already exist.

			# Logging
			create.execute("""
					CREATE TABLE IF NOT EXISTS
						Log (
							id INTEGER PRIMARY KEY AUTOINCREMENT,
							dateTime INTEGER,
							user VARCHAR(12) COLLATE NOCASE,
							text TEXT COLLATE NOCASE
						)
			""")
			
	
			# Fighting Equipment List
			create.execute("""
					CREATE TABLE IF NOT EXISTS
						EquipmentList (
							itemNo VARCHAR(4) PRIMARY KEY,
							itemName VARCHAR(50),
							itemChance INTEGER,
							atk INTEGER,
							grd INTEGER,
							mag INTEGER,
							mdef INTEGER,
							hp INTEGER,
							itemDesc TEXT COLLATE RTRIM
						)
			""")
	
			# Fighters
			create.execute("""
	                                CREATE TABLE IF NOT EXISTS
	                                        Fighters (
	                                                name VARCHAR(12) PRIMARY KEY COLLATE NOCASE,
							level INTEGER,
							atk INTEGER,
							grd INTEGER,
							mag INTEGER,
							mdef INTEGER,
							hp INTEGER,
							xp INTEGER,
							wins INTEGER,
							tmpstat INTEGER,
							tmpbuff INTEGER,
							atksincelvl INTEGER,
							satksincelvl INTEGER,
							fatksincelvl INTEGER,
							magatksincelvl INTEGER,
							grdsincelvl INTEGER,
							mgrdsincelvl INTEGER,
							lastFought VARCHAR(12)
	                                        )
	                """)
	
			# Ongoing Fights
			create.execute("""
	                                CREATE TABLE IF NOT EXISTS
	                                        FightsOngoing (
	                                                playerOne VARCHAR(12) PRIMARY KEY COLLATE NOCASE,
							playerTwo VARCHAR(12) COLLATE NOCASE,
							accepted INTEGER,
							whoseTurn VARCHAR(12) COLLATE NOCASE,
							turnTotal INTEGER,
							lastAction INTEGER,
							stopper VARCHAR(12) COLLATE NOCASE
	                                        )
	                """)
	
			# Fight Inventories
			create.execute("""
	                                CREATE TABLE IF NOT EXISTS
	                                        Inventories (
	                                                user VARCHAR(12) PRIMARY KEY COLLATE NOCASE, 
							items TEXT,
							tempItem VARCHAR(4)
	                                        )
	                """)

			# Equipped Items
			create.execute("""
                                        CREATE TABLE IF NOT EXISTS
                                                EquippedItems (
                                                        user VARCHAR(12) PRIMARY KEY COLLATE NOCASE,
                                                        weapon VARCHAR(4),
                                                        armor VARCHAR(4),
							boot VARCHAR(4),
							acc1 VARCHAR(4),
							acc2 VARCHAR(4)
                                                )
                        """)

	
			# Memos
			create.execute("""
	                                CREATE TABLE IF NOT EXISTS
	                                        Memos (
	                                                id INTEGER PRIMARY KEY AUTOINCREMENT,
	                                                fromUser VARCHAR(12) COLLATE NOCASE,
	                                                toUser VARCHAR(12) COLLATE NOCASE,
	                                                message TEXT,
							dateTime INTEGER
	                                        )
	                """)
	
			# Reminders
			create.execute("""
	                                CREATE TABLE IF NOT EXISTS
	                                        Reminders (
	                                                id INTEGER PRIMARY KEY AUTOINCREMENT,
	                                                user VARCHAR(12) COLLATE NOCASE,
	                                                atTime INTEGER,
	                                                message TEXT,
	                                                dateTime INTEGER
	                                        )
	                """)
		
			# Pings
			if SLACK_ENABLED:
				create.execute("""
						CREATE TABLE IF NOT EXISTS
							Pings (
								id INTEGER PRIMARY KEY AUTOINCREMENT,
								checkUser VARCHAR(12) COLLATE NOCASE,
								toUser VARCHAR(12) COLLATE NOCASE
							)
				""")
	
			# Slack Aliases
			if SLACK_ENABLED:
				create.execute("""
		                                CREATE TABLE IF NOT EXISTS
		                                        SlackAliases (
		                                                ircUser VARCHAR(12) PRIMARY KEY,
		                                                slackUser VARCHAR(12)
		                                        )
		                """)
	
			# Twitter IDs
			if TWITTER_ENABLED:
				create.execute("""
	                    	            CREATE TABLE IF NOT EXISTS
		                                        TwitterIDs (
		                                                id INTEGER,
		                                                dateTime INTEGER
		                                        )
		                """)
	
			self.db.commit()
		except Exception as e:
			self.db.rollback()
			raise e
		finally:
			if checkEq: self.checkEquipment()
			else: pass

	def checkEquipment(self):
		count = 0
		try:
			q = self.db.cursor()
			q.execute("""
				SELECT COUNT(*) FROM EquipmentList
			""")
			
			count = q.fetchone()[0]
			if count == 0 or count is None:
				with open('equipmentlist','r') as f:
					for line in f.readlines():
						if line.startswith('#') or len(line.translate(None, '\r\n')) == 0: continue
						itemId = line.split(' - ')[0]
						itemInfo = line.split(' - ')[1].split('/')
						q.execute("""
							INSERT INTO EquipmentList (itemNo, ItemName, itemChance, atk, 
									grd, mag, mdef, hp, itemDesc)
							VALUES ( ?, ?, ?, ?, ?, ?, ?, ?, ?)
						""", (itemId, itemInfo[0], itemInfo[1], itemInfo[2], itemInfo[3], 
							itemInfo[4], itemInfo[5], itemInfo[6], itemInfo[7]))
						self.db.commit()
				f.close()
				return
	
			with open('equipmentlist','r') as f:	
				for lineCount, l in enumerate(f):
					if l.startswith('#') or len(l.translate(None, '\r\n')) == 0:
						lineCount = lineCount - 1
			f.close()
			
			if count < lineCount:
				with open('equipmentlist','r') as f:
	                                for line in f.readlines():
	                                        if line.startswith('#') or len(line.translate(None, '\r\n')) == 0: continue
	                                        itemId = line.split(' - ')[0]
	                                        itemInfo = line.split(' - ')[1].split('/')
		                                q.execute("""
		                                        INSERT OR REPLACE INTO EquipmentList (itemNo, ItemName, itemChance, atk,
		                                			           grd, mag, mdef, hp, itemDesc)
	                                                VALUES ( ?, ?, ?, ?, ?, ?, ?, ?, ?)
	                                        """, (itemId, itemInfo[0], itemInfo[1], itemInfo[2], itemInfo[3],
		                                                itemInfo[4], itemInfo[5], itemInfo[6], itemInfo[7]))
	                                        self.db.commit()
	                        f.close()
	                        return
		except Exception as e:
			self.db.rollback()
			raise e
