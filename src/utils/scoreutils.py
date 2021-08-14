import math

def pre_process_query(query):
    post_process = query.lower()
    post_process = post_process.split(" ")
    return post_process

def score_unigram(query, index, lamb=0.8):
    query = pre_process_query(query)
    accumulators = {}
    for term in query:
        term_index = index.get(term)
        if not term_index:
            continue
        postlist = term_index["postinglist"]
        postlist_freq = int(term_index["total_freq"])
        postlist_len = 0
        partial_sums = []
        for doc in postlist:
            cur_docid = int(doc["docid"])
            cur_freq = int(doc["freq"])
            cur_len = int(doc["doclen"])
            postlist_len += int(cur_len)
            cur_sum = lamb * (cur_freq / cur_len)
            partial_sums.append((cur_docid, cur_sum))
        postlist_sum = (1 - lamb) * (postlist_freq / postlist_len)
        for docid, partial_sum in partial_sums:
            total_sum = partial_sum + postlist_sum
            if docid in accumulators:
                accumulators[docid] *= total_sum
            else:
                accumulators[docid] = total_sum
    sorted_docs = sorted(accumulators, key=lambda x: accumulators[x], reverse=True)
    return sorted_docs

"""
NOTE:
    Kodun paket yapisini duzenlemek adina utility fonksiyonlarini buraya tasidim.
    Biraz modifiye etmem gerekti global index ve db yerine bunlari referans olarak kullanmamiz daha duzenli olur API icin.
    Ayrica isimlerin biraz duzensizdi, java stili olan isimleri python/eski c genel kullanimina cevirdim.
"""
#
# TFIDF LIKE RETWEET BEGIN
#
def single_term_tfidf_scores(querytext, index, db):
    result = index.get(querytext)
    if not result:
        return []
    returnlist = []
    for element in result['postinglist']:
        tfscore = int(element['freq'])
        idfscore = math.log((db.size() / len(result['postinglist'])))
        tfidfscore = tfscore * idfscore
        returnlist.append({'docid': element['docid'],
                          'tfidf': tfidfscore})
    return returnlist

def score_documents_for_query(querytext, index, db, use_likert, retweet_multiplier, like_multiplier):
    tfidfscores = single_term_tfidf_scores(querytext, index, db)
    returnlist = []
    for element in tfidfscores:
        document = db.safe_get(element['docid'])
        rt = int(document['retweet'])
        like = int(document['like'])
        if use_likert:
            documentscore = (above_zero_sigmoid(rt) * retweet_multiplier + above_zero_sigmoid(like) * like_multiplier) * element['tfidf']
        else:
            documentscore = element['tfidf']
        returnlist = add_score_to_document(element['docid'], documentscore, returnlist)
    return returnlist
    
def score_tfidf(query, index, db, use_likert=True, retweet_multiplier = 0.6, like_multiplier = 0.4):
    query = pre_process_query(query)
    returnlist = []
    for token in query:
        returnlist += score_documents_for_query(token, index, db, use_likert, retweet_multiplier, like_multiplier)
    returnlist = sorted(returnlist, key=lambda x: x["docscore"], reverse=True)
    return returnlist

def above_zero_sigmoid(x):
  return (((1 / (1 + math.exp(-x))) - 0.5) * 2)

def add_score_to_document(docid, score, doclist):
    newlist = doclist
    for element in newlist:
        if element['docid'] == docid:
            element['docscore'] = element['docscore'] + score
            return newlist
    newlist.append({'docid': docid, 'docscore': score})
    return newlist

#
# TFIDF LIKE RETWEET END
#

#UNWEIGHTED COSINE SCORE (?)
def score_documents_uwcos(token, index, db, returnlist):
    result = index.get(token)
    if result:
        newlist = []
        for element in result['postinglist']:
            tfscore = float(element['freq'])
            documentscoreforquery = tfscore / float(element["doclen"])
            newlist.append({'docid': element['docid'],
                            'cosinescore': documentscoreforquery})
            returnlist = add_score_to_document_cosine(element['docid'], documentscoreforquery, returnlist, db)
    return returnlist

def score_query_unweighted_cosine(query, index, db):
    returnlist = []
    for token in query.split(' '):
        returnlist += score_documents_uwcos(token, index, db, returnlist)
    returnlist = sorted(returnlist, key=lambda x: x["cosinescore"], reverse=True)
    return returnlist

#
# HELPER FUNCTIONS BEGIN
#

def above_zero_sigmoid(x):
  return (((1 / (1 + math.exp(-x))) - 0.5) * 2)

def add_score_to_document(docid, score, doclist):
    newlist = doclist
    for element in newlist:
        if element['docid'] == docid:
            element['docscore'] = element['docscore'] + score
            return newlist
    newlist.append({'docid': docid, 'docscore': score})
    return newlist

def add_score_to_document_cosine(docid, score, doclist, db):
    newlist = doclist
    for element in newlist:
        if element['docid'] == docid:
            element['cosinescore'] = element['cosinescore'] + score/2
            return newlist
    document = db.safe_get(element['docid'])
    rt = int(document['retweet'])
    like = int(document['like'])
    totalrtlikescore = above_zero_sigmoid(rt+like)
    newlist.append({'docid': docid, 'cosinescore': score/2 + totalrtlikescore/2})

    return newlist

#
# HELPER FUNCTIONS END
#