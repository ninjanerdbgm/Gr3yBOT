#!usr/bin/env python

import google
import urllib2
import random
from operator import itemgetter
from goose import Goose

def retFirstResult(search):
	result = {}
	res = google.search(search,stop=0)
	for i in res:
		o = urllib2.build_opener(urllib2.HTTPCookieProcessor())
		try:
			r = o.open(i)
		except:
			return "~*403"
		html = r.read()
		g = Goose()
		a = g.extract(raw_html=html)
		result["title"] = a.title
		result["url"] = i
		result["blob"] = getBlob(search,a.cleaned_text)
		return result

def retRandomResult(search):
	result = {}
	res = google.search(search)
	for c,i in enumerate(res):
		if c > 15: break
		if c % 6 == random.randint(0,5): 
	                g = Goose()
	                a = g.extract(raw_html=google.get_page(i))
			result["resNum"] = c
	                result["title"] = a.title
	                result["url"] = i
	                result["blob"] = getBlob(search,a.cleaned_text)
		else: 
			continue
	if len(result) == 0:
		for i in res:
	                g = Goose()
	                a = g.extract(raw_html=google.get_page(i))
	                result["title"] = a.title
	                result["url"] = i
	                result["blob"] = getBlob(search,a.cleaned_text)
	                return result
        return result

def retResults(search):
	result = {}
	res = google.search(search,stop=2)
	for i,v in enumerate(res):
		if len(result) > 2: break
		result[i] = {}
                o = urllib2.build_opener(urllib2.HTTPCookieProcessor())
                try:
                        r = o.open(v)
                except:
                        continue
                html = r.read()
                g = Goose()
                a = g.extract(raw_html=html)
                result[i]["title"] = a.title
                result[i]["url"] = v
        return result


def getBlob(search, text):
	matches = {}
	text = text.replace("\n"," ")
	text = text.split(" ")
	try:
		while text.index("") >= 0:
			text.remove(text[text.index("")])
	except ValueError:
		for i,v in enumerate(search.split()):			
			matches[i] = [a for a, b in enumerate(text) if (str(b).strip().lower() == str(v).strip().lower() or (a+1 < len(text) and "".join(itemgetter(a,a+1)(text)).strip().lower() == str(v).strip().lower()))]
		blob = ""
		for words in matches:
			for index in  matches[words]:
				blob += "..." + " ".join(text[index-4:index+15]) + "... | "
		blob = blob[:len(blob) - 3]
		return blob
