import requests
import json
from elasticsearch import Elasticsearch
from utils import fileutils

import time

"""
Thanks to Mr./Mrs. Ethen8181 for the valuable guide on how to start with Elasticsearch
-> http://ethen8181.github.io/machine-learning/search/bm25_intro.html

Further used: (also provided in the references of the link above)
-> https://www.elastic.co/blog/practical-bm25-part-1-how-shards-affect-relevance-scoring-in-elasticsearch
-> https://www.elastic.co/blog/practical-bm25-part-2-the-bm25-algorithm-and-its-variables
-> https://www.elastic.co/blog/practical-bm25-part-3-considerations-for-picking-b-and-k1-in-elasticsearch

"""
BASE_URL = "http://localhost:9200"
BASE_FOLDER = "bil472"
BASE_HEADER = {"Content-Type": "application/json"}

def init():
	settings = {
		"settings": {
			"index": {
				"number_of_shards": 1,
				"number_of_replicas": 1,
				"similarity": {
					"default": {
						"type": "BM25"
					}
				}
			}
		},
		"mappings": {
			"properties": {
				"title": {
					"type": "text",
					"analyzer": "turkish"
				}
			}
		}
	}
	response = requests.put(f"{BASE_URL}/{BASE_FOLDER}", data=json.dumps(settings), headers=BASE_HEADER)
	print(f"INIT RESP: {response.text}")

def index():
	url = f"{BASE_URL}/{BASE_FOLDER}/_doc"
	tweets = fileutils.read_crawled_files()
	tweet_hashes = set()
	for tweet in tweets:
		tw_hash = tweet["content"]
		if tw_hash not in tweet_hashes:
			tweet_hashes.add(tw_hash)
			response = requests.post(url, data=json.dumps(tweet), headers=BASE_HEADER)
	print(f"IDX RESP: {response}")

def search(query, headers, verbose=False):
	url = f"{BASE_URL}/{BASE_FOLDER}/_doc/_search"
	response = requests.get(url, data=json.dumps(query), headers=headers)
	hits = json.loads(response.text)["hits"]["hits"]
	if verbose:
		print("Num\tRelevance Score\tTitle")
		for idx, hit in enumerate(hits):
			print(f"{idx+1}\t{hit['_score']}\t{hit['_source']['content']}")
	return hits

def get_match_query(query):
	query = {
		"query": {
			"match": {
				"content": query
			}
		}
	}
	return query

def setup():
	cleanup()
	#start = time.time()
	init()
	index()
	#end = time.time()
	#print(end-start)

def cleanup():
	response = requests.delete(f"{BASE_URL}/{BASE_FOLDER}")
	print(f"DEL RESP: {response}")

def text_to_search(text, verbose=False):
	query = get_match_query(text)
	return search(query, BASE_HEADER, verbose=verbose)

"""
Please run setup once before running the queries.

You may also cleanup your folder afterwards to save unnecessary space.
-> I recommend you cleanup once you are done with this index forever, as rebuilding the index has a cost.
"""
if __name__ == "__main__":
	setup()
	#text_to_search("uzayda araba", verbose=True)
	#cleanup()