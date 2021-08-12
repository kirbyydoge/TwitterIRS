import re
import datetime
from utils import fileutils

def extract_hashtags(tweet):
	hashtags = re.findall(r"#(\w+)", tweet["content"].lower())
	return hashtags

def bulk_analysis(tweets):
	user_data = {}
	hashtag_data = {}
	for tweet in tweets:
		handle = tweet["twhandle"]
		if handle in user_data:
			user_data[handle] += 1
		else:
			user_data[handle] = 1
		hashtags = extract_hashtags(tweet)
		for hashtag in hashtags:
			if hashtag in hashtag_data:
				hashtag_data[hashtag] += 1
			else:
				hashtag_data[hashtag] = 1
	sorted_users = sorted(user_data, key=lambda x: user_data[x], reverse=True)
	sorted_hashtags = sorted(hashtag_data, key=lambda x: hashtag_data[x], reverse=True)
	print("Top 10 Users With Most Tweets:")
	for user in sorted_users[:10]:
		print(f"{user}: {user_data[user]}")
	print("Top 10 Hashtags With Most Tweets:")
	for hashtag in sorted_hashtags[:10]:
		print(f"{hashtag}: {hashtag_data[hashtag]}")
	print(f"Total Users: {len(user_data)}")
	print(f"Total Hashtags: {len(hashtag_data)}")
	print(f"Total Tweets: {len(tweets)}")
	cur_time = datetime.datetime.now()
	cur_time = f"{cur_time.year}_{cur_time.month}_{cur_time.day}_{cur_time.hour}"
	with open(f"dataanalysis/{cur_time}.txt", "w", encoding="utf-8") as f:
		f.write("Top 10 Users With Most Tweets:\n")
		for user in sorted_users[:10]:
			f.write(f"\t{user}: {user_data[user]}\n")
		f.write("Top 10 Hashtags With Most Tweets:\n")
		for hashtag in sorted_hashtags[:10]:
			f.write(f"\t#{hashtag}: {hashtag_data[hashtag]}\n")
		f.write(f"Total Users: {len(user_data)}\n")
		f.write(f"Total Hashtags: {len(hashtag_data)}\n")
		f.write(f"Total Tweets: {len(tweets)}\n")
		f.flush()
		f.close()

def main():
	files = fileutils.read_crawled_files()
	print(len(files))
	bulk_analysis(files)

if __name__ == "__main__":
	main()