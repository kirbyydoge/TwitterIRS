import csv
import os
import re
import selenium.webdriver as webdriver
import concurrent.futures
from queue import Queue
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import Chrome
import utils.crawlerutils as cru

username = os.environ["TW_USERNAME"]
password = os.environ["TW_PASSWORD"]

driver = Chrome(executable_path='D:/BrowserDrivers/chrome91.exe')

tweets_per_hash = 1000

initial_hashtags = [
	"#teknoloji",
	"#ekonomi",
	"#haber",
	"#oyun",
	"#magazin"
]

hashtags = set(initial_hashtags)
crawl_branching = False
crawl_queue = Queue()

with concurrent.futures.ThreadPoolExecutor() as executor:

	while not cru.twitter_login(driver, username, password):
		pass

	for hash in hashtags:
		crawl_queue.put(hash)

	while not crawl_queue.empty():
		hash = crawl_queue.get()
		print(f"Starting crawling {hash}")
		# Consumer Producer Setup
		scrape_queue = Queue()
		feedback_queue = Queue()
		tweet_queue = Queue()
		browser = executor.submit(cru.crawl_hashtag, driver, scrape_queue, feedback_queue, hash, tweets_per_hash, tab=None)
		combiner = executor.submit(cru.combine_cards, scrape_queue, feedback_queue, tweet_queue)

		# Result Saving Setup
		f = open(f"crawlmemory/{hash}.csv", "w", newline="", encoding="utf-8")
		keys = None
		writer = None

		# Result Saving
		while True:
			tweet = tweet_queue.get()
			if not tweet:
				break
			if not keys:
				keys = tweet.keys()
				writer = csv.DictWriter(f, keys)
				writer.writeheader()
			for cur_hash in tweet["hashtags"]:
				cur_hash = f"#{cur_hash.lower()}"
				if cur_hash not in hashtags:
					if crawl_branching:
						crawl_queue.put(cur_hash)
					hashtags.add(cur_hash)
			writer.writerow(tweet)

		# Cleanup
		print("Cleaning Up.")
		f.flush()
		f.close()
		browser.result()
		combiner.result()