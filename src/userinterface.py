from logging import debug
from flask import Flask, render_template, request, json, jsonify, redirect, url_for
from utils import scoreutils, fileutils
from wrappers.database import Database
from wrappers.invertedindex import InvertedIndex
import elasticbaseline
import json
import time

app = Flask(__name__)
app.config["SECRET_KEY"] = "9fc5e33cf23b805a512fa86d3ez75b7c"

VERSION = 1
DATABASE_PATH = f"filedumps/db_v{VERSION}.filedump"
INDEX_PATH = f"indexes/index_v{VERSION}.index"

db = Database(DATABASE_PATH)
index = InvertedIndex(INDEX_PATH)

db.load(DATABASE_PATH)
index.load(INDEX_PATH)

@app.route("/")
@app.route("/home")
def home():
	return render_template("home.html", title="BIL472 PROJE YARDIMCI ARAYUZ")

@app.route("/search")
def search():
	return render_template("search.html")

@app.route("/search/judge", methods=["GET", "POST"])
def search_judge():
	data = request.get_json()
	try:
		topic = data["topic"]
		query = data["query"]
		model = data["model"]
		relevant_ids = data["relevant_ids"]
		if len(relevant_ids) > 0 and model != "elasticbm25":
			fileutils.save_judgments(topic, relevant_ids, db)
		fileutils.save_presicion(query, model, len(relevant_ids))
	except Exception as e:
		print(e)
		return jsonify({"success":False})
	return jsonify({"success":True})

@app.route("/search/query", methods=["GET", "POST"])
def search_query():
	data = request.get_json()
	print(data)
	try:
		query = data["query"]
		method = data["method"]
		tweetlist = []
		start = time.time()
		if method == "unigram":
			result = scoreutils.score_unigram(query, index, lamb=0.8)
			for tweetid in result:
				tweet = db.get(tweetid)
				tweet["id"] = tweetid
				tweetlist.append(json.dumps(db.get(tweetid)))
		elif method == "elasticbm25":
			result = elasticbaseline.text_to_search(query)
			for entry in result:
				tweetlist.append(json.dumps(entry["_source"]))
		elif method == "tfidf":
			result = scoreutils.score_tfidf(query, index, db, use_likert=False)
			for score in result:
				tweetlist.append(json.dumps(db.get(score["docid"])))
		elif method == "tfidf_likert":
			result = scoreutils.score_tfidf(query, index, db, use_likert=True)
			for score in result:
				tweetlist.append(json.dumps(db.get(score["docid"])))
		end = time.time()
		fileutils.save_speed(query, method, (end-start))
		if len(tweetlist) > 0:
			tweetlist = tweetlist[:10]
		else:
			return jsonify({"success":False})
	except Exception as e:
		print(e)
		return jsonify({"success":False})
	return jsonify({"success":True, "tweets":tweetlist})

if __name__ == "__main__":
	app.run(debug=True)