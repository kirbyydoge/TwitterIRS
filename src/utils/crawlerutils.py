import time
import traceback
import concurrent.futures
import re
from queue import Queue
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import Chrome
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By

def safe_find(driver, by, query):
	try:
		wait = WebDriverWait(driver, 5)
		elem = wait.until(EC.visibility_of_element_located(
			(by, query)
		))
		return elem
	except:
		traceback.print_exc()
		return None

def safe_find_multiple(driver, by, query):
	try:
		wait = WebDriverWait(driver, 5)
		elem = wait.until(EC.visibility_of_all_elements_located(
			(by, query)
		))
		return elem
	except:
		traceback.print_exc()
		return None

def scrape_single_card(card):
	data = {}
	data["username"] = card.find_element_by_xpath('./div[2]/div[1]//span').text
	data["twhandle"] = card.find_element_by_xpath('.//span[contains(text(), "@")]').text
	try:
		data["postdate"] = card.find_element_by_xpath('.//time').get_attribute('datetime')
	except:
		return None
	data["content"] = card.find_element_by_xpath('.//div[2]/div[2]/div[1]').text
	data["responding"] = card.find_element_by_xpath('.//div[2]/div[2]/div[2]').text
	data["reply"] = card.find_element_by_xpath('.//div[@data-testid="reply"]').text
	data["retweet"] = card.find_element_by_xpath('.//div[@data-testid="retweet"]').text
	data["like"] = card.find_element_by_xpath('.//div[@data-testid="like"]').text
	return data

def twitter_login(driver:Chrome, username, password):
	driver.get("https://twitter.com/login")
	userElem = safe_find(driver, By.XPATH, '//input[@name="session[username_or_email]"]')
	if userElem:
		userElem.send_keys(username)
	else:
		return twitter_login_flow(driver, username, password)
	passElem = safe_find(driver, By.XPATH, '//input[@name="session[password]"]')
	if passElem:
		passElem.send_keys(password)
		passElem.send_keys(Keys.RETURN)
	else:
		return twitter_login_flow(driver, username, password)
	return True

def twitter_login_flow(driver:Chrome, username, password):
	userElem = safe_find(driver, By.XPATH, '//input[@name="username"]')
	if userElem:
		userElem.send_keys(username)
		userElem.send_keys(Keys.RETURN)
	else:
		return False
	passElem = safe_find(driver, By.XPATH, '//input[@name="password"]')
	if passElem:
		passElem.send_keys(password)
		passElem.send_keys(Keys.RETURN)
	else:
		return False
	return True

def twitter_search(driver:Chrome, query, tab=None):
	driver.get("https://twitter.com/home")
	searchBox = safe_find(driver, By.XPATH, '//input[@aria-label="Search query"]')
	if searchBox:
		searchBox.send_keys(query)
		searchBox.send_keys(Keys.RETURN)
		if tab:
			safe_find(driver, By.LINK_TEXT, tab).click()
	else:
		return False
	return True

def crawl_hashtag(driver:Chrome, task_fifo:Queue, feedback_fifo:Queue, hashtag, number_of_max_tweets, tab="Latest"):
	print(f"BROWSER: Starting.")

	executor = concurrent.futures.ThreadPoolExecutor()

	while not twitter_search(driver, hashtag, tab=tab):
		pass

	last_pos = driver.execute_script("return window.pageYOffset;")
	counter = 0
	isRunning = True

	while isRunning and counter < number_of_max_tweets:
		cards = safe_find_multiple(driver, By.XPATH, '//div[@data-testid="tweet"]')
		tweets = executor.map(scrape_single_card, cards[-10:])
		for tweet in tweets:
			if tweet:
				print("BROWSER: Pushing tweet.")
				task_fifo.put(tweet)
		tolerance = 0
		while tolerance < 5:
			driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
			time.sleep(1)
			cur_pos = driver.execute_script("return window.pageYOffset;")
			if last_pos == cur_pos:
				tolerance += 1
			else:
				break
		if tolerance < 5:
			last_pos = cur_pos
		else:
			isRunning = False

		while not feedback_fifo.empty():
			if feedback_fifo.get():
				counter += 1

	executor.shutdown(wait=False)

	task_fifo.put(None)

"""
	DOES NOT WORK
	As selenium requires object to stay to scrape a card.
"""
def process_card(task_fifo:Queue, product_fifo:Queue, thread_id):
	print(f"THREAD{thread_id}: Starting.")
	consume = True
	while consume:
		card = task_fifo.get()
		if card:
			print(f"THREAD{thread_id}: Processing Card.")
			tweet = scrape_single_card(card)
			if tweet:
				print(f"THREAD{thread_id}: Scraped {card['twhandle']}.")
				product_fifo.put(tweet)
			else:
				print(f"THREAD{thread_id}: Bad tweet.")
		else:
			print(f"THREAD{thread_id}: Exitting.")
			consume = False
	product_fifo.put(None)

def combine_cards(task_fifo:Queue, feedback_queue:Queue, product_fifo:Queue):
	print("COMBINER: Starting.")
	combine = True
	tweet_ids = set()
	while combine:
		tweet = task_fifo.get()
		if tweet:
			tweet_id = ''.join(str(tweet[x]) for x in sorted(tweet))
			if tweet_id not in tweet_ids:
				product_fifo.put(tweet)
				print(f"COMBINER: Appending {tweet['twhandle']}")
				feedback_queue.put(True)
				tweet_ids.add(tweet_id)
		else:
			combine = False
			print(f"COMBINER: A thread has shut down.")
	product_fifo.put(None)