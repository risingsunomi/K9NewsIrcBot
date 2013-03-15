#!/usr/bin/env python

#suggestions
#<Sky> another suggestion
#<Sky> would be like PMs
#<Sky> say I want news with a keyword
#<Sky> examples "bulldozer" for amd bulldozer specific news
#<Sky> !subscribe "bulldozer" or some crap
#<Sky> search or subscribe, really
#<Sky> I think search would be smarter, yes

import time
import sched
import feedparser
from datetime import datetime
from concurrent import futures

rss_urls = ['http://english.aljazeera.net/Services/Rss/?PostingId=2007731105943979989',
            'http://feeds.bbci.co.uk/news/rss.xml',
            'http://rss.cnn.com/rss/cnn_topstories.rss',
            'http://rss.slashdot.org/Slashdot/slashdot',
            'http://www.hackinthebox.org/backend.php',
            'http://rss.dw-world.de/rdf/rss-de-all',
            'http://www3.nhk.or.jp/rss/news/cat0.xml',
            'http://www.france24.com/fr/monde/rss',
            'http://www.npr.org/rss/rss.php?id=1001',
            'http://feeds.reuters.com/reuters/topNews',
            'http://feeds.feedburner.com/newsyc150']

rss_sources = set(['aljazeera','bbc','cnn','reuters','slashdot','hitb','dw-world','nhk','france24','npr','reuters'])

rsched = sched.scheduler(time.time, time.sleep)

def getentries():
	entries = []
	with futures.ThreadPoolExecutor(max_workers=2) as executor:
		future_to_url = dict((executor.submit(feedparser.parse, url), url) for url in rss_urls)
		feeds = [future.result() for future in futures.as_completed(future_to_url)]
		#print [future.result() for future in futures.as_completed(future_to_url)]
		for feed in feeds:
			entries.extend(feed["items"])   
			try: 
				sorted_entries = sorted(entries, key=lambda entry: entry["date"], reverse=True)
			except KeyError:
				sorted_entries = sorted(entries, key=lambda entry: entry["updated"], reverse=True)
		print "========================================================================"
		print "feed items loaded @ " + datetime.now().strftime("%m/%w/%Y %H:%M:%S %Z")
		print "========================================================================"
		#print rss feed to channel slowly
	entsize = len(sorted_entries)
	print "========================================================================"
	print "Entry Size: " + str(entsize)
	print "========================================================================"
	print "\n"

	for i in range(0, entsize):
		#print sorted_entries[i]
		#print "\n"
		if sorted_entries[i]['summary_detail']['base'] == u'http://feeds.feedburner.com/newsyc150':
			print "{HACKER NEWS 100} %s - %s" % (sorted_entries[i]['title'],sorted_entries[i]['link'])
		else:
			for name in rss_sources:
				if sorted_entries[i]['link'].find(name) != -1:
					print "{%s} %s - %s" % (name.upper(),sorted_entries[i]['title'],sorted_entries[i]['link'])
				else:
					continue
				

		#if sorted_entries[i]['link'].find("bbc") != -1:
		#	print "[BBC WORLD NEWS] %s - %s" % (sorted_entries[i]['title'],tinyurl.create_one(sorted_entries[i]['link'])
		#elif sorted_entries[i]['link'].find("jazeera") != -1:
		#	print "[AJE] %s - %s" % (sorted_entries[i]['title'],tinyurl.create_one(sorted_entries[i]['link'])
		#elif sorted_entries[i]['link'].find("cnn") != -1:
		#	print "[CNN] %s - %s" % (sorted_entries[i]['title'],tinyurl.create_one(sorted_entries[i]['link'])
		#elif sorted_entries[i]['link'].find("reuters") != -1:
		#	print "[REUTERS BUSINESS] %s - %s" % (sorted_entries[i]['title'],tinyurl.create_one(sorted_entries[i]['link'])
		#elif sorted_entries[i]['link'].find("slashdot") != -1:
		#	print "[\.] %s - %s" % (sorted_entries[i]['title'],tinyurl.create_one(sorted_entries[i]['link'])
		#elif sorted_entries[i]['link'].find("wired") != -1:
		#	print "[WIRED] %s - %s" % (sorted_entries[i]['title'],tinyurl.create_one(sorted_entries[i]['link'])
		#elif sorted_entries[i]['link'].find("popsci") != -1:
		#	print "[POPULAR SCIENCE] %s - %s" % (sorted_entries[i]['title'],tinyurl.create_one(sorted_entries[i]['link'])
		#elif sorted_entries[i]['link'].find("telegraph") != -1:
		#	print "[TELEGRAPH] %s - %s" % (sorted_entries[i]['title'],tinyurl.create_one(sorted_entries[i]['link'])
		#elif sorted_entries[i]['link'].find("google") != -1:
		#	print "[GOOGLE NEWS] %s - %s" % (sorted_entries[i]['title'],tinyurl.create_one(sorted_entries[i]['link'])
		#elif sorted_entries[i]['link'].find("hitb") != -1:
	#		print "[HACK IN THE BOX] %s - %s" % (sorted_entries[i]['title'],tinyurl.create_one(sorted_entries[i]['link'])
	#	elif sorted_entries[i]['link'].find("dw-world") != -1:
	#		print "[DEUTSCHE WELLE ENG] %s - %s" % (sorted_entries[i]['title'],tinyurl.create_one(sorted_entries[i]['link'])
	#	elif sorted_entries[i]['link'].find("pcgamer") != -1:
	#		print "[PC GAMER] %s - %s" % (sorted_entries[i]['title'],tinyurl.create_one(sorted_entries[i]['link'])
	#	elif sorted_entries[i]['link'].find("eluniversal") != -1:
	#		print "[El Universal] %s - %s" % (sorted_entries[i]['title'],tinyurl.create_one(sorted_entries[i]['link'])
	#	elif sorted_entries[i]['link'].find("nhk") != -1:
	#		print "[NHK] %s - %s" % (sorted_entries[i]['title'],tinyurl.create_one(sorted_entries[i]['link'])
	#	elif sorted_entries[i]['link'].find("france24") != -1:
	#		print "[FRANCE24] %s - %s" % (sorted_entries[i]['title'],tinyurl.create_one(sorted_entries[i]['link'])
	#	elif sorted_entries[i]['link'].find("chosun") != -1:
	#		print "[CHOSUN] %s - %s" % (sorted_entries[i]['title'],tinyurl.create_one(sorted_entries[i]['link'])
	#	elif sorted_entries[i]['link'].find("theregister") != -1:
	#		print "[THEREGISTER] %s - %s" % (sorted_entries[i]['title'],tinyurl.create_one(sorted_entries[i]['link'])
	#	elif sorted_entries[i]['link'].find("gameinformer") != -1:
	#		print "[GAME INFORMER] %s - %s" % (sorted_entries[i]['title'],tinyurl.create_one(sorted_entries[i]['link'])  
		time.sleep(15)
	rsched.enter(5, 1, getentries, ())
	
rsched.enter(5, 1, getentries, ())
rsched.run()
