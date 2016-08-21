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
from newspaper import Article, Config

ignoredWords = stopwords.words('english')
ignoredWords.extend(['said','could','want','told'])
ignoredWords = [x.lower() for x in ignoredWords]
tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
#TAGGER = StanfordPOSTagger('english-left3words-distsim.tagger')

def getWordFrequency(text, kws):
	words = []
	for sentence in text:
		for thing in sentence.split(' '):
			words.append(thing)
	wordFreq = nltk.FreqDist(words)
	wordFreq = sorted(wordFreq.items(), key=lambda x: (x[1],x[0]), reverse=True)
	wordFreq = wordFreq[:16]
	wordFreq = dict((a,b) for a, b in wordFreq)
	impWords = [w for i,w in enumerate(words) if w in kws]
	return wordFreq.keys(),impWords

def getPropCount(sentence):
	tags = pos_tag(sentence.split())
	props = [word for word,pos in tags if pos == "NNP"]
	return len(props)

def getBaseScore(text,title,kws):
	scores = {}
	cleanBody = []
	body = tokenizer.tokenize(text)
	for sentence in body:
		props = getPropCount(sentence)
		sentence = sentence.split(' ')
		cleanedSent = [w for w in sentence if w.lower() not in ignoredWords]
		cleanBody.append(" ".join(cleanedSent))
	i = 0
	wordFreq, impWrds = getWordFrequency(cleanBody,kws)
	for n,sentence in enumerate(cleanBody):
		if n == 0: firstSen = sentence.split(' ')
		sentence = sentence.split(' ')
		if "==" in sentence: continue # Attempt to skip code blocks
		scoreBonus = -n # Sentences earlier on in the article are generally better for summaries.
		cnt = 0
		wordlen = 0
		num = 0
		freq = 0
		impWords = 0
		for n,word in enumerate(sentence):
			# If the first word isn't an ASCII-based word, skip the sentence.
			if n == 0:				
				if not all(ord(c) < 128 for c in word):	
					break
			if word in wordFreq: freq += 1
			if word in impWrds: impWords += 1
			if word in title or word in firstSen: cnt += 1
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
		#	Multiply that by 16.5.  Divide by the sentence length.
		sharedWords = (cnt * 16.5)
		# Next, how many uncommon words does the sentence have?  
		#	Multiply that by 2.5.
		frequentWords = (freq * 2.5)
		# Next, let's try to determine how many keywords were used.
		#	Multiply that by 7.75
		importantWords = (impWords * 7.75)
		#importantWords = 0
		# Next, how many proper nounds does the sentence contain?
		#	Multiply that by 7.
		propNouns = (props * 7)
		# Finally, let's see how many numbers are in the sentence.  Numbers 
		#	indicate years or statistics, so those sentences should
		#	be rated higher.
		#	Multiply that by 3.5
		statWords = (num * 3.5)
		#--
		# Estimations
		#
		# The following equations are estimations based on common findings
		# in articles. As such, while they are still counted, they are 
		# weighted nuch less.
		#--
		# Fourth, how is the overall length of each word in the sentence?
		# Sentences with longer than average words might be more important.
		# Divide that average by 3.  Factor in the keywords.
		averageLen = float(int((wordlen / len(sentence)) / 3))
		# Finally, what's the overall length of the sentence in relation to
		#	the amount of common words it contains and the amount
		#	of words it shares with the headline?
		#	Divide that by 15.
		#	We SUBTRACT this from the score -- longer sentences don't
		#	necessarily make better ones.
		sentenceLen = float((float(impWords) + float(freq)) / len(sentence))
		# Add that all together to get the strength score of the sentence:
		scores[i] = (scoreBonus + sharedWords + propNouns + frequentWords + importantWords + statWords + averageLen) * sentenceLen
		i+=1
	return scores
			

def summary(title, text, kws):
	summItUp = []
	highScores = []
	title = title.split(' ')
	cleanedTitle = [w for w in title if w not in ignoredWords]
	scores = getBaseScore(text,cleanedTitle, kws)
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
	config = Config()
	config.MAX_KEYWORDS = 10
	if is_article:
		sumitup = {}
		b = Article(url=url,config=config)
		b.download()
		b.parse()
		b.nlp()
		sumNews = summary(b.title, b.text, b.keywords)
		sumTitle = b.title
		movies = b.movies[0] if len(b.movies) > 0 else "None"
		return sumNews,sumTitle,movies
	return "Nope"
