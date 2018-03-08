import nltk
import string
import json
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk import tokenize
import pickle
from utils import timetools as timesort, postgres as redditdb, coinlist as cointools
import matplotlib.dates
import matplotlib.pyplot as plt
import time
import pprint
from decimal import Decimal
import requests

stop_words = set(nltk.corpus.stopwords.words('english'))
other_stop_words = ['doge', 'part', 'rise', 'key', 'pay', 'etc', 'bot', 'moon', 'link', 'game', 'trust', 'data', 'fun', 'block', 'key', 'karma', 'via', 'decent', 'sub', 'get', 'time', 'change', 'life', 'ok']

coinlistrankfilter = 500
coinlistsource = 0 #0 for local, 1 for github


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
    def __init__(self, id, author, h, text, ups, subreddit, createdutc, parent_id):
        self.id = id
        self.author = author
        self.hash = None
        self.text = text
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

'''
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
'''

def writepickle(objecttowrite):
    with open("commentarray", "wb") as commentarray:
        pickle.dump(objecttowrite, commentarray)


def readpickle():
    with open("commentarray", "rb") as commentarray:
        commentobjectarraynew = pickle.load(commentarray)
        print('\nlen of pickle comment array that is being read in (number of comments): ' + str(len(commentobjectarraynew)) + '\n')
    return commentobjectarraynew

'''
def fetch_analyse_update():
    coinnames = cointools.fetch_coinnameslist_rankfilter(coinlistrankfilter, coinlistsource)
    existingarray = readpickle()
    lasttime = 0
    for x in existingarray:
        if x.createdutc > lasttime:
            lasttime = x.createdutc
    comments = redditdb.returnwholetablefromtime("reddit_replies", lasttime)
    print(str(len(comments)) + ' new comments retrieved since ' + str(lasttime) + ' -- ' + str(timesort.epoch_to_utc(lasttime)))
    commentobjectarray = [RedditComment(*x) for x in comments]
    print("NLP might take a while. Number of comments processing: " + str(len(commentobjectarray)))
    xcount = 0
    oldcountp = 0
    for x in commentobjectarray:
        commenttokeniser(x, coinnames)
        freqcalc(x)
        sentcalc(x)
        existingarray.append(x)
        xcount += 1
        newcountp = (xcount/len(commentobjectarray))*100
        if newcountp - oldcountp >= 1:
            oldcountp = newcountp
            print(str(round(newcountp))+"% completed.")
    writepickle(existingarray)
    print('pickle updated')


def fetch_analyse_updatepastday():
    coinnames = cointools.fetch_coinnameslist_rankfilter(coinlistrankfilter, coinlistsource)
    temparray = readpickle()
    existingarray = []
    lasttime = timesort.currenttime() - (60*60*24)
    for x in temparray:
        if x.createdutc < lasttime:
            existingarray.append(x)
    comments = redditdb.returnwholetablefromtime("reddit_replies", lasttime)
    print(str(len(comments)) + ' new comments retrieved since ' + str(lasttime) + ' -- ' + str(timesort.epoch_to_utc(lasttime)))
    commentobjectarray = [RedditComment(*x) for x in comments]
    print("NLP might take a while. Number of comments processing: " + str(len(commentobjectarray)))
    xcount = 0
    oldcountp = 0
    for x in commentobjectarray:
        commenttokeniser(x, coinnames)
        freqcalc(x)
        sentcalc(x)
        existingarray.append(x)
        xcount += 1
        newcountp = (xcount/len(commentobjectarray))*100
        if newcountp - oldcountp >= 1:
            oldcountp = newcountp
            print(str(round(newcountp))+"% completed.")
    writepickle(existingarray)
    print('pickle updated')


def fetch_analyse_write():
    coinnames = cointools.fetch_coinnameslist_rankfilter(coinlistrankfilter, coinlistsource)
    comments = redditdb.returnwholetable("reddit_replies")
    commentobjectarray = [RedditComment(*x) for x in comments]
    print("NLP might take a while. Number of comments processing: " + str(len(commentobjectarray)))
    xcount = 0
    oldcountp = 0
    for x in commentobjectarray:
        commenttokeniser(x, coinnames)
        freqcalc(x)
        sentcalc(x)
        xcount += 1
        newcountp = (xcount/len(commentobjectarray))*100
        if newcountp - oldcountp >= 1:
            oldcountp = newcountp
            print(str(round(newcountp))+"% completed.")
    writepickle(commentobjectarray)
'''


