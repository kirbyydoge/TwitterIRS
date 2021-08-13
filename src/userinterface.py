from logging import debug
from flask import Flask, render_template, request, json, jsonify
from utils import scoreutils
import elasticbaseline

app = Flask(__name__)
app.config["SECRET_KEY"] = "9fc5e33cf23b805a512fa86d3ez75b7c"

@app.route("/")
@app.route("/home")
def home():
	return render_template("home.html", title="BIL472 PROJE YARDIMCI ARAYUZ")

@app.route("/search")
def search():
	return render_template("search.html")
	
@app.route("/search/query", methods=["GET", "POST"])
def search_query():
	data = request.get_json()
	try:
		query = data["query"]
		method = data["method"]
		if method == "UNIGRAM":
			result = scoreutils.score_unigram(query)
		elif method == "ELASTICBM25":
			result = elasticbaseline.text_to_search(query)
		if result:
			result = result[:10]
		else:
			return jsonify({"success":False})
	except Exception as e:
		print(e)
		return jsonify({"success":False})
	return jsonify({"success":True, "tweets": jsonify(result)})

if __name__ == "__main__":
	app.run(debug=True)