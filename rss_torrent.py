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
	print(torrent_file)

	p = subprocess.Popen( ["curl", "-s", e.link, "-o", torrent_file] )
	p.wait()
	#should check if this actually is a torrent file
	subprocess.Popen( ['transmission-remote', '-a', torrent_file, '-sr', SEED_RATIO] )

def check_substrings(title, match_strings):
	for s in match_strings:
		if s not in title.lower():
			return False
	return True;

def check_feed(feed_url, last_checked, match_strings):

	feed = feedparser.parse(feed_url)

	for e in feed.entries:
		entry_time = calendar.timegm(e.updated_parsed)
		if last_checked < entry_time:
			if check_substrings(e.title, match_strings):
				add_torrent(e)
				oldest = e
		else:
			break # this should work because the entries are supposed to be in chronological order.

	try:
		last_checked = calendar.timegm(feed.entries[0].updated_parsed)
	except IndexError:
		#print("IndexError: "+feed_url+". Apparently there is no feed.entries[0]")

		with open(HOME+"err.last", "w") as errfile:
			errfile.write(str(feed))

	return last_checked

def check_new_feeds(rss_file):
	lines = []
	with open(rss_file) as f:
		for line in f:
			cols = line.split(',');
			if len(cols) == 2:
				lines.append([cols[0].strip(), 0, cols[1].split()])
			else:
				lines.append([cols[0].strip(), 0, ""])
	with open(rss_file,'w') as f:
		f.write('')
	# there is probably a better way to do this

	return lines

def parse_rss_csv(csv_file):
	with open(csv_file, 'rb') as f:
		reader = csv.reader(f)
		rows = []
		for row in reader:
			rows.append([row[0], int(row[1]), row[2].split(' ')])
		return rows

def write_rss_csv(feeds,csv_file):
	with open(csv_file, 'wb') as f:
		writer = csv.writer(f)
		writer.writerows(feeds)

def main():
	feeds = parse_rss_csv(FEED_FILE)

	new_feeds = check_new_feeds(NEW_FEEDS)
	if new_feeds: feeds = feeds + new_feeds;

	updated_feeds = []

	for feed,timestamp,match_strings in feeds:
		timestamp = check_feed(feed,timestamp, match_strings)
		updated_feeds.append([feed,timestamp, ' '.join(match_strings)])

	if len(feeds) != len(updated_feeds):
		print("this is a problem.")

	write_rss_csv(updated_feeds,FEED_FILE)



if __name__ == '__main__':
	main()
