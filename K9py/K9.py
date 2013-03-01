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

#suggestions
#<Sky> another suggestion
#<Sky> would be like PMs
#<Sky> say I want news with a keyword
#<Sky> examples "bulldozer" for amd bulldozer specific news
#<Sky> !subscribe "bulldozer" or some crap
#<Sky> search or subscribe, really
#<Sky> I think search would be smarter, yes

logging.basicConfig(level=logging.DEBUG)
nickname = "K-9"
channel = "#worldnews"
host = "irc.rizon.net"
#get rss entries
rss_urls = ['http://english.aljazeera.net/Services/Rss/?PostingId=2007731105943979989',
            'http://feeds.bbci.co.uk/news/rss.xml',
            'http://rss.cnn.com/rss/cnn_topstories.rss',
            'http://feeds.reuters.com/reuters/businessNews',
            'http://rss.slashdot.org/Slashdot/slashdot',
            'http://feeds.wired.com/wired/index?format=xml',
            'http://popsci.com/rss.xml',
            'http://www.telegraph.co.uk/news/picturegalleries/worldnews/rss',
            'http://www.hackinthebox.org/backend.php',
            'http://rss.dw-world.de/rdf/rss-en-all',
            'http://www3.nhk.or.jp/rss/news/cat0.xml',
            'http://www.france24.com/fr/monde/rss']
rsched = sched.scheduler(time.time, time.sleep)     

