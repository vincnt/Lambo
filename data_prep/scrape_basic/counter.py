import nltk
import string
import json
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk import tokenize
import pickle
from utils import timetools as timesort, postgres as redditdb
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
    testobject.texttokencoin = [word.lower() for word in testobject.texttoken if word.lower() in coinnames and word not in stop_words and word not in other_stop_words]


def freqcalc(x):
    x.freqdist = nltk.FreqDist(x.texttokencoin)


def sentcalc(x):
    sid = SentimentIntensityAnalyzer()
    sentText = tokenize.sent_tokenize(x.text)
    count = 0
    sent = 0
    for sentence in sentText:
        count +=1
        ss = sid.polarity_scores(sentence)
        sent += ss['compound']
    if count != 0:
        sent = float(sent / count)
    x.sent = sent


def getcoinnames():
    coinnames = []
    with open('/home/vincent/Projects/Crypto/Lambo/utils/coinlist.json') as currentlist:
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
        print('\nlen of comment array (number of comments): ' + str(len(commentobjectarraynew)) + '\n')
    return commentobjectarraynew


def fetch_analyse_write():
    coinnames = getcoinnames()
    comments = redditdb.returnwholetable("reddit_replies")
    commentobjectarray = [RedditComment(*x) for x in comments]
    print("NLP might take a while. Number of comments processing: " + str(len(commentobjectarray)))
    a = len(commentobjectarray)/100
    b = 0
    c = 0
    for x in commentobjectarray:
        commenttokeniser(x, coinnames)
        freqcalc(x)
        sentcalc(x)
        b += 1
        if b % a == 0:
            c += 1
            print(str(c)+"% completed.")
    writepickle(commentobjectarray)


def coinsovertime(commentobjectarray, timee):
    coindict = {}
    # generate dictionary of coins and their epoch time blocks {'stellar':[123,456],'eth':[123,345]}
    for x in commentobjectarray:
        if x.freqdist.most_common(10):
            mostcommon = x.freqdist.most_common(10)
            for coin in mostcommon:
                if coin[0] not in coindict and coin[0] not in other_stop_words:
                    coindict[coin[0]] = [x.createdutc]
                elif coin[0] not in other_stop_words:
                    coindict[coin[0]].append(x.createdutc)

    # Creates new dictionary of coins with timeblocks and count in each timeblock {'stellar':{123:1,456,2}}
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

    # Counts how many times each coin is mentioned
    coinscount = []
    for x in coindict:
        coinscount.append(tuple([x, len(coindict[x])]))
    coinscount.sort(key=lambda y: y[1], reverse=True)

    return newcoindict, coinscount


def printcomments(coin, commentobjectarray):
    for x in range(len(commentobjectarray)):
        templist = []
        if commentobjectarray[x].freqdist.most_common(10):
            for y in commentobjectarray[x].freqdist.most_common(10):
                templist.append(y[0])
            if coin in templist:
                print(commentobjectarray[x].freqdist.most_common(10))
                print(commentobjectarray[x].text)
                print('ups: ' + str(commentobjectarray[x].ups))
                print('downs: ' + str(commentobjectarray[x].downs))
                print('sent: ' + str(commentobjectarray[x].sent))
                print('subreddit: ' + str(commentobjectarray[x].subreddit))
                print('createdepoch: ' + str(commentobjectarray[x].createdutc))
                print('createdutc: ' + str(timesort.epoch_to_utc(commentobjectarray[x].createdutc)))
                print('\n')


def coinswithtimeprinter(coinswithtime, cointosearch):
    for x in coinswithtime[cointosearch]:
        print(str(timesort.epoch_to_utc(x))+": " + str(coinswithtime[cointosearch][x]))


def coinmentionsprinter(coinscount):
    print('\n Number of times each word is mentioned: ')
    print(coinscount)
    print('\n')


def main():
    print(timesort.epoch_to_utc(time.time()))
    # fetch_analyse_write()
    coinarray = readpickle()
    timearray = timesort.timearray_pastxintervals(3600, 100)  # create time array for coinsovertime (interval, length)
    coinswithtime, coinscount = coinsovertime(coinarray, timearray)
    coinmentionsprinter(coinscount)
    #coinswithtimeprinter(coinswithtime, 'stellar')
    #printcomments('poly', coinarray)

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