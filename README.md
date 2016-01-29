# Gr3yBOT    
A snarky, full-featured, python IRC bot.    
Written by bgm    
https://greynoi.se

      What started as a small bot aimed for no more than just printing
      out the latest episode info in chat turned in to something much,
      much more.  At the time of this writing, it supports:

              - Wikipedia searching
              - Meal suggestions powered by Yelp
              - Urban Dictionary definitions
              - A full-fledged RPG fighting system
              - CleverBot integration
              - A creepy stalker subrouting (I'm a horror fan)
              - A memos system to relay a message to another user
              - Unobtrusive and entertaining idle chat.
              - Twitter Integration, including:
                      - Being able to send tweets as the bot.
                      - The bot auto-follows its followers.
                      - The bot randomly reads a follower's latest tweet in chat.
                      - You can get any twitter user's latest tweet in chat.
                      - The bot responds to tweets @ it on Twitter
                      - The bot automatically displays tweets @ it in chat too.
              - Channel op commands, if user's in the admin file:
                      - Op a user
                      - Change the topic
	      NEW with 1.9:
		      - Automatic News Article summarization
		      - Automatic Youtube video information
		      - Slack integration for cell phone pinging
			  
		  NEW with 1.91:
			  - Better data collection and aggregation
			  - Added the ability for the bot to decode QR codes from a supplied URL
	      
              And of course,
              - Displays latest GR3YNOISE podcast info
              - Displays the upcoming events at SynShop Las Vegas

      Gr3yBOT requires the following python modules:
            For Twitter functionality:
                  - Tweepy
            For Urban Dictionary and Weather:
                  - BeautifulSoup
            For Ping functionality:
                  - Slacker
            For Wikipedia:
                  - Wikipedia
            For Cleverbot:
                  - CookieJar
            For Weather:
            	  - feedparser

      NEW IN 1.9:
		- Article Summarization
		
			For article summarization, more dependencies have been added.  You'll need to install Goose for python as well as
			NLTK.  After installing NLTK, you'll need to get the following dependencies:
				- stopwords
				- punkt
				- maxent_treebank_pos_tagger

      --== IMPORTANT!! ==--
            Make sure you open gr3ybot_settings.py and configure the bot before attempting to run it.

	  NEW in 1.91:
		- QR Code Decoding
			
			For QR code decoding, even more dependencies are required:
				- python-qrtools (sudo apt-get install python-qrtools)
					NOTE:
						If you're getting an error message saying qrtools doesn't exist, try this:
						sudo apt-get install libzbar-dev
						sudo pip install zbar
						sudo pip install Image
