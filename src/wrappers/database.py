"""
	Wrapper Class to hide implementation details of document storage
"""

import utils.fileutils as fu

class Database():
	def __init__(self, path):
		self.path = path
		self.hash = set()
		self.dump = []

	def add(self, tweet):
		tweet["docid"] = self.size()
		cur_hash = fu.hash_tweet(tweet)
		if cur_hash not in self.hash:
			self.dump.append(tweet)
			self.hash.add(cur_hash)

	def get(self, id):
		return self.dump[int(id)]

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