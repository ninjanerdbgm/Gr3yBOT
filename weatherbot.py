#!/usr/bin/env python

import requests
from bs4 import BeautifulSoup
import feedparser
import sys
import urllib, urllib2

if __name__ == "__main__":
	print "What are you doing?  Why are you doing this?"
	sys.exit()

def getWindDirection(wind):
	if wind >= 348.75 or wind < 11.25:
		return "north"
	if wind >= 11.25 or wind < 33.75:
		return "north-northeast"
	if wind >= 33.75 or wind < 56.25:
		return "northeast"
	if wind >= 56.25 or wind < 78.75:
		return "east-northeast"
	if wind >= 78.75 or wind < 101.25:
		return "east"
	if wind >= 101.25 or wind < 123.75:
		return "east-southeast"
	if wind >= 123.75 or wind < 146.25:
		return "southeast"
	if wind >= 146.25 or wind < 168.75:
		return "south-southeast"
	if wind >= 168.75 or wind < 191.25:
		return "south"
	if wind >= 191.25 or wind < 213.75:
		return "south-southwest"
	if wind >= 213.75 or wind < 236.25:
		return "southwest"
	if wind >= 236.25 or wind < 258.75:
		return "west-southwest"
	if wind >= 258.75 or wind < 281.25:
		return "west"
	if wind >= 281.25 or wind < 303.75:
		return "west-northwest"
	if wind >= 303.75 or wind < 326.25:
		return "northwest"
	if wind >= 326.25 or wind < 348.75:
		return "north-northwest"

def getWeather(loc):
	weather = {}
	loc = loc.replace('%','%25')
	loc = loc.split(' ')
	loc = "%20".join(loc)
	# Let's get the Where On Earth ID...
	url = 'http://query.yahooapis.com/v1/public/yql?q=select%20*%20from%20geo.placefinder%20where%20text=%22{0}%22'.format(loc)
	r = requests.get(url)
	soup = BeautifulSoup(r.content)
	for breaks in soup.find_all('br'):
		breaks.extract()
	try:
		woeid = soup.find("woeid").text
	except:
		return "~*404"
	# Done
	# Now let's get the weather...
	url = 'http://weather.yahooapis.com/forecastrss?w={0}'.format(woeid)
	parsed = feedparser.parse(url)
	parsed_loc = parsed['feed']['title']
	parsed_loc = parsed_loc.replace('Yahoo! Weather - ','')
	parsed_loc = parsed_loc.lower()
	try:
		parsed_clouds = parsed.entries[0]['yweather_condition']
		parsed_clouds = parsed_clouds['text'].lower()
	except KeyError:
		parsed_clouds = "idk"
	try:
		parsed_temp = parsed.entries[0]['yweather_condition']
		parsed_temp = int(parsed_temp['temp'])
	except (KeyError, ValueError):
		parsed_temp = "idk"
	try:
		parsed_humidity = parsed['feed']['yweather_atmosphere']['humidity']
		parsed_pressure = parsed['feed']['yweather_atmosphere']['pressure']
		parsed_visibility = parsed['feed']['yweather_atmosphere']['visibility']
	except (KeyError, ValueError):
		parsed_humidity,parsed_pressure,parsed_visibility = "idk","idk","idk"
	try:
		parsed_sunrise = parsed['feed']['yweather_astronomy']['sunrise'].lower()
		parsed_sunset = parsed['feed']['yweather_astronomy']['sunset'].lower()
	except (KeyError, ValueError):
		parsed_sunrise,parsed_sunset = "idk","idk"
	try:
		parsed_wind_chill = parsed['feed']['yweather_wind']['chill']
		parsed_wind_speed = parsed['feed']['yweather_wind']['speed']
		parsed_wind_direction = float(parsed['feed']['yweather_wind']['direction'])
		parsed_wind_direction = getWindDirection(parsed_wind_direction)
	except (KeyError, ValueError):
		parsed_wind_chill,parsed_wind_speed,parsed_wind_direction = "idk","idk","idk"

	weather['location'] = parsed_loc
	weather['cloudcover'] = parsed_clouds
	weather['temp'] = parsed_temp
	weather['humidity'] = parsed_humidity
	weather['pressure'] = parsed_pressure
	weather['visibility'] = parsed_visibility
	weather['sunrise'] = parsed_sunrise
	weather['sunset'] = parsed_sunset
	weather['windchill'] = parsed_wind_chill
	weather['windspeed'] = parsed_wind_speed
	weather['winddirection'] = parsed_wind_direction
	
	return weather
