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

import time, threading, feedparser
import socket, re, sys, os, getpass, time, codecs
from datetime import datetime
from concurrent import futures
from HTMLParser import HTMLParser
from random import shuffle
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
	s.feed(html)
	return s.get_data()

class RSSStream:
	def __init__(self, client):
		# RSS information
		self.rss_urls = ['http://english.aljazeera.net/Services/Rss/?PostingId=2007731105943979989',
					'http://www.theregister.co.uk/headlines.atom',
					'http://feeds.bbci.co.uk/news/rss.xml',
					'http://www.ft.com/rss/home/uk',
					'http://rss.slashdot.org/Slashdot/slashdot',
					'http://www.hackinthebox.org/backend.php',
					'http://www.npr.org/rss/rss.php?id=1001',
					'http://feeds.reuters.com/reuters/topNews',
					'http://feeds.feedburner.com/newsyc150',
					'http://rt.com/rss/news/',
					'http://www.economista.com.mx/ultimas-noticias/rss',
					'http://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml',
					'http://rssfeeds.usatoday.com/usatoday-NewsTopStories',
					'http://www.washingtonpost.com/rss/world',
					'http://hosted.ap.org/lineups/USHEADS-rss_2.0.xml?SITE=SCAND&SECTION=HOME']
		
		self.rss_sources = set(['aljazeera.net',
							'bbc.com',
							'reuters.com',
							'slashdot.org', 
							'npr.org',
							'theregister.co.uk', 
							'rt.com', 
							'hitb',
							'nytimes.com',
							'usatoday.com',
							'washingtonpost.com',
							'ap.org'])

		self.rss_titles = {
			'aljazeera.net': 'Al Jazeera',
			'bbc.com': 'BBC News',
			'bbci.co.uk': 'BBC News',
			'reuters.com': 'Reuters',
			'slashdot.org': 'Slashdot',
			'npr.org': 'National Public Radio',
			'theregister.co.uk': 'The Register',
			'rt.com': 'Russia Today',
			'hitb': 'HITB',
			'nytimes.com': 'New York Times',
			'usatoday.com': 'USA Today',
			'washingtonpost.com': 'Washington Post',
			'ap.org': 'Associated Press'
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
		# get media:thumbnail, description, pubDate (change to mysql datetime format)
		rssitem = {}
		i = 0

		#print self.sorted_entries[i]
		if self.client.sorted_entries[i]['summary_detail']['base'] == u'http://feeds.feedburner.com/newsyc150':
			if 'published_parsed' in self.client.sorted_entries[i]:
				dt = datetime.fromtimestamp(time.mktime(self.client.sorted_entries[i]['published_parsed']))
				rssitem['date_published'] = dt.strftime('%Y-%m-%d %H:%M:%S')
			else:
				rssitem['date_published'] = None

			rssitem['news_source'] = "hacker news 100"
			rssitem['title'] = self.client.sorted_entries[i]['title']
			rssitem['url'] = self.client.sorted_entries[i]['link']
			rssitem['description'] = strip_tags(self.client.sorted_entries[i]['description'])
			rssitem['rss_raw'] = self.client.sorted_entries[i]
			rssitem['scrape_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

			self.client.sorted_entries.pop(i)
			
		else:
			for name in self.rss_sources:
				print name
				if self.client.sorted_entries[i]['link'].find(name) != -1:
					if 'author_detail' in self.client.sorted_entries[i]:
						rssitem['news_author'] = self.client.sorted_entries[i]['author_detail']
					else:
						rssitem['news_author'] = None

					if 'published_parsed' in self.client.sorted_entries[i]:
						dt = datetime.fromtimestamp(time.mktime(self.client.sorted_entries[i]['published_parsed']))
						rssitem['date_published'] = dt.strftime('%Y-%m-%d %H:%M:%S')
					else:
						rssitem['date_published'] = None

					if 'media_thumbnail' in self.client.sorted_entries[i]:
						rssitem['media_thumbnail'] = str(self.client.sorted_entries[i]['media_thumbnail'])
					else:
						rssitem['media_thumbnail'] = None

					rssitem['news_source'] = self.rss_titles[name]
					rssitem['description'] = strip_tags(self.client.sorted_entries[i]['description'])
					rssitem['title'] = self.client.sorted_entries[i]['title']
					rssitem['url'] = self.client.sorted_entries[i]['link']
					rssitem['rss_raw'] = self.client.sorted_entries[i]
					rssitem['scrape_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

					# remove article already printed
					print rssitem
					
					for c in self.client.channels:
						self.client.say(" ", c)
						self.client.say("\002[%s] %s" % (rssitem['news_source'], rssitem['title']), c)
						self.client.say(" ", c)
						self.client.say("\035%s" % rssitem['description'], c)
						self.client.say(" ", c)
						self.client.say("\037%s" % rssitem['url'], c)
						self.client.say(" ", c)
						self.client.rssitem = rssitem
						print rssitem
						print "\n\n"
					
					time.sleep(40)
				else:
					continue

			self.client.sorted_entries.pop(i)

class IRCClient:
	
	# irc information
	socket = None
	connected = False
	registered = False
	nickname = 'WNews'
	channels = ['#worldnews']
	network = raw_input('IRC Network: ')

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
				print "I<", data

				# server ping/pong?
				if data.find('PING') != -1:
					n = data.split(':')[1]
					self.send('PONG :' + n)
					if self.connected == False:
						self.perform()
						self.connected = True
					continue

				args = data.split(None, 3)
				if len(args) != 4:
					continue
				self.ctx['sender'] = args[0][1:]
				self.ctx['type']   = args[1]
				self.ctx['target'] = args[2]
				self.ctx['msg']    = args[3][1:]

				# register
				#print self.ctx['type']
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

				if self.connected and not self.stream_started:
					self.rss_stream.get_feeds()
					self.stream_started = True
					self.rss_stream.print_article()
					continue

				if self.connected and self.stream_started:
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