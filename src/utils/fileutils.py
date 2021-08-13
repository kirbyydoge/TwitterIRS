import csv
import os
import datetime

def create_filedump(path_list):
	tweets = []
	for path in path_list:
		f = open(path, "r", encoding="utf-8")
		reader = csv.DictReader(f, delimiter=",")
		for line in reader:
			tweets.append(line)
		f.close()
	return tweets

def save_filedump(path, tweets):
	with open(path, "w", encoding="utf-8") as f:
		keys = tweets[0].keys()
		writer = csv.DictWriter(f, keys)
		writer.writeheader()
		writer.writerows(tweets)
		f.close()

def load_filedump(path):
	tweets = []
	with open(path, "r", encoding="utf-8") as f:
		reader = csv.DictReader(f, delimiter=",")
		for line in reader:
			tweets.append(line)
	return tweets

def list_files(path):
	return [os.path.join(path, f) for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]

def hashtag_path_list():
	return list_files("hashtags/latest") + list_files("hashtags/top")

def read_crawled_files():
	return create_filedump(hashtag_path_list())

def judgment_hash(tweet):
	hash =  ''.join(str(tweet[x]) for x in sorted(tweet))
	return hash

def load_judgments(topic):
	judgments = []
	with open(f"judgments/{topic}.csv", "r", encoding="utf-8") as f:
		reader = csv.DictReader(f, delimiter=",")
		for line in reader:
			judgments.append(line)
	return judgments

def save_judgments(topic, relevant_ids, db):
	topic_info = []
	judg_hashes = set()
	for id in relevant_ids:
		tweet = db.get(id)
		topic_info.append(tweet)
	if os.path.isfile(f"judgments/{topic}.csv"):
		judgments = load_judgments(topic)
		for judgment in judgments:
			judg_hash = judgment_hash(judgment)
			judg_hashes.add(judg_hash)
		write_header = False
	else:
		write_header = True
	clean_topics = []
	for tweet in topic_info:
		tweet_hash = judgment_hash(tweet)
		if tweet_hash not in judg_hashes:
			judg_hashes.add(tweet_hash)
			clean_topics.append(tweet)
	with open(f"judgments/{topic}.csv", "a", encoding="utf-8") as f:
		keys = topic_info[0].keys()
		writer = csv.DictWriter(f, keys)
		if write_header:
			writer.writeheader()
		writer.writerows(clean_topics)
		f.close()

if __name__ == "__main__":
	paths = list_files("hashtags/latest") + list_files("hashtags/top")
	tweets = create_filedump(paths)
	save_filedump("filedumps/initaldb.filedump", tweets)
	test = load_filedump("filedumps/initaldb.filedump")
	print(test == tweets)