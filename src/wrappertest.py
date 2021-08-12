from wrappers.database import Database
from wrappers.invertedindex import InvertedIndex
from utils import fileutils, scoreutils

import time

DATABASE_PATH = "filedumps/initialdb.filedump"
INDEX_PATH = "indexes/initialidx.index"

def print_tweet(tweet):
	print("*************")
	print(f"{tweet['twhandle']} demis ki:\n")
	print(tweet["content"])
	print("\n*************")


def test_create():
	db = Database(DATABASE_PATH)
	index = InvertedIndex(INDEX_PATH)

	files = fileutils.read_crawled_files()

	for file in files:
		db.add(file)

	db.save()

	for i in range(db.size()):
		document = db.get(i)
		index.add(document)

	db.load(db.path)
	index.save()

def test_load():
	db = Database(DATABASE_PATH)
	index = InvertedIndex(INDEX_PATH)

	db.load(DATABASE_PATH)
	index.load(INDEX_PATH)

	result = index.get("marvel")

	print("Icerisinde 'marvel' gecen tweetler:")

	for doc in result["postinglist"]:
		tweet = db.get(doc["docid"])
		print(tweet)
		print(doc)
		print_tweet(tweet)
	print(db.size())

def test_unigram():
	db = Database(DATABASE_PATH)
	index = InvertedIndex(INDEX_PATH)

	db.load(DATABASE_PATH)
	index.load(INDEX_PATH)

	results = scoreutils.score_unigram("uzaya araba göndermek", index, lamb=0.8)

	for docid in results:
		tweet = db.get(docid)
		print_tweet(tweet)

if __name__ == "__main__":
	start = time.time()
	test_create()
	end = time.time()
	print(f"Index Creation and Writing took {end - start} ms.")
	start = time.time()
	test_load()
	end = time.time()
	print(f"Index Load and Query took {end - start} ms.")
	"""
	test_unigram()
	"""
