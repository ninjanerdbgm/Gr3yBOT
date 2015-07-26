import requests
from bs4 import BeautifulSoup
import sys
import urllib, urllib2

if __name__ == "__main__":
	print "Can't do it, Tommy.  Can't do it."
	sys.exit()

def getWord(word):
	word = word.replace('%', '%25')
	word = word.split(' ')
	word = "%20".join(word)
	print 'http://www.urbandictionary.com/define.php?term={0}'.format(word)
	url = 'http://www.urbandictionary.com/define.php?term={0}'.format(word)
	r = requests.get(url)
	soup = BeautifulSoup(r.content)
	for breaks in soup.find_all('br'):
		breaks.extract()
	try:
		meaning = soup.find("div",attrs={"class":"meaning"}).text
		try:
			meaning = meaning.split('1. ')[1].split('2.')[0]
		except IndexError:
			meaning = meaning
	except AttributeError:
		meaning = None
	try:
		example = soup.find("div",attrs={"class":"example"}).text
	except AttributeError:
		example = None
	return meaning, example, url
