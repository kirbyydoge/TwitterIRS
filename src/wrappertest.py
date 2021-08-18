from wrappers.database import Database
from wrappers.invertedindex import InvertedIndex
from utils import fileutils, scoreutils
from utils.fileutils import print_tweet

import time

version = 1
DATABASE_PATH = f"filedumps/db_v{version}.filedump"
INDEX_PATH = f"indexes/index_v{version}.index"

def test_create():
	db = Database(DATABASE_PATH)
	index = InvertedIndex(INDEX_PATH)

	files = fileutils.read_crawled_files()

	for file in files:
		db.add(file)

	print(db.dupes)

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

	print(db.size())

def test_unigram():
	db = Database(DATABASE_PATH)
	index = InvertedIndex(INDEX_PATH)

	db.load(DATABASE_PATH)
	index.load(INDEX_PATH)

	results = scoreutils.score_unigram("ucan araba", index, lamb=0.8)

	for docid in results:
		tweet = db.get(docid)
		print_tweet(tweet)

if __name__ == "__main__":
	"""
	start = time.time()
	test_create()
	end = time.time()
	print(f"Index Creation and Writing took {end - start} seconds.")
	"""
	start = time.time()
	test_unigram()
	end = time.time()
	print(f"Index Load and Query took {end - start} seconds.")