def coinsovertime(commentobjectarray, timee):
    coindict = {}
    # generate dictionary of coins and their epoch time blocks {'stellar':[123,456],'eth':[123,345]}
    for x in commentobjectarray:
        if x.freqdist.most_common(10):
            mostcommon = x.freqdist.most_common(10)
            for coin in mostcommon:
                if coin[0] not in coindict and coin[0] not in other_stop_words:
                    coindict[coin[0]] = {}
                    coindict[coin[0]][x.createdutc] = x.ups
                elif coin[0] not in other_stop_words:
                    coindict[coin[0]][x.createdutc] = x.ups

    # sentiment
    coindictpre_sent = {}
    # generate dictionary of coins and their epoch time blocks {'stellar':[123,456],'eth':[123,345]}
    for x in commentobjectarray:
        if x.freqdist.most_common(10):
            mostcommon = x.freqdist.most_common(10)
            for coin in mostcommon:
                if coin[0] not in coindictpre_sent and coin[0] not in other_stop_words:
                    coindictpre_sent[coin[0]] = {}
                    coindictpre_sent[coin[0]][x.createdutc] = x.sent
                elif coin[0] not in other_stop_words:
                    coindictpre_sent[coin[0]][x.createdutc] = x.sent

    # without ups
    # Creates new dictionary of coins with timeblocks and count in each timeblock {'stellar':{123:1,456,2}}
    # counts for the PAST interval of timeblock (eg. 5-6pm will be 6pm)
    coindictplain = {}
    coindictups = {}
    coindictsent = {}
    coindictupssent = {}
    for x in coindict:
        coindictplain[x] = {}
        coindictups[x] = {}
        coindictsent[x] = {}
        coindictupssent[x] = {}
        for timez in range(len(timee) - 1):
            prevtimez = timee[timez + 1]
            for y in coindict[x]:
                if timee[timez] > y > prevtimez:
                    if timee[timez] not in coindictplain[x]:
                        coindictplain[x][timee[timez]] = 0
                    if timee[timez] in coindictplain[x]:
                        coindictplain[x][timee[timez]] += 1
                    if timee[timez] not in coindictups[x]:
                        coindictups[x][timee[timez]] = 0
                    if timee[timez] in coindictups[x]:
                        coindictups[x][timee[timez]] += coindict[x][y]
                    if timee[timez] not in coindictsent[x]:
                        coindictsent[x][timee[timez]] = 0
                    if timee[timez] in coindictsent[x]:
                        coindictsent[x][timee[timez]] += coindictpre_sent[x][y]
                    if timee[timez] not in coindictupssent[x]:
                        coindictupssent[x][timee[timez]] = 0
                    if timee[timez] in coindictupssent[x]:
                        coindictupssent[x][timee[timez]] += (coindictpre_sent[x][y] + coindict[x][y])

    # Counts how many times each coin is mentioned
    coinscount = []
    for x in coindictplain:
        tempcount = 0
        for y in coindictplain[x]:
            tempcount += coindictplain[x][y]
        temptuple = tuple([x, tempcount])
        coinscount.append(temptuple)
        coinscount.sort(key=lambda y: y[1], reverse=True)

    return coindictups, coindictplain, coindictsent, coindictupssent, coinscount


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
                print('sent: ' + str(commentobjectarray[x].sent))
                print('subreddit: ' + str(commentobjectarray[x].subreddit))
                print('createdepoch: ' + str(commentobjectarray[x].createdutc))
                print('createdutc: ' + str(timesort.epoch_to_utc(commentobjectarray[x].createdutc)))
                print('\n')


def coinovertimeprinter(coinswithtime, cointosearch):
    print('Printing mentions for '+cointosearch)
    for x in coinswithtime[cointosearch]:
        print(str(x) + '  ' + str(timesort.epoch_to_utc(x))+": " + str(coinswithtime[cointosearch][x]))


def coinmentionsprinter(coinscount):
    print('\n Number of times each word is mentioned: ')
    print(coinscount)
    print('\n')


def grapher(coinswithtime, cointosearch, cointosearchccname):
    cointime = []
    coincount = []
    for x in coinswithtime[cointosearch]:
        cointime.append(matplotlib.dates.epoch2num(x))
        coincount.append(coinswithtime[cointosearch][x])

    response = requests.get("https://min-api.cryptocompare.com/data/histohour?fsym="+cointosearchccname+"&tsym=BTC&aggregate=1&limit=500")
    data = response.json()
    print('Cryptocompare fetch data')
    print(data['Data'])
    coinprice = []
    for x in cointime:
        for y in data['Data']:
            if x == matplotlib.dates.epoch2num(y['time']):
                coinprice.append(y['open'])
    print('\ncoin count')
    print(coincount)
    print('\ncoinprice before')
    print(coinprice)
    coinprice = [((x-min(coinprice))/(max(coinprice)-min(coinprice))) for x in coinprice]
    coincount = [(x-min(coincount))/(max(coincount)-min(coincount)) for x in coincount]
    print('\ncoinpriceafter')
    print(coinprice)



    fig, ax = plt.subplots()
    # Plot the date using plot_date rather than plot
    ax.plot_date(cointime, coincount, '*-', label='coincount')
    ax.plot_date(cointime, coinprice, '--', label='coinprice')
    # Choose your xtick format string
    date_fmt = '%d-%m %H:%M'
    # Use a DateFormatter to set the data to the correct format.
    date_formatter = matplotlib.dates.DateFormatter(date_fmt)
    ax.xaxis.set_major_formatter(date_formatter)
    # Sets the tick labels diagonal so they fit easier.
    fig.autofmt_xdate()
    ax.xaxis.set_major_locator(matplotlib.dates.MinuteLocator(interval=240))
    fig.suptitle(cointosearch, fontsize=20)
    ax.legend(loc='lower right')
    plt.show()


def main():
    print('Start time: ' + str(timesort.epoch_to_utc(time.time())) + '\n')

    fetch_analyse_write()

    coinarray = readpickle()

    timearray = timesort.timearray_pastxintervals(3600, 70)  # create time array for coinsovertime (interval, length)
    coinswithtimeups, coinswithtime, coinswithsent, coinswithupsent, coinscount = coinsovertime(coinarray, timearray)
    coinmentionsprinter(coinscount)
    coinswithtime = coinswithupsent
    cointosearch = 'NEO'.lower()
    cointosearchccname = 'NEO'
    #coinovertimeprinter(coinswithtime, cointosearch)
    #printcomments(cointosearch, coinarray)
    grapher(coinswithtime, cointosearch, cointosearchccname)

    print('\nEnd time: ' + str(timesort.epoch_to_utc(time.time())))


#main()
print(cointools.fetch_coinnameslist_rankfilter(coinlistrankfilter, coinlistsource))
print(len(cointools.fetch_coinnameslist_rankfilter(coinlistrankfilter, coinlistsource)))

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