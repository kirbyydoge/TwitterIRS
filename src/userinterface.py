from logging import debug
from flask import Flask, render_template, request, json, jsonify, redirect, url_for
from utils import scoreutils, fileutils
from wrappers.database import Database
from wrappers.invertedindex import InvertedIndex
import elasticbaseline
import json

app = Flask(__name__)
app.config["SECRET_KEY"] = "9fc5e33cf23b805a512fa86d3ez75b7c"

DATABASE_PATH = "filedumps/initialdb.filedump"
INDEX_PATH = "indexes/initialidx.index"

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
		fileutils.save_judgments(topic, relevant_ids, db)
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
		if method == "unigram":
			result = scoreutils.score_unigram(query, index, lamb=0.8)
			tweetlist = []
			for tweetid in result:
				tweet = db.get(tweetid)
				tweet["id"] = tweetid
				tweetlist.append(json.dumps(db.get(tweetid)))
		elif method == "elasticbm25":
			result = elasticbaseline.text_to_search(query)
			tweetlist = []
			for entry in result:
				tweetlist.append(json.dumps(entry["_source"]))
		if tweetlist:
			tweetlist = tweetlist[:10]
		else:
			return jsonify({"success":False})
	except Exception as e:
		print(e)
		return jsonify({"success":False})
	return jsonify({"success":True, "tweets":tweetlist})

if __name__ == "__main__":
	app.run(debug=True)