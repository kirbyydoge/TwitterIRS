import math
from wrappers.database import Database
from wrappers.invertedindex import InvertedIndex

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
        idfscore = math.log(((db.size()/(1+len(result['postinglist'])))+1))
        tfidfscore = float(tfscore) * idfscore

        returnlist.append({'docid': element['docid'],
                          'tfidf': tfidfscore})
    return returnlist

def score_document_for_query(querytext, returnlist, multiplier = 1):
    tfidfscores = get_documents_tf_idf(querytext)
    for element in tfidfscores:
        document = db.get(element['docid'])
        rt = document['retweet']
        if(rt == ''):
            rt = 0;
        else:
            rt = float(rt)
        like = document['like']
        if(like == ''):
            like = 0;
        else:
            like = float(like)

        documentscore = (abovezerosigmoid(rt) * 0.6 + abovezerosigmoid(like) * 0.4)*element['tfidf'] + element['tfidf'] * multiplier
        returnlist = addScoreToDocument(element['docid'], documentscore, returnlist)
    
    return returnlist


def makeQuery(query):
    querydict = vectorofquery(query)
    returnlist = []
    for token in querydict.keys():
        score_document_for_query(token,returnlist,querydict[token])
    
    return returnlist

def abovezerosigmoid(x):
  return (((1 / (1 + math.exp(-1*x))) - 0.5) * 2)

def addScoreToDocument(docid, score, doclist):
    newlist = doclist

    for element in newlist:
        if element['docid'] == docid:
            element['docscore'] = element['docscore'] + score
            return newlist
    
    newlist.append({'docid': docid, 'docscore': score})
    return newlist

def vectorofquery(query):
    querydict = {}
    for token in query.split(' '):
        if token not in querydict.keys():
            querydict[token] = 1
        else:
            querydict[token] = querydict[token] +1
    return querydict



def makeQueryFor(string):
    for element in makeQuery(string.lower()):
        print('*****************************************')
        print("")
        document = db.get(element['docid'])
        print(document['content'])
        print('Score :' + str(element['docscore']))

makeQueryFor('elon musk')
