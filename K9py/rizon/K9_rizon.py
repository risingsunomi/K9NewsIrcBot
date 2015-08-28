#!/usr/bin/env python
# -*- coding: utf-8 -*-
#---------------------------------------------------
#              K-9 News Irc Stream Bot             |
#     drwho ~ I Love To Party Fake Industries ©    |
#---------------------------------------------------
# Version 0.3                                      |
#---------------------------------------------------
# add in python twitter and make k-9news account
# change: no oyoyo

import time, threading, feedparser, tinyurl
import socket, re, sys, os, getpass, time, codecs
from datetime import datetime
from concurrent import futures
from HTMLParser import HTMLParser
from random import shuffle
from pymongo import MongoClient
from bson.objectid import ObjectId

import threading

class MLStripper(HTMLParser):
	def __init__(self):
		self.reset()
		self.fed = []
	def handle_data(self, d):
		self.fed.append(d)
	def get_data(self):
		return ''.join(self.fed)

def strip_tags(html):
	s = MLStripper()
	try:
		s.feed(html)
		return s.get_data()
	except:
		return html

class RSSStream:
	def __init__(self, client):
		# RSS information
		self.rss_urls = ['http://english.aljazeera.net/Services/Rss/?PostingId=2007731105943979989',
					'http://www.theregister.co.uk/headlines.atom',
					'http://feeds.bbci.co.uk/news/rss.xml',
					'http://rss.slashdot.org/Slashdot/slashdot',
					'http://www.hackinthebox.org/backend.php',
					'http://www.npr.org/rss/rss.php?id=1001',
					'http://feeds.reuters.com/reuters/topNews',
					'http://feeds.feedburner.com/newsyc150',
					'http://rt.com/rss/news/',
					'http://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml',
					'http://rssfeeds.usatoday.com/usatoday-NewsTopStories',
					'http://www.washingtonpost.com/rss/world',
					'http://hosted.ap.org/lineups/USHEADS-rss_2.0.xml?SITE=SCAND&SECTION=HOME',
					'https://news.google.com/?output=rss',
					'http://www.drudgereportfeed.com/',
					'http://edition.presstv.ir/rss/',
					'http://www.scmp.com/rss/91/feed',
					'http://feeds.arstechnica.com/arstechnica/index',
					'http://feeds.feedburner.com/TheHackersNews',
					'http://english.chosun.com/site/data/rss/rss.xml',
					'http://vuxml.freebsd.org/freebsd/rss.xml']
		
		self.rss_sources = set(['aljazeera.net',
							'bbc.com',
							'bbc.co.uk',
							'reuters.com',
							'slashdot.org', 
							'npr.org',
							'theregister.co.uk',
							'theregister.com',
							'rt.com', 
							'hitb',
							'nytimes.com',
							'usatoday.com',
							'washingtonpost.com',
							'ap.org',
							'arstechnica.com',
							'chosun.com',
							'scmp.com'])

		self.rss_titles = {
			'aljazeera.net': 'Al Jazeera',
			'aljazeera.com': 'Al Jazeera',
			'bbc.com': 'BBC News',
			'bbc.co.uk': 'BBC News',
			'bbci.co.uk': 'BBC News',
			'reuters.com': 'Reuters',
			'slashdot.org': 'Slashdot',
			'npr.org': 'National Public Radio',
			'theregister.co.uk': 'The Register',
			'theregister.com': 'The Register',
			'rt.com': 'Russia Today',
			'hitb': 'HITB',
			'nytimes.com': 'New York Times',
			'usatoday.com': 'USA Today',
			'washingtonpost.com': 'Washington Post',
			'ap.org': 'Associated Press',
			'arstechnica.com': 'Ars Technica',
			'chosun.com': 'The Chosun Ilbo',
			'scmp.com': 'South China Morning Post',
		}

		self.client = client

	def get_feeds(self):
		with futures.ThreadPoolExecutor(max_workers=13) as executor:
			future_to_url = dict((executor.submit(feedparser.parse, url), url) for url in self.rss_urls)     
			feeds = [future.result() for future in futures.as_completed(future_to_url)]
			for feed in feeds:
				self.client.entries.extend(feed["items"])   
				try: 
					self.client.sorted_entries = sorted(self.client.entries, key=lambda entry: entry["date"], reverse=True)
				except KeyError:
					self.client.sorted_entries = sorted(self.client.entries, key=lambda entry: entry["updated"], reverse=True)

			shuffle(self.client.sorted_entries)
			
			print "========================================================================"
			print "feed items loaded @ " + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
			print "========================================================================"
		
		self.client.entsize = len(self.client.sorted_entries)
		print "========================================================================"
		print "Entry Size: " + str(self.client.entsize)
		print "========================================================================"

	def print_article(self):
		rssitem = {}
		i = 0
		if not self.client.sorted_entries:
			self.get_feeds()

		summary_detail = self.client.sorted_entries[i].get('summary_detail', None)
		if summary_detail is not None and summary_detail['base'] == u'http://feeds.feedburner.com/newsyc150':
			if 'published_parsed' in self.client.sorted_entries[i]:
				dt = datetime.fromtimestamp(time.mktime(self.client.sorted_entries[i]['published_parsed']))
				rssitem['date_published'] = dt.strftime('%Y-%m-%d %H:%M:%S')
			else:
				rssitem['date_published'] = None

			rssitem['news_source'] = "hacker news 100"
			rssitem['title'] = self.client.sorted_entries[i]['title']
			rssitem['url'] = tinyurl.create_one(self.client.sorted_entries[i]['link'])
			rssitem['description'] = strip_tags(self.client.sorted_entries[i]['description'])
			rssitem['rss_raw'] = self.client.sorted_entries[i]
			rssitem['scrape_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

			self.client.sorted_entries.pop(i)

			self.client.entsize = len(self.client.sorted_entries)
			print "========================================================================"
			print "Entry Size: " + str(self.client.entsize)
			print "========================================================================"
			
		else:
			namefound = False
			for name in self.rss_sources:
				print name
				if self.client.sorted_entries[i]['link'].find(name) != -1:
					if 'author_detail' in self.client.sorted_entries[i]:
						try:
							rssitem['news_author'] = self.client.sorted_entries[i]['author_detail']['name']
						except KeyError:
							rssitem['news_author'] = None
					else:
						rssitem['news_author'] = None

					if 'published_parsed' in self.client.sorted_entries[i]:
						dt = datetime.fromtimestamp(time.mktime(self.client.sorted_entries[i]['published_parsed']))
						rssitem['date_published'] = dt.strftime('%Y-%m-%d %H:%M:%S')
					else:
						rssitem['date_published'] = None

					if 'media_thumbnail' in self.client.sorted_entries[i]:
						rssitem['media_thumbnail'] = self.client.sorted_entries[i]['media_thumbnail']
					else:
						rssitem['media_thumbnail'] = None

					rssitem['news_source'] = self.rss_titles[name]
					if self.client.sorted_entries[i]['description'] != None:
						rssitem['description'] = strip_tags(self.client.sorted_entries[i]['description'])
					else:
						rssitem['description'] = self.client.sorted_entries[i]['description']

					rssitem['title'] = self.client.sorted_entries[i]['title']
					rssitem['url'] = tinyurl.create_one(self.client.sorted_entries[i]['link'])
					rssitem['rss_raw'] = self.client.sorted_entries[i]
					rssitem['scrape_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

					# save rss item
					rsstmp = {
						'news_source': rssitem['news_source'],
						'description': rssitem['description'],
						'title': rssitem['title'],
						'url': rssitem['url'],
						'scrape_date': rssitem['scrape_date'],
						'news_author': rssitem['news_author'],
						'date_published': rssitem['date_published'],
						'media_thumbnail': rssitem['media_thumbnail']
					}
					
					self.save_rss(rsstmp)
					print rsstmp
					del rsstmp
					
					for c in self.client.channels:
						self.client.say("\002[%s] %s \037%s" % (rssitem['news_source'], rssitem['title'], rssitem['url']), c)
						self.client.rssitem = rssitem
						print rssitem
						print "\n\n"
					namefound = True
					time.sleep(60)
					break
				else:
					namefound = False
					continue

			if namefound == False:
				if 'author_detail' in self.client.sorted_entries[i]:
					rssitem['news_author'] = self.client.sorted_entries[i]['author_detail']['name']
				else:
					rssitem['news_author'] = None

				if 'published_parsed' in self.client.sorted_entries[i]:
					dt = datetime.fromtimestamp(time.mktime(self.client.sorted_entries[i]['published_parsed']))
					rssitem['date_published'] = dt.strftime('%Y-%m-%d %H:%M:%S')
				else:
					rssitem['date_published'] = None

				if 'media_thumbnail' in self.client.sorted_entries[i]:
					rssitem['media_thumbnail'] = self.client.sorted_entries[i]['media_thumbnail']
				else:
					rssitem['media_thumbnail'] = None

				rssitem['news_source'] = "K9 World News"
				
				rss_description = self.client.sorted_entries[i].get('summary_detail', None)
				if rss_description is not None:
					rssitem['description'] = strip_tags(rss_description)
					rssitem['description'] = rssitem['description'][:100] + '..' if len(rssitem['description']) > 100 else rssitem['description']
				else:
					rssitem['description'] = rss_description

				rssitem['title'] = self.client.sorted_entries[i]['title']
				rssitem['url'] = self.client.sorted_entries[i]['link']
				rssitem['rss_raw'] = self.client.sorted_entries[i]
				rssitem['scrape_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

				# save rss item
				rsstmp = {
					'news_source': rssitem['news_source'],
					'description': rssitem['description'],
					'title': rssitem['title'],
					'url': rssitem['url'],
					'scrape_date': rssitem['scrape_date'],
					'news_author': rssitem['news_author'],
					'date_published': rssitem['date_published'],
					'media_thumbnail': rssitem['media_thumbnail']
				}

				self.save_rss(rsstmp)
				print rsstmp
				del rsstmp
				
				for c in self.client.channels:
					self.client.say("\002[%s] %s \037%s" % (rssitem['news_source'], rssitem['title'], rssitem['url']), c)
					self.client.rssitem = rssitem
					print rssitem
					print "\n\n"
				
				time.sleep(60)

			self.client.sorted_entries.pop(i)
			self.client.entsize = len(self.client.sorted_entries)
			print "========================================================================"
			print "Entry Size: " + str(self.client.entsize)
			print "========================================================================"

	def save_rss(self, rssdata):
		mg_cnn = MongoClient()
		mg_db = mg_cnn["qnews"]

		if "rss_data" not in mg_db.collection_names():
			mg_db.create_collection("rss_data")

		if mg_db["rss_data"].find_one(rssdata):
			mgtd = mg_db["rss_data"].find_one(rssdata)
			mg_db["rss_data"].update({"_id": ObjectId(mgtd["_id"])}, {"$set": rssdata})
		else:
			mg_db["rss_data"].insert(rssdata)

	def wait_print(self):
		print datetime.now()

class IRCClient:
	
	# irc information
	socket = None
	connected = False
	joined = False
	registered = False
	nickname = 'WNews'
	channels = ['#worldnews']
	network = 'irc.rizon.net'

	# mysql information
	host = 'localhost'
	dbuser = ''
	chatdb = None
	dbpassw = None
	dbname = None 

	def __init__(self):
		#self.dbpassw = getpass.getpass('[MySQL Pass] ')
		self.socket = socket.socket()
		self.socket.connect((self.network, 6667))
		self.send("NICK %s" % self.nickname)
		self.send("USER %(nick)s %(nick)s %(nick)s :%(nick)s" % {'nick':self.nickname})
		self.rss_stream = RSSStream(self)
		self.stream_started = False
		self.ctx = {}
		self.entries = []
		self.entsize = None
		self.sorted_entries = None
		self.rssitem = None
		self.rss_loaded = False

		
		while True:
			buf = self.socket.recv(4096)
			lines = buf.split("\n")
			for data in lines:
				data = str(data).strip()
				if data == '':
					continue
				#print "I<", data

				# server ping/pong?
				if data.find('PING') != -1:
					n = data.split(':')[1]
					print self.rss_stream.wait_print()
					self.send('PONG :' + n)
					if self.connected == False:
						self.perform()
						self.connected = True
					if self.connected and self.stream_started:
						self.rss_stream.print_article()
					continue

				args = data.split(None, 3)
				if len(args) != 4:
					continue
				self.ctx['sender'] = args[0][1:]
				self.ctx['type']   = args[1]
				self.ctx['target'] = args[2]
				self.ctx['msg']    = args[3][1:]

				# check to start rss
				if self.ctx['type'] == '366':
					self.joined = True

				# register
				print self.ctx['type']
				print self.ctx['sender']
				print self.ctx['target']
				print self.ctx['msg']
				#if self.ctx['type'] == '332' and self.registered is False:
					#print 'PRIVMSG NickServ@network.net :IDENTIFY %s' % self.register_pass
					#self.send('PRIVMSG NickServ@network.net :IDENTIFY %s' % self.register_pass)
					#self.registered = True

				# whom to reply?
				target = self.ctx['target']
				if self.ctx['target'] == self.nickname:
					target = self.ctx['sender'].split("!")[0]


				# some basic commands
				if self.ctx['msg'] == '!test':
					self.say('fuck off', target)


				# directed to the bot?
				if self.ctx['type'] == 'PRIVMSG' and (self.ctx['msg'].lower()[0:len(self.nickname)] == self.nickname.lower() or self.ctx['target'] == self.nickname):
					# something is speaking to the bot
					query = self.ctx['msg']
					if self.ctx['target'] != self.nickname:
						query = query[len(self.nickname):]
						query = query.lstrip(':,;. ')

					# do something intelligent here, like query a chatterbot
					#print 'someone spoke to us: ', query
					#self.say('alright :|', target)

				if self.connected and self.joined and not self.stream_started:
					self.rss_stream.get_feeds()
					self.stream_started = True
					self.rss_stream.print_article()
					continue

				if self.connected and self.joined and self.stream_started:
					self.rss_stream.print_article()
					continue

	# IRC message protocol methods
	def send(self, msg):
		print "I>",msg.encode('utf-8')
		self.socket.send(bytearray(msg+"\r\n", "utf-8"))

	def say(self, msg, to):
		self.send("PRIVMSG %s :%s" % (to, msg))

	# long text chunker
	def chunks(s, n):
		"""Produce `n`-character chunks from `s`."""
		for start in range(0, len(s), n):
			yield s[start:start+n]
	
	# MySQL methods
	def mysql_connect(self):
		#db=mysql.connector.connect(user=self.dbuser, passwd=self.dbpassw, database=self.dbname, use_unicode=True, charset='utf8')
		self.chatdb = db
		return db

	# bot methods
	def shutdown(self, channel=None):
		if channel:
			self.send("QUIT %s" % channel)
		
		if self.chatdb:
			self.chatdb.close()
		
		self.socket.close()
		sys.exit()
	
	def perform(self):
		#self.send("PRIVMSG R : Register <>"
		#self.send("PRIVMSG R : Login <>")
		self.send("MODE %s +x" % self.nickname)
		for c in self.channels:
			self.send("JOIN %s" % c)
			print 'News Stream Started'


if __name__ == '__main__':
	IRCClient()
