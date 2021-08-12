def pre_process_query(query):
    post_process = query.lower()
    post_process = post_process.split(" ")
    return post_process

def score_unigram(query, index, lamb=0.8):
    query = pre_process_query(query)
    accumulators = {}
    for term in query:
        term_index = index.get(term)
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
