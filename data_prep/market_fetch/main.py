import requests
import json
import pprint
import datetime
import urllib.request
import operator
from google.cloud import bigquery
import datetime
import time
import asyncio
import aiohttp

# location of existing list of coins
coinlist_location = "https://raw.githubusercontent.com/vincnt/Lambo/master/coinlist.json"


# read coin file
def read_current():
    with urllib.request.urlopen(coinlist_location) as url:
        data = json.loads(url.read().decode())
        return data


def read_local():
    with open("/home/vincent/Projects/Crypto/Lambo/coinlist.json") as currentlist:
        data = json.load(currentlist)
        return data


def cmctest(coin):
    response = requests.get("https://api.coinmarketcap.com/v1/ticker/"+coin)
    print(response.status_code)
    print("\n")
    data = response.json()
    pprint.pprint(data)
    timez = int(data[0]["last_updated"])
    print(datetime.datetime.fromtimestamp(timez).strftime('%c'))


def market_finder(coinlist,market):
    marketlist=[]
    for x in coinlist:
        if 'CC_markets' in coinlist[x]:
            if coinlist[x]['CC_markets']['BTC']:
                if market in coinlist[x]['CC_markets']["BTC"]:
                    marketlist.append(coinlist[x]['CMC_ID'])
    print(marketlist)
    print(len(marketlist))
    return marketlist


def cap_finder(coinlist):
    caplist={}
    response = requests.get("https://api.coinmarketcap.com/v1/ticker/?limit=0")
    data = response.json()
    for x in coinlist:
        for y in data:
            if y['id'] == x:
                if y['market_cap_usd']:
                    caplist[x] = float(y['market_cap_usd'])/1000000
    return caplist


def bqtest(rows):
    #import os
    #os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = '/home/vincent/Lambo-89cff3bde0ba.json'
    bigquery_client = bigquery.Client()
    dataset_ref = bigquery_client.dataset("test_coin")
    table_ref = dataset_ref.table("prices")
    # Get the table from the API so that the schema is available.
    table = bigquery_client.get_table(table_ref)
    errors = bigquery_client.insert_rows(table, rows)
    if not errors:
        print('Loaded succesfully into {}:{}'.format("test_coin", "prices"))
    else:
        print('Errors:')
        pprint.pprint(errors)


def getepochtime():
    dts = datetime.datetime.utcnow()
    epochtime = round(time.mktime(dts.timetuple()) + dts.microsecond/1e6)
    return epochtime


def cc_truecoinlist(truelist):
    finallist = []
    for x in truelist:
        if "CC_symbol" in truelist[x]:
            finallist.append(x)
    return finallist


async def fetch(session, coin):
    params = {"fsym": coin, "tsyms": "BTC,USD,GBP,ETH"}
    url = "https://min-api.cryptocompare.com/data/price"
    with aiohttp.Timeout(30):
        async with session.get(url, params=params) as response:
            prices = await response.json()
            result = {"CC_price":prices, "CMC_id": coin, "Time": getepochtime()}
            return result


async def fetch_all(session, coins, loop):
    results = await asyncio.gather(
        *[fetch(session, coin) for coin in coins],
        return_exceptions=True  # default is false, that would raise
    )
    print(results)
    newzlist=[]
    for x in results:
        try:
            if "CC_price" in x:
                if "BTC" in x["CC_price"]:
                    newzlist.append(x)
        except Exception:
            pass
    print(newzlist)
    print(len(newzlist))
    return newzlist





'''
# Either read_local or read_current from github
coinlist = read_local()

# get latest price for coin from CC (10 sec accuracy)
cc_symbol = coinlist["BTC"]["CC_symbol"]
cc_price(cc_symbol)

# get market cap of coins for an exchange (a few minutes accuracy)
marketlist = market_finder(coinlist, "Binance")
marketlist_d = cap_finder(marketlist)
sortedmarket = sorted(marketlist_d.items(), key=operator.itemgetter(1))
for x in sortedmarket:
    print(x)
    '''


def lambda_test(event,context):
    loop = asyncio.get_event_loop()
    coinlist = read_current()
    cc_coinlist = cc_truecoinlist(coinlist)
    with aiohttp.ClientSession(loop=loop) as session:
        the_results = loop.run_until_complete(
            fetch_all(session, cc_coinlist, loop))
    print(the_results)
    justusdresults = []
    for x in the_results:
        y = {'CC_price': x['CC_price']['USD'], 'CMC_ID': x['CMC_id'], 'Time': x['Time']}
        justusdresults.append(y)
    print(justusdresults)
    print(len(justusdresults))
    bqtest(justusdresults)
    return event['test']




'''
depreciated synchronous
def testbqpriceadder(mylist):
    pricearray = []
    for x in mylist:
        temp_dict = {}
        if "CC_symbol" in coinlist[x]:
            cc_symbol = coinlist[x]["CC_symbol"]
            if 'USD' in cc_price(cc_symbol):
                temp_dict['CC_price'] = float(cc_price(cc_symbol)['USD'])
            else:
                temp_dict['CC_price'] = None
            temp_dict['CMC_ID'] = x
            temp_dict['Time'] = getepochtime()
            pricearray.append(temp_dict)
    return pricearray
'''


'''
depreciated synchronous
def cc_price(cc_symbol):
    parameters = {"fsym": cc_symbol, "tsyms": "BTC,USD,GBP"}
    response = requests.get("https://min-api.cryptocompare.com/data/price", params=parameters)
    data = response.json()
    return data
'''
