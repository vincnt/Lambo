from data_prep.scrape_basic import db as redditdb
import nltk
import string
import json
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk import tokenize
import pickle

stop_words = set(nltk.corpus.stopwords.words('english'))
other_stop_words = ['part', 'rise', 'key']


class RedditPost:
    def __init__(self, post_id, author, subreddit, title, h, text, downs, ups, likes, score, createdutc, num_comments):
        self.post_id = post_id
        self.author = author
        self.subreddit = subreddit
        self.title = title
        self.hash = h
        self.text = text
        self.downs = downs
        self.ups = ups
        self.likes = likes
        self.score = score
        self.createdutc = createdutc
        self.num_comments = num_comments
        self.coincount = {}
        self.titletoken = []


class RedditComment:
    def __init__(self, id, author, h, text, downs, ups, subreddit, createdutc, parent_id):
        self.id = id
        self.author = author
        self.hash = None
        self.text = text
        self.downs = downs
        self.ups = ups
        self.subreddit = subreddit
        self.createdutc = createdutc
        self.parent_id = parent_id
        self.texttoken = []
        self.texttokencoin = []
        self.texttokensentiment = 0
        self.freqdist = None
        self.sent = 0


def posttokeniser(testobject):
    testobject.titletoken = nltk.word_tokenize(testobject.title.translate(dict.fromkeys(string.punctuation)))
    testobject.titletoken = [word.lower() for word in testobject.titletoken]
    testobject.titletoken = [word for word in testobject.titletoken if len(word) > 1]
    testobject.titletoken = [word for word in testobject.titletoken if word not in stop_words]


def commenttokeniser(testobject):
    testobject.texttoken = nltk.word_tokenize(testobject.text.translate(dict.fromkeys(string.punctuation)))
    #testobject.texttoken = [word.lower() for word in testobject.texttoken if len(word) > 1 and word not in stop_words]
    testobject.texttokencoin = [word.lower() for word in testobject.texttoken if word in coinnames and word not in stop_words and word not in other_stop_words]


def freqcalc(x):
    x.freqdist = nltk.FreqDist(x.texttokencoin)


def sentcalc(x):
    sid = SentimentIntensityAnalyzer()
    sentText = tokenize.sent_tokenize(x.text)
    count=0
    sent=0
    for sentence in sentText:
        count +=1
        ss = sid.polarity_scores(sentence)
        sent += ss['compound']
    if count != 0:
        sent = float(sent / count)
    x.sent = sent


def getcoinnames():
    coinnames = []
    with open('/home/vincent/Projects/Crypto/Lambo/coinlist.json') as currentlist:
        data = json.load(currentlist)
        for x in data:
            if int(data[x]['CMC_rank']) < 300:
                coinnames.append(x.lower())
                if 'CC_key' in data[x]:
                    coinnames.append(data[x]['CC_key'].lower())
                coinnames.append(data[x]['CMC_ID'].lower())
                coinnames.append(data[x]['Name'].lower())
    return set(coinnames)


def writepickle(objecttowrite):
    with open("commentarray", "wb") as commentarray:
        pickle.dump(objecttowrite, commentarray)


def readpickle():
    with open("commentarray", "rb") as commentarray:
        commentobjectarraynew = pickle.load(commentarray)
    return commentobjectarraynew


coinnames = getcoinnames()


def everything():
    comments = redditdb.get_comments()
    commentobjectarray = [RedditComment(*x) for x in comments]
    print(coinnames)
    print(len(commentobjectarray))
    for x in commentobjectarray:
        commenttokeniser(x)
        freqcalc(x)
        sentcalc(x)
    writepickle(commentobjectarray)


def reader():
    commentobjectarraynew = readpickle()
    for x in range(1000):
        if commentobjectarraynew[x].freqdist.most_common(10) != []:
            print(commentobjectarraynew[x].freqdist.most_common(10))
            print(commentobjectarraynew[x].text)
            print('ups: '+ str(commentobjectarraynew[x].ups))
            print('sent: ' + str(commentobjectarraynew[x].sent))
            print('\n')


reader()
'''
records = redditdb.get_posts()
postobjectarray = [RedditPost(*x) for x in records]
print(len(postobjectarray))
stop_words = set(nltk.corpus.stopwords.words('english'))
for x in postobjectarray:
    posttokeniser(x)

with open("test.txt", "rb") as fp:   # Unpickling
...   b = pickle.load(fp)
fdist = nltk.FreqDist(combinedtext)
for word, frequency in fdist.most_common(100):
    print(u'{} - {}'.format(word, frequency))
'''