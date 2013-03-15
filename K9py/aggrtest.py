#!/usr/bin/env python
# used for testing rss feeds to see if feedparser can read them

from concurrent import futures
import feedparser
import sched, time

rss_urls = ['http://feeds.feedburner.com/ImgurGallery?format=xml']
entries = []
s = sched.scheduler(time.time, time.sleep)

def getentries():
    with futures.ThreadPoolExecutor(max_workers=2) as executor:
         future_to_url = dict((executor.submit(feedparser.parse, url), url) for url in rss_urls)
         
         feeds = [future.result() for future in futures.as_completed(future_to_url)]
         #print [future.result() for future in futures.as_completed(future_to_url)]
         for feed in feeds:
            for item in feed:
                print "\n"
                print item
                print feed[item]
                print "\n"
            entries.extend(feed["feed"])
            print entries.extend(feed["feed"])
            entries.extend(feed["items"])
            sorted_entries = sorted(entries, key=lambda entry: entry["date_parsed"], reverse=True)
            sorted_entries = sorted_entries.reverse()
    s.enter(5, 1, getentries, ())
    print entries
    #entsize = len(sorted_entries)
    #for i in range(0, entsize):
    #    if sorted_entries[i]['link'].find("bbc") != -1:
    #       print "bbc"
    #   elif sorted_entries[i]['link'].find("jazeera") != -1:
    #       print "aje"
    #print sorted_entries[0]['link'].find("bbc")

#def displayentries():
    #print getentries()
    #entsize = len(sentries)
    #for i in range(0, entsize):
    #    if sentries[i]['link'].find("bbc") != -1:
    #       print "bbc"
    #    elif sentries[i]['link'].find("jazeera") != -1:
    #       print "aje"
    #print sentries[0]['link'].find("bbc")

s.enter(5, 1, getentries, ())
s.run()
#displayentries()
