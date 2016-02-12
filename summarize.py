#!/usr/bin/env python

from gr3ybot_settings import SUMMARY_COUNT
from urldetect import *
from urlparse import urlparse
import zlib
import nltk
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
from nltk.tag import pos_tag
#from nltk.tag.stanford import StanfordPOSTagger
import re
import operator
import urllib2
from cookielib import CookieJar
from goose import Goose

ignoredWords = stopwords.words('english')
tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
#TAGGER = StanfordPOSTagger('english-left3words-distsim.tagger')

def getWordFrequency(text):
	words = []
	# Count root words for better accuracy.
	roots = SnowballStemmer("english", ignore_stopwords=True)
	for sentence in text:
		for thing in sentence.split(' '):
			thing = roots.stem(thing)
			if thing not in ignoredWords: words.append(thing)
	wordFreq = nltk.FreqDist(words)
	return wordFreq.keys()

def getPropCount(sentence):
	tags = pos_tag(sentence.split())
	props = [word for word,pos in tags if pos == "NNP"]
	return len(props)

def getBaseScore(text,title):
	scores = {}
	cleanBody = []
	body = tokenizer.tokenize(text)
	for sentence in body:
		props = getPropCount(sentence)
		sentence = sentence.split(' ')
		cleanedSent = [w for w in sentence if w not in ignoredWords]
		cleanBody.append(" ".join(cleanedSent))
	i = 0
	freqWords = getWordFrequency(cleanBody)
	for sentence in cleanBody:
		sentence = sentence.split(' ')
		if "==" in sentence: continue # Attempt to skip code blocks
		cnt = 0
		wordlen = 0
		freq = 0
		num = 0
		impWords = 0
		for word in sentence:
			if word in freqWords[:30]: freq += 1
			if word in freqWords[-30:]: impWords += 1
			if word in title: cnt += 1
			try:
				if int(word.replace(",", "").replace(".", "").replace("$", "")) > 0: num += 1
				if word.find("illion") or word in ["one","two","three","four","five","six","seven","eight","nine","ten"]: num += 1
			except:
				pass
			wordlen += len(word)
		#--
		# Here is where I determine the strength of the sentence. This is broken down into 
		# a few sections to make it easier to read.
		# NOTE: All of the following scores exclude stopwords.
		#	--	--	--	--	--	--	--	--	--	--
		# First, how many words in the sentence share words with the headline?
		#	Multiply that by 8.
		sharedWords = (cnt * 8)
		# Next, how many common important words does the sentence have?  
		#	Multiply that by 6.
		frequentWords = (freq * 6)
		# Next, let's try to determine how many infrequent words were used.
		#	Multiply that by 4
		importantWords = (impWords * 4)
		# Next, how many proper nounds does the sentence contain?
		#	Multiply that by 5.
		propNouns = (props * 5)
		# Finally, let's see how many numbers are in the sentence.  Numbers 
		#	indicate years or statistics, so those sentences should
		#	be rated higher.
		#	Multiply that by 8
		statWords = (num * 8)
		#--
		# Estimations
		#
		# The following equations are estimations based on common findings
		# in articles. As such, while they are still counted, they are 
		# weighted nuch less.
		#--
		# Fourth, how is the overall length of each word in the sentence?
		# Sentences with longer than average words might be more important.
		# Divide that average by 3.
		averageLen = int((wordlen / len(sentence)) / 3)
		# Finally, what's the overall length of the sentence?
		#	Divide that by 7.
		sentenceLen = int((len(sentence) / 7))
		# Add that all together to get the strength score of the sentence:
		scores[i] = sharedWords + propNouns + frequentWords + importantWords + statWords + averageLen + sentenceLen
		i+=1
	return scores
			

def summary(title, text):
	summItUp = []
	highScores = []
	title = title.split(' ')
	cleanedTitle = [w for w in title if w not in ignoredWords]
	scores = getBaseScore(text,cleanedTitle)
	sortedScores = sorted(scores.items(), key=operator.itemgetter(1), reverse=True)
	for thing in sortedScores:
		scoreKey = int(str(thing).split(',')[0].split('(')[1])
		highScores.append(scoreKey)
        body = tokenizer.tokenize(text)
	sentences = SUMMARY_COUNT
	for i in range(SUMMARY_COUNT):
		try:
			summItUp.append(body[highScores[i]].encode('utf-8', 'ignore'))
		except:
			sentences-=1	
	return summItUp
	

def whoHasTimeToRead(url):
	is_article = valid_url(url, verbose=True)
	if is_article:
		sumitup = {}
		g = Goose({'enable_image_fetching':False})
		b = g.extract(url=url)
		if b.cleaned_text is None or len(b.cleaned_text) < 6:
			return "~~HTTPS~~"
		sumNews = summary(b.title, b.cleaned_text)
		sumTitle = b.title
		return sumNews,sumTitle
	return "Nope"

def readingIsFun(url):
	sumitup = {}
	g = Goose({'enable_image_fetching':False})
	yummy = CookieJar()
	cookieSesh = urllib2.build_opener(urllib2.HTTPCookieProcessor(yummy))
	raw_html = cookieSesh.open(url).read()
	raw_html = zlib.decompress(raw_html, 16 + zlib.MAX_WBITS)
	b = g.extract(url=url, raw_html=raw_html)
	sumNews = summary(b.title, b.cleaned_text)
	sumTitle = b.title
	return sumNews,sumTitle
