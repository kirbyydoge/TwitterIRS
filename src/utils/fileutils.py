import csv
import os

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

if __name__ == "__main__":
	paths = list_files("hashtags/latest") + list_files("hashtags/top")
	tweets = create_filedump(paths)
	save_filedump("filedumps/initaldb.filedump", tweets)
	test = load_filedump("filedumps/initaldb.filedump")
	print(test == tweets)