"""
	Wrapper Class to hide implementation details of document storage
"""

import utils.fileutils as fu

class Database():
	def __init__(self, path):
		self.path = path
		self.hash = set()
		self.dupes = 0
		self.dump = []

	def add(self, tweet):
		tweet["docid"] = self.size()
		cur_hash = tweet["content"]
		if cur_hash not in self.hash:
			self.dump.append(tweet)
			self.hash.add(cur_hash)
		else:
			self.dupes += 1

	def get(self, id):
		return self.dump[int(id)]

	def safe_get(self, id):
		document = self.dump[int(id)]
		if document["retweet"] == "":
			document["retweet"] = 0
		if document["like"] == "":
			document["like"] = 0
		if document["reply"] == "":
			document["reply"] = 0
		return document

	def size(self):
		return len(self.dump)

	def save(self):
		fu.save_filedump(self.path, self.dump)

	def repair_hash(self):
		self.hash = set()
		for i in range(self.size()):
			tweet = self.get(i)
			cur_hash = fu.hash_tweet(tweet)
			self.hash.add(cur_hash)

	def load(self, path):
		self.path = path
		self.dump = fu.load_filedump(path)