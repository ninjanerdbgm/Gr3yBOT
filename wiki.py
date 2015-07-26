#!/usr/bin/env python

import wikipedia
import sys

if __name__ == '__main__':
	print "This program cannot be run on its own!"
	sys.exit()

def wiki(query):
	try:
		search = wikipedia.search(query)
		result = getresults(query)
	except wikipedia.exceptions.PageError:
		return "-*e"
	except wikipedia.exceptions.WikipediaException:
		return "-*nf"
	if result[0] == "-*d":
		return result
	else:
		search = ", ".join(search)
		if len(search) > 1:
			result.append(search)
		return result

def getresults(query):
	try:
		results = wikipedia.page(query)
	except wikipedia.exceptions.DisambiguationError as e:
		e.options.insert(0, "-*d")
		return e.options
	results = [results.url]
	results.append(wikipedia.summary(query, sentences=3))
	return results
