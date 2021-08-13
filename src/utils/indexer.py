import csv
import nltk
import string
import re
from nltk import text
from nltk.corpus import stopwords
from nltk.downloader import update

hash = "test"
# nltk.download("stopwords)

def text_preprocess(tweet):
	turkish_stopwords = stopwords.words("turkish")
	text = tweet["content"]
	trans = str.maketrans("", "", string.punctuation)
	text = text.translate(trans)
	text = text.lower()
	processed_text = ""
	for word in text.split():
		if word not in turkish_stopwords:
			processed_text += word + " "
	tweet["processed"] = processed_text

def create_tokens(tweet):
	text_preprocess(tweet)
	index = {}
	words = tweet["processed"].split()
	for word in words:
		if word in index.keys():
			index[word]["freq"] += 1
		else:
			index[word] = {
				"docid": tweet["docid"],
				"doclen": len(words),
				"freq": 1
			}
	return index

def update_index(index, tweet):
	tokens = create_tokens(tweet)
	for token in tokens.keys():
		if token in index:
			index[token]["postinglist"].append(tokens[token])
			index[token]["total_freq"] += tokens[token]["freq"]
		else:
			index[token] = {}
			index[token]["postinglist"] = [tokens[token]]
			index[token]["total_freq"] = tokens[token]["freq"]

def write_index(path, index):
	with open(path, "w", newline='', encoding="utf-8") as f:
		writer = csv.writer(f)
		for key in sorted(index):
			postlist = index[key]["postinglist"]
			doc_num = len(postlist)
			total_freq = index[key]["total_freq"]
			entry = [key, doc_num, total_freq]
			for post in postlist:
				entry.append(post["docid"])
				entry.append(post["doclen"])
				entry.append(post["freq"])
			writer.writerow(entry)

def load_index(path):	
	index = {}
	with open(path, "r", newline='', encoding="utf-8") as f:
		reader = csv.reader(f)
		for line in reader:
			key = line[0]
			total_docs = line[1]
			total_freq = line[2]
			posting_list = []
			it = iter(line[3:])
			for val in it:
				posting_list.append({
					"docid": val,
					"doclen": next(it),
					"freq": next(it)
				})
			index[key] = {
				"postinglist": posting_list,
				"total_docs": total_docs,
				"total_freq": total_freq
			}
	return index

def main():
	docs = []
	f = open(f"{hash}.csv", "r", encoding="utf-8")
	reader = csv.DictReader(f, delimiter=",")
	for line in reader:
		docs.append(line)
	main_index = {}
	for doc in docs:
		update_index(main_index, doc)
	f.close()
	write_index("test_index.csv", main_index)

def load_test():
	index = load_index("test_index.csv")
	print(index)

if __name__ == "__main__":
	main()
	load_test()
