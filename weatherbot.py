#!/usr/bin/env python
# coding=utf8

from __future__ import unicode_literals
from gr3ybot_settings import WEATHER_API_KEY
from bs4 import BeautifulSoup
import feedparser
import sys
import requests

if __name__ == "__main__":
	print "What are you doing?  Why are you doing this?"
	sys.exit()

def getWindDirection(wind):
        if wind >= 348.75 or wind < 11.25:
                return "north"
        if wind >= 11.25 and wind < 33.75:
                return "north-northeast"
        if wind >= 33.75 and wind < 56.25:
                return "northeast"
        if wind >= 56.25 and wind < 78.75:
                return "east-northeast"
        if wind >= 78.75 and wind < 101.25:
                return "east"
        if wind >= 101.25 and wind < 123.75:
                return "east-southeast"
        if wind >= 123.75 and wind < 146.25:
                return "southeast"
        if wind >= 146.25 and wind < 168.75:
                return "south-southeast"
        if wind >= 168.75 and wind < 191.25:
                return "south"
        if wind >= 191.25 and wind < 213.75:
                return "south-southwest"
        if wind >= 213.75 and wind < 236.25:
                return "southwest"
        if wind >= 236.25 and wind < 258.75:
                return "west-southwest"
        if wind >= 258.75 and wind < 281.25:
                return "west"
        if wind >= 281.25 and wind < 303.75:
                return "west-northwest"
        if wind >= 303.75 and wind < 326.25:
                return "northwest"
        if wind >= 326.25 and wind < 348.75:
                return "north-northwest"

def getForecast(loc):
	weathers,timesFrom,timesTo,wtypes,precips,temps,wspeednames,wdirs,wspeeds = [[] for i in range(9)]
	loc = loc.replace('%','%25')
	loc = loc.split(' ')
	loc = '%20'.join(loc)
	url = 'http://api.openweathermap.org/data/2.5/forecast?q={0}&APPID={1}&mode=xml&units=imperial&cnt=3'.format(loc,WEATHER_API_KEY)
	try:
		xml = requests.get(url)
	except:
		return "~*404"
	xml = BeautifulSoup(xml.text, "lxml")
	location = xml.weatherdata.findAll("location")[0].findAll("name")[0]
	forecast = xml.weatherdata.findAll("forecast")[0]
	for i in forecast.findAll("time"):
		timesFrom.append(i["from"])
		timesTo.append(i["to"])
	for i in forecast.findAll("temperature"):
		temps.append(i["value"])
	for i in forecast.findAll("precipitation"):
		try:
			precips.append(" (" + i["value"] + "mm)")
		except KeyError:
			precips.append("none")
	for i in forecast.findAll("symbol"):
		wtypes.append(i["name"])
	for i in forecast.findAll("windspeed"):
		wspeednames.append(i["name"])
		wspeeds.append(round(float(i["mps"]) * 2.23694,2))
	for i in forecast.findAll("winddirection"):
		wdirs.append(getWindDirection(float(i["deg"])))
	for i in range(3):
		weathers.append([timesFrom[i],timesTo[i],wtypes[i],precips[i] if precips[i] != "none" else "",temps[i],wspeednames[i],wdirs[i],wspeeds[i],location])
	return weathers

def getWeather(loc):
	weather = {}
	loc = loc.replace('%','%25')
	loc = loc.split(' ')
	loc = "%20".join(loc)
	# Now let's get the weather...
	url = 'http://api.openweathermap.org/data/2.5/weather?q={0}&APPID={1}&mode=xml&units=imperial'.format(loc,WEATHER_API_KEY)
	parsed = feedparser.parse(url)
	parsed = parsed['feed']
	try:
		parsed_loc = parsed['city']['name']
	except:
		parsed_loc = "i broke something"
	try:
                parsed_clouds = parsed['clouds']
                parsed_clouds = parsed_clouds['name'].lower()
        except KeyError:
                parsed_clouds = "weather"
        try:
                parsed_temp = parsed['temperature']['value']
        except (KeyError, ValueError):
                parsed_temp = "a temperature in degrees"
        try:
                parsed_humidity = parsed['humidity']['value']
        except (KeyError, ValueError):
                parsed_humidity = "some "
        try:
                parsed_pressure = parsed['pressure']['value']
		parsed_pressure = str(round(float(parsed_pressure) * 0.000145038,2))  + 'psi'
        except (KeyError, ValueError):
                parsed_pressure = "at least 0"
        try:
                parsed_precip = parsed['precipitation']['mode']
		parsed_pamt = '0'
		if parsed_precip != 'no':
			parsed_pamt = parsed['precipitation']['value']
		else: parsed_precip = parsed_precip + 'ne'
        except (KeyError, ValueError):
                parsed_precip = "some crazy number of"
        try:
                parsed_sunrise = parsed['sun']['rise']
        except (KeyError, ValueError):
                parsed_sunrise = "sometime in the morning, i think,"
        try:
                parsed_sunset = parsed['sun']['set']
                if len(parsed_sunset) < 4: parsed_sunset = "just before night"
        except (KeyError, ValueError):
                parsed_sunset = "just before night"
        try:
                parsed_wind_speed = parsed['speed']['value']
		parsed_wind_speed = round(float(parsed_wind_speed) * 2.23694,2)
        except (KeyError, ValueError):
                parsed_wind_speed = "an unknown speed in"
        try:
                parsed_wind_direction = getWindDirection(int(parsed['direction']['value']))
        except (KeyError, ValueError):
                parsed_wind_direction = "some direction"

	weather['location'] = parsed_loc
        weather['cloudcover'] = parsed_clouds
        weather['temp'] = parsed_temp
        weather['humidity'] = parsed_humidity
        weather['pressure'] = parsed_pressure
        weather['visibility'] = parsed_precip
        weather['sunrise'] = parsed_sunrise
        weather['sunset'] = parsed_sunset
        weather['windchill'] = '({0}%)'.format(parsed_pamt)
        weather['windspeed'] = parsed_wind_speed
        weather['winddirection'] = parsed_wind_direction
	
	return weather
