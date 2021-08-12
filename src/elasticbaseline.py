import requests
import json
from elasticsearch import Elasticsearch
from utils import fileutils


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
	for tweet in tweets:
		response = requests.post(url, data=json.dumps(tweet), headers=BASE_HEADER)
	print(f"IDX RESP: {response}")

def search(query, headers):
	url = f"{BASE_URL}/{BASE_FOLDER}/_doc/_search"
	response = requests.get(url, data=json.dumps(query), headers=headers)
	hits = json.loads(response.text)["hits"]["hits"]

	print("Num\tRelevance Score\tTitle")
	for idx, hit in enumerate(hits):
		print(f"{idx+1}\t{hit['_score']}\t{hit['_source']['content']}")

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
	init()
	index()

def cleanup():
	response = requests.delete(f"{BASE_URL}/{BASE_FOLDER}")
	print(f"DEL RESP: {response}")

def text_to_search(text):
	query = get_match_query(text)
	search(query, BASE_HEADER)

"""
Please run setup once before running the queries.

You may also cleanup your folder afterwards to save unnecessary space.
-> I recommend you cleanup once you are done with this index forever, as rebuilding the index has a cost.
"""
if __name__ == "__main__":
	#setup()
	text_to_search("uzayda araba")
	#cleanup()