# TO DO
# put the timesort.timearray_pastxintervals(3600,100) from pickleanalysis into here

from data_prep.scrape_basic import pickleanalysis, picklewriter, db, grapher
from utils import timetools as timesort, postgres as redditdb, coinlist as cointools
import time


# make this more reusable and also expand to posts
def printcomments(coin):
    commentobjectarray = db.readpickle('commentarray')
    for x in range(len(commentobjectarray)):
        templist = []
        for y in commentobjectarray[x].coinsmentioned:
            templist.append(y)
        if coin in templist:
            commentobjectarray[x].printer()


# have to implement multiple coin name into this
def specificcoinovertimeprinter(coinswithtime, cointosearch):
    print('Printing mentions for '+cointosearch)
    for x in coinswithtime[cointosearch]:
        print(str(x) + '  ' + str(timesort.epoch_to_utc(x))+": " + str(coinswithtime[cointosearch][x]))


# MAIN FUNCTIONS ###############
print('Start time: ' + str(timesort.epoch_to_utc(time.time())) + '\n')

cointosearch = 'NEO'.lower()  # name in the coin dict array
cointosearchccname = 'NEO'  # look for the specific CC name
# picklewriter.main('3 hours', 'reddit_replies')  # fetch from db and update pickle
cd_plain, cd_ups, cd_sent, cd_upsplussent, cd_upstimessent = pickleanalysis.return_coindicts()  # count the stuffs
totalcoincount = pickleanalysis.returntotalcountpercoin() # get total count per coin
# specificcoinovertimeprinter(cd_plain, cointosearch) # detailed print for a specific coin
printcomments(cointosearch)  # print all comments for a specific coin
grapher.grapher(cd_plain,cointosearch, cointosearchccname)

print('\nEnd time: ' + str(timesort.epoch_to_utc(time.time())))

# tests
# print(cd_plain)
# print(totalcoincount)
