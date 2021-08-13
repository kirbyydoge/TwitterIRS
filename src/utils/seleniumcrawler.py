import csv
import os
import re
import selenium.webdriver as webdriver
import concurrent.futures
import datetime
from queue import Queue
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import Chrome
import crawlerutils as cru

username = os.environ["TW_USERNAME"]
password = os.environ["TW_PASSWORD"]

opts = Options()
opts.headless = True
opts.add_argument("window-size=1200,1100")

driver = Chrome(options=opts, executable_path='D:/BrowserDrivers/chrome91.exe')

tweets_per_hash = 2000
branch_decay = 0.6
branch_thresh = 100

initial_hashtags = [
	"#uzay",
	"#sağlık",
	"#sondakika",
	"#haber",
	"#magazin",
	"#teknoloji",
	"#oyun"
]

tab = None

hashtags = set(initial_hashtags)
crawl_branching = True
crawl_queue = Queue()
max_queue = Queue()
cur_time = datetime.datetime.now()
cur_time = f"{cur_time.year}_{cur_time.month}_{cur_time.day}_{cur_time.hour}_{cur_time.minute}"
print(cur_time)

with concurrent.futures.ThreadPoolExecutor() as executor:

	while not cru.twitter_login(driver, username, password):
		pass

	for hash in hashtags:
		crawl_queue.put(hash)
		max_queue.put(tweets_per_hash)

	while not crawl_queue.empty():
		hash = crawl_queue.get()
		max_count = max_queue.get()
		print(f"Starting crawling {hash}. Max tweets {max_count}")
		# Consumer Producer Setup
		scrape_queue = Queue()
		feedback_queue = Queue()
		tweet_queue = Queue()
		browser = executor.submit(cru.crawl_hashtag, driver, scrape_queue, feedback_queue, hash, max_count, tab=tab)
		combiner = executor.submit(cru.combine_cards, scrape_queue, feedback_queue, tweet_queue)

		# Result Saving Setup
		f = open(f"crawlmemory/{hash}_{cur_time}.csv", "w", newline="", encoding="utf-8")
		keys = None
		writer = None

		# Result Saving
		while True:
			tweet = tweet_queue.get()
			if not tweet:
				break
			tweet["hashtags"] = re.findall(r"#(\w+)", tweet["content"])
			if not keys:
				keys = tweet.keys()
				writer = csv.DictWriter(f, keys)
				writer.writeheader()
			cur_max_tweets = max_count*branch_decay
			if cur_max_tweets > branch_thresh:
				for cur_hash in tweet["hashtags"]:
					cur_hash = f"#{cur_hash.lower()}"
					if cur_hash not in hashtags:
						if crawl_branching:
							crawl_queue.put(cur_hash)
							max_queue.put(cur_max_tweets)
						hashtags.add(cur_hash)
				writer.writerow(tweet)

		# Cleanup
		print("Cleaning Up.")
		f.flush()
		f.close()
		browser.result()
		combiner.result()
