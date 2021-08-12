import math
from wrappers.database import Database
from wrappers.invertedindex import InvertedIndex
from utils.indexer import create_tokens

DATABASE_PATH = "filedumps/initialdb.filedump"
INDEX_PATH = "indexes/initialidx.index"

db = Database(DATABASE_PATH)
index = InvertedIndex(INDEX_PATH)

db.load(DATABASE_PATH)
index.load(INDEX_PATH)


def get_documents_tf_idf(querytext):
    
    result = index.get(querytext)
    returnlist = []
    for element in result['postinglist']:
        tfscore = element['freq']
        idfscore = math.log((db.size()/len(result['postinglist'])))
        tfidfscore = tfscore * idfscore

        returnlist.append({'docid': element['docid'],
                          'tfidf': tfidfscore})
    return returnlist

def score_document_for_query(querytext, returnlist):
    tfidfscores = get_documents_tf_idf(querytext)
    for element in tfidfscores:
        document = db.get(element['docid'])
        rt = document['retweet']
        like = document['like']

        documentscore = (abovezerosigmoid(rt) * 0.6 + abovezerosigmoid(like) * 0.4) * element['tfidf']
        returnlist = addScoreToDocument(element['docid'], documentscore, returnlist)
    
    return returnlist

def makeQuery(query):
    returnlist = []
    for token in query.split(' '):
        score_document_for_query(token,returnlist)
    
    return returnlist

def abovezerosigmoid(x):
  return (((1 / (1 + math.exp(-x))) - 0.5) * 2)

def addScoreToDocument(docid, score, doclist):
    newlist = doclist

    for element in newlist:
        if element['docid'] == docid:
            element['docscore'] = element['docscore'] + score
            return newlist
    
    newlist.append({'docid': docid, 'docscore': score})
    return newlist