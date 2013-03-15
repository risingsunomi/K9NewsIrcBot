#!/usr/bin/env python
# -*- coding: utf-8 -*-
#---------------------------------------------------
#              K-9 News Irc Stream Bot             |
#  RisingSunomi ~ I Love To Pary Fake Industries © |
#---------------------------------------------------
# Version 0.1                                      |
#---------------------------------------------------

import time
import sched
import logging
import feedparser
import tinyurl
import logging
from datetime import datetime
from concurrent import futures
from oyoyo.client import IRCClient
from oyoyo.cmdhandler import DefaultCommandHandler
from oyoyo import helpers

# IRC information
logging.basicConfig(level=logging.DEBUG)
nickname = "K-9"
channel = "#worldnews"
host = "irc.cyberdynesystems.net"

# RSS information
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

# setting up scheduler
rsched = sched.scheduler(time.time, time.sleep)     

# starting news stream
def news_stream(cli):
    entries = []
    with futures.ThreadPoolExecutor(max_workers=13) as executor:
        future_to_url = dict((executor.submit(feedparser.parse, url), url) for url in rss_urls)     
        feeds = [future.result() for future in futures.as_completed(future_to_url)]
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
    print " BEGIN STREAM =========================================================="
    print "\n"

    for i in range(0, entsize):
        if sorted_entries[i]['summary_detail']['base'] == u'http://feeds.feedburner.com/newsyc150':
            print "{hacker news 100} %s - %s\n" % (sorted_entries[i]['title'],sorted_entries[i]['link'])
            helpers.msg(cli, channel, "{HACKER NEWS 100} %s - %s\n" % (sorted_entries[i]['title'],tinyurl.create_one(sorted_entries[i]['link'])))
        else:
            for name in rss_sources:
                if sorted_entries[i]['link'].find(name) != -1:
                    print "{%s} %s - %s\n" % (name,sorted_entries[i]['title'],sorted_entries[i]['link'])
                    helpers.msg(cli, channel, "{%s} %s - %s\n" % (name,sorted_entries[i]['title'],tinyurl.create_one(sorted_entries[i]['link'])))
                else:
                    continue

        # sleep for 10 seconds
        time.sleep(10)

    rsched.enter(5, 1, newsfeed, (cli,))   


def connect_callback(cli):
    logging.basicConfig(level=logging.DEBUG)
    #helpers.identify(cli, "a-password")
    helpers.join(cli, channel)
    rsched.enter(5, 1, news_stream, (cli,))
    rsched.run()

# the leash for the dog or the IRC command handler
class k9leash(DefaultCommandHandler):
    def privmsg(self, nick, chan, msg):
        print "[%s] %s in %s said: %s" % (datetime.now().strftime("%m/%w/%Y %H:%M:%S %Z"), nick, chan, msg)

cli = IRCClient(k9leash, host=host, port=6667, nick=nickname, connect_cb=connect_callback)
connection = cli.connect()
while True:
    connection.next()
