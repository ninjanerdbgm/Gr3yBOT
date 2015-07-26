#!/usr/bin/env python

from gr3ybot_settings import YELP_CONSUMER_KEY,YELP_CONSUMER_SECRET,YELP_TOKEN,YELP_TOKEN_SECRET
import oauth2
import argparse
import json
import sys
import urllib
import urllib2

#--
# Set some defaults..
DEFAULT_LOC = 'Las Vegas, NV'
SEARCH_LIMIT = 20
#--

def getFood(params=None):
	query = params or {}
	url = "http://api.yelp.com/v2/search?"
	
	consumer = oauth2.Consumer(YELP_CONSUMER_KEY, YELP_CONSUMER_SECRET)
	oauth_req = oauth2.Request(method="GET", url=url, parameters=query)

	oauth_req.update(
		{
			'oauth_nonce': oauth2.generate_nonce(),
			'oauth_timestamp': oauth2.generate_timestamp(),
			'oauth_token': YELP_TOKEN,
			'oauth_consumer_key': YELP_CONSUMER_KEY
		}
	)
	token = oauth2.Token(YELP_TOKEN, YELP_TOKEN_SECRET)
	oauth_req.sign_request(oauth2.SignatureMethod_HMAC_SHA1(), consumer, token)
	signed_url = oauth_req.to_url()

	try:
		yelp = urllib2.urlopen(signed_url, None)
	except urllib2.HTTPError as error:
		return "ERROR: {0}".format(error.code)

	try:
		suggestions = json.loads(yelp.read())
	finally:
		yelp.close()

	return suggestions

if __name__ == "__main__":
	print "You can't run this program separately!"
	sys.exit()	
