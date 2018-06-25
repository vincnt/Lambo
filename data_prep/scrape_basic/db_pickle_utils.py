# Scraping specific Postgres db utilities that interact with pickle file

from utils import timetools as timesort, postgres as redditdb, coinlist as cointools
import pickle
from data_prep.scrape_basic.redditcomment import RedditComment
coinlistrankfilter = 500
coinlistsource = 0  # 0 for local, 1 for github


def readpickle(picklefile):
    with open(picklefile, "rb") as picklearray:
        result = pickle.load(picklearray)
        print('\nlen of pickle array that is being read in (number of entries): ' + str(len(result)) + '\n')
    return result


def fetch_pastday(table, picklefile):
    temparray = readpickle(picklefile)
    existingarray = []
    lasttime = timesort.currenttime() - (60*60*24)
    for x in temparray:
        if x.createdutc < lasttime:
            existingarray.append(x)
    result = redditdb.returnwholetablefromtime(table, lasttime)
    print(str(len(result)) + ' new results retrieved since ' + str(lasttime) + ' -- ' + str(timesort.epoch_to_utc(lasttime)))
    return result, existingarray


def fetch_past3hours(table, picklefile):
    temparray = readpickle(picklefile)
    existingarray = []
    lasttime = timesort.currenttime() - (60*60*3)
    for x in temparray:
        if x.createdutc < lasttime:
            existingarray.append(x)
    result = redditdb.returnwholetablefromtime(table, lasttime)
    print(str(len(result)) + ' new results retrieved since ' + str(lasttime) + ' -- ' + str(timesort.epoch_to_utc(lasttime)))
    return result, existingarray


def fetch_newentries(table, picklefile):
    existingarray = readpickle(picklefile)
    lasttime = 0
    for x in existingarray:
        if x.createdutc > lasttime:
            lasttime = x.createdutc
    results = redditdb.returnwholetablefromtime(table, lasttime)
    print(str(len(results)) + ' new results retrieved since ' + str(lasttime) + ' -- ' + str(timesort.epoch_to_utc(lasttime)))
    return results, existingarray


def fetch_all(table):
    results = redditdb.returnwholetable(table)
    existingarray = []
    return results, existingarray


if __name__ == "__main__":
    fetch_past3hours('reddit_replies','commentarray')
