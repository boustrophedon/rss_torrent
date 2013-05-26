#!/usr/bin/python

import feedparser
import time,calendar
import csv
import os
import subprocess


HOME = os.path.expanduser("~")
### Config
# will probably error if these folders/files do not exist.
TORRENT_DIR = HOME+"/.cache/rss_torrent/torrentfiles/"
FEED_FILE = HOME+"/.local/rss_torrent/feeds.csv" 
NEW_FEEDS = HOME+"/.local/rss_torrent/new.txt" 
SEED_RATIO = "50"




def add_torrent(e):
	#should check if entry.link is a valid url
	torrent_file = TORRENT_DIR+e.title+".torrent"
	p = subprocess.Popen( ["curl", "-s", e.link, "-o", torrent_file] )
	p.wait()
	#should check if this actually is a torrent file
	subprocess.Popen( ['transmission-remote', '-a', torrent_file, '-sr', SEED_RATIO] )


def check_feed(feed_url, last_checked):

	feed = feedparser.parse(feed_url)

	for e in feed.entries:
		entry_time = calendar.timegm(e.published_parsed)
		if last_checked < entry_time:
			add_torrent(e)
			oldest = e
		else:
			break # this should work because the entries are supposed to be in chronological order.

	last_checked = calendar.timegm(feed.entries[0].published_parsed)
	return last_checked

def check_new_feeds(rss_file):
	lines = []
	with open(rss_file) as f:
		for line in f:
			lines.append([line.strip(), 0])
	with open(rss_file,'w') as f:
		f.write('')
	# there is probably a better way to do this

	return lines

def parse_rss_csv(csv_file):
	with open(csv_file, newline='') as f:
		reader = csv.reader(f)
		rows = []
		for row in reader:
			rows.append([row[0], int(row[1])])
		return rows

def write_rss_csv(feeds,csv_file):
	with open(csv_file, 'w', newline='') as f:
		writer = csv.writer(f)
		writer.writerows(feeds)

def main():
	feeds = parse_rss_csv(FEED_FILE)

	new_feeds = check_new_feeds(NEW_FEEDS)
	if new_feeds: feeds = feeds + new_feeds;

	updated_feeds = []

	for feed,timestamp in feeds:
		timestamp = check_feed(feed,timestamp)
		updated_feeds.append([feed,timestamp])

	if len(feeds) != len(updated_feeds):
		print("this is a problem.")

	write_rss_csv(updated_feeds,FEED_FILE)



if __name__ == '__main__':
	main()
