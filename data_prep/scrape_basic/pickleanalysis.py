import pickle
from utils import timetools as timesort, postgres as redditdb, coinlist as cointools
from data_prep.scrape_basic.redditcomment import RedditComment


other_stop_words = ['doge', 'part', 'rise', 'key', 'pay', 'etc', 'bot', 'moon', 'link', 'game', 'trust', 'data', 'fun', 'block', 'key', 'karma', 'via', 'decent', 'sub', 'get', 'time', 'change', 'life', 'ok']


def readpickle(picklefile):
    with open(picklefile, "rb") as picklearray:
        result = pickle.load(picklearray)
        print('\nlen of pickle array that is being read in (number of entries): ' + str(len(result)) + '\n')
    return result


def coinsovertime(commentobjectarray, timee):
    coindict = {}
    # generate dictionary of coins and their epoch time blocks {'ven': {1520534400: 2, 1520534225: 1}, 'eth':...}}
    for x in commentobjectarray:
        if x.coinsmentioned:
            for coin in x.coinsmentioned:
                if coin not in coindict and coin not in other_stop_words:
                    coindict[coin] = {}
                    coindict[coin][x.createdutc] = x.ups
                elif coin not in other_stop_words:
                    coindict[coin][x.createdutc] = x.ups
    print(coindict)


timearray = timesort.timearray_pastxintervals(3600, 70)  # create time array for coinsovertime (interval, length)
coinarray = readpickle('commentarray')
coinsovertime(coinarray, timearray)