import math
from wrappers.database import Database
from wrappers.invertedindex import InvertedIndex
from utils.indexer import create_tokens
from utils import scoreutils
from utils.fileutils import print_tweet

VERSION = 1
DATABASE_PATH = f"filedumps/db_v{VERSION}.filedump"
INDEX_PATH = f"indexes/index_v{VERSION}.index"

if __name__ == "__main__":

    db = Database(DATABASE_PATH)
    index = InvertedIndex(INDEX_PATH)

    db.load(DATABASE_PATH)
    index.load(INDEX_PATH)

    for score in scoreutils.score_query("ucan araba", index, db):
        tweet = db.get(score["docid"])
        print_tweet(tweet)