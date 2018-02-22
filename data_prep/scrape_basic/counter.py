from data_prep.utils import postgres as redditdb
import nltk
import string
import json
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk import tokenize
import pickle
from data_prep.utils import timetools as timesort
import time
import pprint

stop_words = set(nltk.corpus.stopwords.words('english'))
other_stop_words = ['doge', 'part', 'rise', 'key', 'pay', 'etc', 'bot', 'moon', 'link', 'game', 'trust', 'data', 'fun', 'block', 'key', 'karma', 'via', 'decent', 'sub', 'get', 'time', 'change', 'life', 'ok']


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


def commenttokeniser(testobject, coinnames):
    testobject.texttoken = nltk.word_tokenize(testobject.text.translate(dict.fromkeys(string.punctuation)))
    #testobject.texttoken = [word.lower() for word in testobject.texttoken if len(word) > 1 and word not in stop_words]
    testobject.texttokencoin = [word.lower() for word in testobject.texttoken if word.lower() in coinnames and word not in stop_words and word not in other_stop_words]


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
            if int(data[x]['CMC_rank']) < 500:
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
        print('len of comment array (number of comments): ' + str(len(commentobjectarraynew)))
    return commentobjectarraynew


def everything(coinnames):
    comments = redditdb.returnwholetable("reddit_replies")
    commentobjectarray = [RedditComment(*x) for x in comments]
    print(len(commentobjectarray))
    for x in commentobjectarray:
        commenttokeniser(x, coinnames)
        freqcalc(x)
        sentcalc(x)
    writepickle(commentobjectarray)


def analysis():
    commentobjectarraynew = readpickle()
    for x in range(1000):
        if commentobjectarraynew[x].freqdist.most_common(10):
            print(commentobjectarraynew[x].freqdist.most_common(10))
            print(commentobjectarraynew[x].text)
            print('ups: ' + str(commentobjectarraynew[x].ups))
            print('downs: ' + str(commentobjectarraynew[x].downs))
            print('sent: ' + str(commentobjectarraynew[x].sent))
            print('createdepoch: ' + str(commentobjectarraynew[x].createdutc))
            print('createdutc: ' + str(timesort.epoch_to_utc(commentobjectarraynew[x].createdutc)))
            print('\n')


def specanalysis(coin):
    commentobjectarraynew = readpickle()
    for x in range(46000):
        templist = []
        if commentobjectarraynew[x].freqdist.most_common(10):
            for y in commentobjectarraynew[x].freqdist.most_common(10):
                templist.append(y[0])
            if coin in templist:
                print(commentobjectarraynew[x].freqdist.most_common(10))
                print(commentobjectarraynew[x].text)
                print('ups: ' + str(commentobjectarraynew[x].ups))
                print('downs: ' + str(commentobjectarraynew[x].downs))
                print('sent: ' + str(commentobjectarraynew[x].sent))
                print('subreddit: ' + str(commentobjectarraynew[x].subreddit))
                print('createdepoch: ' + str(commentobjectarraynew[x].createdutc))
                print('createdutc: ' + str(timesort.epoch_to_utc(commentobjectarraynew[x].createdutc)))
                print('\n')


def createarrayoftime():
    currenttime = timesort.currenttime()
    current = int(currenttime) - int(currenttime) % 3600
    timearray = []
    for x in range(300):
        timearray.append(current)
        current -= 3600
    return timearray


def coinsovertime(timee):
    coindict = {}
    commentobjectarraynew = readpickle()
    for x in commentobjectarraynew:
        if x.freqdist.most_common(10):
            mostcommon = x.freqdist.most_common(10)
            for coin in mostcommon:
                if coin[0] not in coindict and coin[0] not in other_stop_words:
                    coindict[coin[0]] = [x.createdutc]
                elif coin[0] not in other_stop_words:
                    coindict[coin[0]].append(x.createdutc)
    print('Dictionary of coins and the time blocks that they appear in: ')
    print(coindict)

    tempdictcount = []
    for x in coindict:
        temptuple = tuple([x, len(coindict[x])])
        tempdictcount.append(temptuple)
    tempdictcount.sort(key=lambda y: y[1], reverse=True)
    print('\n Number of times each word is mentioned: ')
    print(tempdictcount)
    print('n')

    newcoindict = {}
    for x in coindict:
        lasttimez = time.time()
        newcoindict[x] = {}
        for timez in timee:
            for y in coindict[x]:
                if lasttimez > y > timez:
                    if timez not in newcoindict[x]:
                        newcoindict[x][timez] = 0
                    if timez in newcoindict[x]:
                        newcoindict[x][timez] += 1
            lasttimez = timez
    return newcoindict


def beep():
    coinnames = getcoinnames()
    everything(coinnames)  # fetches from db, does all the counting, and nltk calculations and writes to pickle


def boop():
    timee = timesort.timearray_pastxintervals(3600, 300)  #c reate time array for coinsovertime
    coinswithtime = coinsovertime(timee)  # generates coins over time

    cointosearch = 'poly'
    for x in coinswithtime[cointosearch]:
        print(str(timesort.epoch_to_utc(x))+": " + str(coinswithtime[cointosearch][x]))

    #analysis()  # reads pickle, display examples of the comment text and their respective coin counts, sentiment, votes, creation time
    specanalysis(cointosearch)  # analysis but for specific coin


def main():
    print(timesort.epoch_to_utc(time.time()))
    boop()
    print(timesort.epoch_to_utc(time.time()))


main()

'''
records = redditb.get_posts()
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