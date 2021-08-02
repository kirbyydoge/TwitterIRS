from wrappers.database import Database
from wrappers.invertedindex import InvertedIndex
from utils import fileutils


DATABASE_PATH = "filedumps/initialdb.filedump"
INDEX_PATH = "indexes/initialidx.index"

def read_crawled_files():
	return fileutils.create_filedump(fileutils.hashtag_path_list())

def test_create():
	db = Database(DATABASE_PATH)
	index = InvertedIndex(INDEX_PATH)

	files = read_crawled_files()

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
		print (tweet)
		print("*************")
		print(f"{tweet['twhandle']} demis ki:\n")
		print(tweet["content"])
		print("\n*************")

	print(db.size())

test_load()
