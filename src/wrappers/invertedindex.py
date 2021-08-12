"""
	Wrapper Class to hide implementation details of inverted index
"""

from utils import indexer

class InvertedIndex():
	
	def __init__(self, path):
		self.path = path
		self.index = {}

	def add(self, document):
		indexer.update_index(self.index, document)

	def get(self, key):
		return self.index[key]

	def size(self):
		return len(self.index.keys())

	def save(self):
		indexer.write_index(self.path, self.index)

	def load(self, path):
		self.path = path
		self.index = indexer.load_index(path)

	def get_dict(self):
		return self.index	# DO NOT MODIFY THE INDEX MANUALLY WITH THE RETURNED DICT, USE self.add(document) INSTEAD