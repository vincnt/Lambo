# TO DO
# put the timesort.timearray_pastxintervals(3600,100) from pickleanalysis into here
# multiple input options for analysis and grapher (eg. bitcoin/btc/bittybaby
# coinlist keys arent lowercased? should they be

from data_prep.scrape_basic import objectAnalysis, picklewriter, db_pickle_utils, grapher
from utils import timetools as timesort, postgres as redditdb, coinlist as cointools
import time
import pprint


# make this more reusable and also expand to posts
def printcomments(coin):
    commentobjectarray = db_pickle_utils.readpickle('commentarray')
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


def combiner(cd):
    # get names from coinlist
    # for each name search for all possible names
    # create new dict and append, and combine the values of all the different variations of the coin
    coinlist = cointools.read_local_coinlist()
    newdict = {}
    for x in coinlist:
        newdict[x] = {}
        for name in set(coinlist[x]['Names']):  # this doesnt have to be a set once its fixed in coinlist.py
            if name in cd:
                if newdict[x] == {}:
                    newdict[x] = cd[name]
                else:
                    for y in cd[name]:
                        if y in newdict[x]:
                            newdict[x][y] += cd[name][y]
                        else:
                            newdict[x][y] = cd[name][y]
    return newdict


def tests():
    cd_plain, cd_ups, cd_sent, cd_upsplussent, cd_upstimessent = objectAnalysis.return_coindicts()  # count the stuffs
    print(cd_plain)
    print(objectAnalysis.totalcountpercoin(cd_plain))  # list the total counts for each coin


def examplerun():
    # MAIN FUNCTIONS ###############
    print('Start time: ' + str(timesort.epoch_to_utc(time.time())) + '\n')
    cointosearch = 'ETH'.lower()  # name in the coin dict array
    cointosearchccname = 'ETH'  # look for the specific CC name for prices
    picklewriter.main('all time', 'reddit_replies')  # fetch from db and update pickle
    cd_plain, cd_ups, cd_sent, cd_upsplussent, cd_upstimessent = objectAnalysis.return_coindicts()  # count the stuffs
    print(objectAnalysis.totalcountpercoin(cd_plain))  # list the total counts for each coin
    # specificcoinovertimeprinter(cd_plain, cointosearch) # detailed print for a specific coin
    # printcomments(cointosearch)  # print all comments for a specific coin
    grapher.grapher(cd_upsplussent, cointosearch, cointosearchccname)

    print('\nEnd time: ' + str(timesort.epoch_to_utc(time.time())))

examplerun()

'''
cd_plain, cd_ups, cd_sent, cd_upsplussent, cd_upstimessent = objectAnalysis.return_coindicts()  # count the stuffs
print(cd_plain)
print('LENGTH 1')
print(len(cd_plain['eth']))
combined_plain = combiner(cd_plain)
combined_ups = combiner(cd_ups)
combined_sent = combiner(cd_sent)
combined_upsplussent = combiner(cd_upsplussent)
combined_upstimessent = combiner(cd_upstimessent)
print('LENGTH 2')
print(len(combined_plain['ETH']))
print("everything combined")
print(combined_plain)
combinedcombined = []
coinlist = cointools.read_local_coinlist()
for x in coinlist:
    for t in combined_plain[x]:
        y = {
            'CMC_TICKER': x,
            'PLAIN': int(combined_plain[x][t]),
            'UPS': int(combined_ups[x][t]),
            'SENT': float(combined_sent[x][t]),
            'SENTPUPS': float(combined_upsplussent[x][t]),
            'SENTXUPS': float(combined_upstimessent[x][t]),
            'TIME': t
        }
        combinedcombined.append(y)


'''
from google.cloud import bigquery
import os


# load rows into Big Query
def bq_loader(rows, datasetname, tablename):
    bigquery_client = bigquery.Client()
    dataset_ref = bigquery_client.dataset(datasetname)
    table_ref = dataset_ref.table(tablename)
    table = bigquery_client.get_table(table_ref)
    errors = bigquery_client.insert_rows(table, rows)
    if not errors:
        print('Loaded succesfully into {}:{}'.format(datasetname, tablename))
    else:
        print('Errors:')
        pprint.pprint(errors)

'''
local_google_credentials = '/home/vincent/Lambo-89cff3bde0ba.json'
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = local_google_credentials

# BigQuery Setup
bq_dataset = "Market_Fetch"
bq_table = "historic_counts"

combined1 = combinedcombined[0:9000]
combined2 = combinedcombined[9001:18000]
combined3 = combinedcombined[18001:]
bq_loader(combined1, bq_dataset, bq_table)
bq_loader(combined2, bq_dataset, bq_table)
bq_loader(combined3, bq_dataset, bq_table)
'''