#for rizon
def newsfeed(cli):
    entries = []
    with futures.ThreadPoolExecutor(max_workers=13) as executor:
        future_to_url = dict((executor.submit(feedparser.parse, url), url) for url in rss_urls)     
        feeds = [future.result() for future in futures.as_completed(future_to_url)]
        for feed in feeds:
            entries.extend(feed["items"])
            try:    
                sorted_entries = sorted(entries, key=lambda entry: entry["date_parsed"], reverse=True)
            except KeyError:
                continue
        print "========================================================================"
        print "feed items loaded @ " + datetime.now().strftime("%m/%w/%Y %H:%M:%S %Z")
        print "========================================================================"
         #print rss feed to channel slowly
    entsize = len(sorted_entries)
    print "========================================================================"
    print "Entry Size: " + str(entsize)
    print "========================================================================"
    print "\n"

    # old method of news posting - lost new code from hd whipe -- will rewrite
    for i in range(0, entsize):
        if sorted_entries[i]['link'].find("bbc") != -1:
           helpers.msg(cli, channel, "[BBC WORLD NEWS] %s - %s" % (sorted_entries[i]['title'],tinyurl.create_one(sorted_entries[i]['link'])))
        elif sorted_entries[i]['link'].find("jazeera") != -1:
             helpers.msg(cli, channel, "[AJE] %s - %s" % (sorted_entries[i]['title'],tinyurl.create_one(sorted_entries[i]['link'])))
        elif sorted_entries[i]['link'].find("cnn") != -1:
             helpers.msg(cli, channel, "[CNN] %s - %s" % (sorted_entries[i]['title'],tinyurl.create_one(sorted_entries[i]['link'])))
        elif sorted_entries[i]['link'].find("reuters") != -1:
             helpers.msg(cli, channel, "[REUTERS BUSINESS] %s - %s" % (sorted_entries[i]['title'],tinyurl.create_one(sorted_entries[i]['link'])))
        elif sorted_entries[i]['link'].find("slashdot") != -1:
             helpers.msg(cli, channel, "[\.] %s - %s" % (sorted_entries[i]['title'],tinyurl.create_one(sorted_entries[i]['link'])))
        elif sorted_entries[i]['link'].find("wired") != -1:
             helpers.msg(cli, channel, "[WIRED] %s - %s" % (sorted_entries[i]['title'],tinyurl.create_one(sorted_entries[i]['link'])))
        elif sorted_entries[i]['link'].find("popsci") != -1:
             helpers.msg(cli, channel, "[POPULAR SCIENCE] %s - %s" % (sorted_entries[i]['title'],tinyurl.create_one(sorted_entries[i]['link'])))
        elif sorted_entries[i]['link'].find("telegraph") != -1:
             helpers.msg(cli, channel, "[TELEGRAPH] %s - %s" % (sorted_entries[i]['title'],tinyurl.create_one(sorted_entries[i]['link'])))
        elif sorted_entries[i]['link'].find("google") != -1:
             helpers.msg(cli, channel, "[GOOGLE NEWS] %s - %s" % (sorted_entries[i]['title'],tinyurl.create_one(sorted_entries[i]['link'])))
        elif sorted_entries[i]['link'].find("hitb") != -1:
             helpers.msg(cli, channel, "[HACK IN THE BOX] %s - %s" % (sorted_entries[i]['title'],tinyurl.create_one(sorted_entries[i]['link'])))
        elif sorted_entries[i]['link'].find("dw-world") != -1:
             helpers.msg(cli, channel, "[DEUTSCHE WELLE ENG] %s - %s" % (sorted_entries[i]['title'],tinyurl.create_one(sorted_entries[i]['link'])))
        elif sorted_entries[i]['link'].find("pcgamer") != -1:
             helpers.msg(cli, channel, "[PC GAMER] %s - %s" % (sorted_entries[i]['title'],tinyurl.create_one(sorted_entries[i]['link'])))
        elif sorted_entries[i]['link'].find("eluniversal") != -1:
             helpers.msg(cli, channel, "[El Universal] %s - %s" % (sorted_entries[i]['title'],tinyurl.create_one(sorted_entries[i]['link'])))
        elif sorted_entries[i]['link'].find("nhk") != -1:
             helpers.msg(cli, channel, "[NHK] %s - %s" % (sorted_entries[i]['title'],tinyurl.create_one(sorted_entries[i]['link'])))
        elif sorted_entries[i]['link'].find("france24") != -1:
             helpers.msg(cli, channel, "[FRANCE24] %s - %s" % (sorted_entries[i]['title'],tinyurl.create_one(sorted_entries[i]['link'])))
        elif sorted_entries[i]['link'].find("chosun") != -1:
             helpers.msg(cli, channel, "[CHOSUN] %s - %s" % (sorted_entries[i]['title'],tinyurl.create_one(sorted_entries[i]['link'])))
        elif sorted_entries[i]['link'].find("theregister") != -1:
             helpers.msg(cli, channel, "[THEREGISTER] %s - %s" % (sorted_entries[i]['title'],tinyurl.create_one(sorted_entries[i]['link'])))
        elif sorted_entries[i]['link'].find("gameinformer") != -1:
             helpers.msg(cli, channel, "[GAME INFORMER] %s - %s" % (sorted_entries[i]['title'],tinyurl.create_one(sorted_entries[i]['link'])))  
        time.sleep(15)
    rsched.enter(5, 1, newsfeed, (cli,))   
#    for i in range(0,ajefeednum):
#        helpers.msg(cli, "#worldnews", "[AJE] %s" % ajefeed['entries'][i]['title'])
#        helpers.msg(cli, "#worldnews", "[AJE] %s" % ajefeed['entries'][i]['link'])
#        time.sleep(30)
#    for i in range(0,bbcfeednum):
#        helpers.msg(cli, "#worldnews", "[BBC WORLD NEWS] %s" % bbcfeed['entries'][i]['title'])
#        helpers.msg(cli, "#worldnews", "[BBC WORLD NEWS] %s" % bbcfeed['entries'][i]['link'])
#        time.sleep(30)

def connect_callback(cli):
    logging.basicConfig(level=logging.DEBUG)
    helpers.identify(cli, "19374862KL<>io")
    helpers.join(cli, channel)
    rsched.enter(5, 1, newsfeed, (cli,))
    rsched.run()

class k9leash(DefaultCommandHandler):
    def privmsg(self, nick, chan, msg):
        print "%s in %s said: %s" % (nick, chan, msg)

cli = IRCClient(k9leash, host=host, port=6667, nick=nickname, connect_cb=connect_callback)
connection = cli.connect()
while True:
    connection.next()
