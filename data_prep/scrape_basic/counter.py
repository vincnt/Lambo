from data_prep.scrape_basic import db as redditdb
import nltk
import string
from nltk.corpus import stopwords


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
    def __init__(self, id, author, hash, text, downs, ups, subreddit, createdutc, parent_id):
        self.id = id
        self.author = author
        self.hash = hash
        self.text = text
        self.downs = downs
        self.ups = ups
        self.subreddit = subreddit
        self.createdutc = createdutc
        self.parent_id = parent_id
        self.texttoken = []


def posttokeniser(testobject):
    testobject.titletoken = nltk.word_tokenize(testobject.title.translate(dict.fromkeys(string.punctuation)))
    testobject.titletoken = [word.lower() for word in testobject.titletoken]
    testobject.titletoken = [word for word in testobject.titletoken if len(word) > 1]
    testobject.titletoken = [word for word in testobject.titletoken if word not in stop_words]


def commenttokeniser(testobject):
    testobject.texttoken = nltk.word_tokenize(testobject.text.translate(dict.fromkeys(string.punctuation)))
    testobject.texttoken = [word.lower() for word in testobject.texttoken]
    testobject.texttoken = [word for word in testobject.texttoken if len(word) > 1]
    testobject.texttoken = [word for word in testobject.texttoken if word not in stop_words]



'''
records = redditdb.get_posts()
postobjectarray = [RedditPost(*x) for x in records]
print(len(postobjectarray))
stop_words = set(nltk.corpus.stopwords.words('english'))
for x in postobjectarray:
    posttokeniser(x)
combinedtext = []
for x in postobjectarray:
    combinedtext = combinedtext + x.titletoken

fdist = nltk.FreqDist(combinedtext)

for word, frequency in fdist.most_common(30):
    print(u'{} - {}'.format(word, frequency))
'''

comments = redditdb.get_comments()
commentobjectarray = [RedditComment(*x) for x in comments]
print(len(commentobjectarray))
stop_words = set(nltk.corpus.stopwords.words('english'))
for x in commentobjectarray:
    commenttokeniser(x)
combinedtext = []
for x in commentobjectarray:
    combinedtext = combinedtext + x.texttoken
print(len(combinedtext))
fdist = nltk.FreqDist(combinedtext)
for word, frequency in fdist.most_common(100):
    print(u'{} - {}'.format(word, frequency))