# perform analysis on pickle file

import pickle
from utils import timetools as timesort, postgres as redditdb, coinlist as cointools
from data_prep.scrape_basic.redditcomment import RedditComment


other_stop_words = ['doge', 'part', 'rise', 'key', 'pay', 'etc', 'bot', 'moon', 'link', 'game', 'trust', 'data', 'fun', 'block', 'key', 'karma', 'via', 'decent', 'sub', 'get', 'time', 'change', 'life', 'ok']


def readpickle(picklefile):
    with open(picklefile, "rb") as picklearray:
        result = pickle.load(picklearray)
        print('\nlen of pickle array that is being read in (number of entries): ' + str(len(result)) + '\n')
    return result


def rawcoinscount(commentobjectarray):
    rawcoindictups = {}
    rawcoindictsent = {}
    # generate dictionary of coins and their epoch time blocks {'ven': {1520534400: 1, 1520534225: 1}, 'eth':...}}
    for x in commentobjectarray:
        if x.coinsmentioned:
            for coin in x.coinsmentioned:
                if coin not in rawcoindictups and coin not in other_stop_words:
                    rawcoindictups[coin] = {}
                    rawcoindictsent[coin] = {}
                    rawcoindictups[coin][x.createdutc] = x.ups
                    rawcoindictsent[coin][x.createdutc] = x.sentiment
                elif coin not in other_stop_words:
                    rawcoindictups[coin][x.createdutc] = x.ups
                    rawcoindictsent[coin][x.createdutc] = x.sentiment
    return rawcoindictups, rawcoindictsent


def coinsovertime(coindict, coindictpre_sent, time_array):
    # Creates new dictionary of coins with timeblocks and count in each timeblock {'stellar':{123:1,456,2}}
    # counts for the PAST interval of timeblock (eg. 5-6pm will be 6pm)
    coindictplain = {}
    coindictups = {}
    coindictsent = {}
    coindictupsplussent = {}
    coindictupstimessent = {}
    for coin in coindict:
        coindictplain[coin] = {}
        coindictups[coin] = {}
        coindictsent[coin] = {}
        coindictupsplussent[coin] = {}
        coindictupstimessent[coin] = {}
        for timeblock in range(len(time_array) - 1):
            prevtimez = time_array[timeblock + 1]
            for y in coindict[coin]:
                if time_array[timeblock] > y > prevtimez:
                    if time_array[timeblock] not in coindictplain[coin]:
                        coindictplain[coin][time_array[timeblock]] = 0
                        coindictups[coin][time_array[timeblock]] = 0
                        coindictsent[coin][time_array[timeblock]] = 0
                        coindictupsplussent[coin][time_array[timeblock]] = 0
                        coindictupstimessent[coin][time_array[timeblock]] = 0
                    if time_array[timeblock] in coindictplain[coin]:
                        coindictplain[coin][time_array[timeblock]] += 1
                        coindictups[coin][time_array[timeblock]] += coindict[coin][y]
                        coindictsent[coin][time_array[timeblock]] += coindictpre_sent[coin][y]
                        coindictupsplussent[coin][time_array[timeblock]] += (coindictpre_sent[coin][y] + coindict[coin][y])
                        coindictupstimessent[coin][time_array[timeblock]] += (coindictpre_sent[coin][y] * coindict[coin][y])
    return coindictplain, coindictups, coindictsent, coindictupsplussent, coindictupstimessent


def totalcountpercoin(coindictplain):
    # Counts how many times each coin is mentioned
    coinscount = []
    for coin in coindictplain:
        tempcount = 0
        for y in coindictplain[coin]:
            tempcount += coindictplain[coin][y]
        temptuple = tuple([coin, tempcount])
        coinscount.append(temptuple)
        coinscount.sort(key=lambda y: y[1], reverse=True)
    return coinscount


def returntotalcountpercoin():
    coinarray = readpickle('commentarray')
    coincountups, coincountsent = rawcoinscount(coinarray)
    timearray = timesort.timearray_pastxintervals(3600,400)  # time array for coinsovertime (interval in seconds, length)
    cd_plain, cd_ups, cd_sent, cd_upsplussent, cd_upstimessent = coinsovertime(coincountups, coincountsent, timearray)
    totalcountarray = totalcountpercoin(cd_plain)
    return totalcountarray


def return_coindicts():
    coinarray = readpickle('commentarray')
    coincountups, coincountsent = rawcoinscount(coinarray)
    timearray = timesort.timearray_pastxintervals(3600, 1350)  # time array for coinsovertime (interval in seconds, length)
    cd_plain, cd_ups, cd_sent, cd_upsplussent, cd_upstimessent = coinsovertime(coincountups, coincountsent, timearray)
    return cd_plain, cd_ups, cd_sent, cd_upsplussent, cd_upstimessent


if __name__ == '__main__':
    totalcoincounts = returntotalcountpercoin()
    cd_plain, cd_ups, cd_sent, cd_upsplussent, cd_upstimessent = return_coindicts()
    print(totalcoincounts)
    print(cd_plain)
    print(cd_sent)
