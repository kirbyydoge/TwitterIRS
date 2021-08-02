"""
	Wrapper Class to hide implementation details of document storage
"""

import utils.fileutils as fu

class Database():
	def __init__(self, path):
		self.path = path
		self.dump = []

	def add(self, tweet):
		self.dump.append(tweet)

	def get(self, id):
		return self.dump[int(id)]

	def size(self):
		return len(self.dump)

	def save(self):
		fu.save_filedump(self.path, self.dump)

	def load(self, path):
		self.path = path
		self.dump = fu.load_filedump(path)