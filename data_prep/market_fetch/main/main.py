import requests
import json
import pprint
import urllib.request
from google.cloud import bigquery
import datetime
import time
import asyncio
import aiohttp

# locations of existing list of coins
coinlist_location_online = "https://raw.githubusercontent.com/vincnt/Lambo/master/coinlist.json"
coinlist_location_local = "/home/vincent/Projects/Crypto/Lambo/coinlist.json"

# credentials to connect to Google auth - for local runs.
local_google_credentials = '/home/vincent/Lambo-89cff3bde0ba.json'

# BigQuery Setup
bq_dataset = "Market_Fetch"
bq_table = "raw_prices"

# Other parameters
coinlist_rank_filter = 200   # Only return results for those with rank below this (for testing / saving resources)
fetch_timeout = 30  # timeout for fetching coin price
fetch_price_params = "BTC,USD,ETH"  # prices returned from coin fetch
fetch_retry_count = 5  # how many times to retry fetching prices in one fetch call


# read coin file from online location (github)
def read_current():
    with urllib.request.urlopen(coinlist_location_online) as url:
        data = json.loads(url.read().decode())
        return data


# read coin file from local location
def read_local():
    import os
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = local_google_credentials
    with open(coinlist_location_local) as currentlist:
        data = json.load(currentlist)
        return data


# generate list of coins that are in a specific exchange(market)
def market_finder(coinlist, market):
    marketlist = []
    for x in coinlist:
        if 'CC_markets' in coinlist[x]:
            if coinlist[x]['CC_markets']['BTC']:
                if market in coinlist[x]['CC_markets']["BTC"]:
                    marketlist.append(coinlist[x]['CMC_ID'])
    print(marketlist)
    print(len(marketlist))
    return marketlist


# get the market caps for coins in $millions
def cap_finder(coinlist):
    caplist = {}
    response = requests.get("https://api.coinmarketcap.com/v1/ticker/?limit=0")
    data = response.json()
    for x in coinlist:
        for y in data:
            if y['id'] == x:
                if y['market_cap_usd']:
                    caplist[x] = float(y['market_cap_usd'])/1000000
    return caplist


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


# return current epoch time
def getepochtime():
    dts = datetime.datetime.utcnow()
    epochtime = round(time.mktime(dts.timetuple()) + dts.microsecond/1e6)
    return epochtime


# main fetch function
def fetch_runner(coinlist):
    loop = asyncio.get_event_loop()
    print("pre filtered coinlist length: " + str(len(coinlist)))
    cc_coinlist = cc_coinlistfilter(coinlist)
    print("filtered coinlist length: " + str(len(cc_coinlist)) + "\n")
    success_list, failed_list = fetch_loop(loop, cc_coinlist)
    for x in range(fetch_retry_count - 1):
        retry_success_list, failed_list = fetch_loop(loop, failed_list)
        for y in retry_success_list:
            success_list.append(y)
    print(str(len(success_list)) + " successful overall")
    print(success_list)
    finalprices = fetch_to_bq_format(success_list,coinlist)
    bq_loader(finalprices, bq_dataset, bq_table)


# filter raw conlist into specific parameters eg. only those with CC_symbol, and those with rank <200
def cc_coinlistfilter(original_list):
    finallist = []
    for x in original_list:
        if "CC_symbol" in original_list[x]:
            if int(original_list[x]["CMC_rank"]) < coinlist_rank_filter:
                finallist.append(original_list[x]["CC_symbol"])
    return finallist


# one fetch cycle - allows to retry fetches for failed results
def fetch_loop(loop, fetch_list):
    with aiohttp.ClientSession(loop=loop) as session:
        fetch_results = loop.run_until_complete(
            fetch_all(session, fetch_list))
    success_list, failed_list = fetch_success_filter(fetch_results)
    print(str(len(failed_list)) + " failed:")
    print(failed_list)
    print("\n")
    return success_list, failed_list


# async function to fetch all coins in the list
async def fetch_all(session, coins):
    results = await asyncio.gather(
        *[fetch(session, coin) for coin in coins],
        return_exceptions=True  # default is false, that would raise
    )
    return results


# async function to fetch individual coin, called by fetch_all
async def fetch(session, coin):
    params = {"fsym": coin, "tsyms": fetch_price_params}
    url = "https://min-api.cryptocompare.com/data/price"
    with aiohttp.Timeout(fetch_timeout):
        async with session.get(url, params=params) as response:
            prices = await response.json()
            result = {"CC_price": prices, "CC_symbol": coin, "Time": getepochtime()}
            return result


# return list of fetches that returned succesfully (no timeout or rate limit exceeded), and return those that failed
def fetch_success_filter(raw_fetch):
    success_list = []
    failed_list = []
    for x in raw_fetch:
        try:
            if "CC_price" in x:
                if "BTC" in x["CC_price"]:
                    success_list.append(x)
                else:
                    failed_list.append(x["CC_symbol"])
        except Exception:
            pass
    print(str(len(success_list))+" returned succesfully:")
    print(success_list)
    return success_list, failed_list


# prepares the final fetched results for bigquery insertion
def fetch_to_bq_format(success_list, coinlist):
    finalprices = []
    for x in success_list:
        y = {
            'CC_USD_PRICE': x['CC_price']['USD'],
            'CC_BTC_PRICE': x['CC_price']['BTC'],
            'CC_ETH_PRICE': x['CC_price']['ETH'],
            'CC_symbol': x['CC_symbol'],
            'Timestamp': x['Time']
        }
        for z in coinlist:
            if 'CC_symbol' in coinlist[z]:
                if x['CC_symbol'] == coinlist[z]['CC_symbol']:
                    y['CMC_ID'] = coinlist[z]['CMC_ID']
                    y['CMC_ticker'] = z
        finalprices.append(y)
    print("final price array")
    print(finalprices)
    return finalprices


def lambda_test(event, context):
    coinlist = read_current()
    fetch_runner(coinlist)
    return 'yay'  # event['test']


# lambda_test("yay", "woo")



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
