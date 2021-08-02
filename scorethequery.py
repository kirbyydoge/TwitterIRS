import math

def tf_idf(querytext, document, collection):
    tfrawscore = document['content'].count(querytext)
    idfrawscore = 0
    for sampledocument in collection:
        if(querytext in sampledocument['content']):
            idfrawscore +=1
    
    tfscore = math.log(1+idfrawscore)/math.log(1+len(collection))

def score_document_for_query(querytext, document, collection):
    retweetrawscore = document['retweet']
    likerawscore = document['like']
    hashtagrawscore = 1 if querytext in document['hashtags'] else 0
    tfidfscore = tf_idf(querytext, document, collection)

    finalscore = math.log(abovezerosigmoid(retweetrawscore) * 0.3 + abovezerosigmoid(likerawscore) * 0.3 + hashtagrawscore * 0.4) + tfidfscore

def abovezerosigmoid(x):
  return (((1 / (1 + math.exp(-x))) - 0.5) * 2)
