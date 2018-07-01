import requests
import json
import pprint
import urllib.request
from google.cloud import bigquery
import datetime
import time
import asyncio
import aiohttp
import os
from apscheduler.schedulers.asyncio import AsyncIOScheduler


controls_location = "https://raw.githubusercontent.com/vincnt/Lambo/master/data_prep/market_fetch/fetch_controls.json"


# initialise variables to github controls file
def read_controls():
    with urllib.request.urlopen(controls_location) as url:
        data = json.loads(url.read().decode())
        return data


try:
    controls = read_controls()
    coinlist_location_online = controls["coinlist_link"]
    bq_dataset = controls["bq_dataset"]
    bq_table = controls["bq_table"]
    coinlist_rank_filter = int(controls["coin_rank_limit"])
    fetch_timeout = int(controls["timeout"]) # timeout for fetching coin price
    fetch_retry_count = int(controls["retries"])  # how many times to retry fetching prices in one fetch call
    oneloopruntime = int(controls["repeat_interval"])  # interval to run script in seconds
except Exception as e:
    coinlist_location_online = "https://raw.githubusercontent.com/vincnt/Lambo/master/utils/coinlist.json"
    bq_dataset = "Market_Fetch"
    bq_table = "raw_prices"
    coinlist_rank_filter = 400   # Only return results for those with rank below this (for testing / saving resources)
    fetch_timeout = 20  # timeout for fetching coin price
    fetch_retry_count = 5  # how many times to retry fetching prices in one fetch call
    oneloopruntime = 120  # in seconds

# other parameters
fetch_price_params = "BTC,USD,ETH"  # prices returned from coin fetch
coinlist_location_local = "/home/vincent/Projects/Crypto/Lambo/utils/coinlist.json"
local_google_credentials = '/home/vincent/Lambo-89cff3bde0ba.json'


# read coin file from online location (github)
def read_current():
    with urllib.request.urlopen(coinlist_location_online) as url:
        data = json.loads(url.read().decode())
        return data


# read coin file from local location
def read_local():
    #os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = local_google_credentials
    with open(coinlist_location_local) as currentlist:
        data = json.load(currentlist)
        return data


# return current epoch time
def getepochtime():
    dts = datetime.datetime.utcnow()
    epochtime = round(time.mktime(dts.timetuple()) + dts.microsecond/1e6)
    return epochtime


# main_aws fetch function
def fetch_runner(coinlist):
    loop = asyncio.new_event_loop()
    print("pre filtered coinlist length: " + str(len(coinlist)))
    cc_coinlist = cc_coinlistfilter(coinlist)
    print("filtered coinlist length: " + str(len(cc_coinlist)) + "\n")
    success_list, failed_list = fetch_loop(loop, cc_coinlist)
    for x in range(fetch_retry_count - 1):
        retry_success_list, failed_list = fetch_loop(loop, failed_list)
        for y in retry_success_list:
            success_list.append(y)
    print(str(len(success_list)) + " successful overall. " + str(len(failed_list)) + " failed.")
    print("Failed List: ")
    print(failed_list)
    return success_list


# filter raw conlist into specific parameters eg. only those with CC_symbol, and those with rank <200
def cc_coinlistfilter(original_list):
    finallist = []
    for x in original_list:
        if "CC_symbol" in original_list[x]:
            if int(original_list[x]["CMC_rank"]) < coinlist_rank_filter:
                finallist.append(original_list[x]["CC_symbol"])
    return finallist


# initiates each fetch cycle
def fetch_loop(loop, fetch_list):
    with aiohttp.ClientSession(loop=loop) as session:
        fetch_results = loop.run_until_complete(
            fetch_all(session, fetch_list))
    success_list, failed_list = fetch_success_filter(fetch_results,fetch_list)
    print(str(len(failed_list)) + " failed:")
    #print(failed_list)
    print("\n")
    return success_list, failed_list


# async function to fetch all coins in the list, called by fetch_loop
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
def fetch_success_filter(raw_fetch, fetch_list):
    success_list = []
    nameonly_success_list=[]
    failed_list = []
    print("Total coins searching for: "+str(len(raw_fetch)))
    for x in raw_fetch:
        try:
            if "CC_price" in x:
                if "BTC" in x["CC_price"]:
                    success_list.append(x)
                    nameonly_success_list.append(x["CC_symbol"])
        except Exception:
            pass
    for y in fetch_list:
        if y not in nameonly_success_list:
            failed_list.append(y)
    print(str(len(success_list))+" returned succesfully:")
    #print(success_list)
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
    return finalprices


# load rows into Big Query
def bq_loader(rows, datasetname, tablename):
    bigquery_client = bigquery.Client()
    dataset_ref = bigquery_client.dataset(datasetname)
    table_ref = dataset_ref.table(tablename)
    table = bigquery_client.get_table(table_ref)
    errors = bigquery_client.insert_rows(table, rows)
    if not errors:
        print('Loaded succesfully into {}:{} on {}'.format(datasetname, tablename, datetime.datetime.utcnow()))
    else:
        print('Errors:')
        pprint.pprint(errors)


def main():
    print("\nRunning...\n")
    coinlist = read_current()
    fetchresults = fetch_runner(coinlist)
    bqprices = fetch_to_bq_format(fetchresults, coinlist)
    print("\nfinal price array")
    #print(bqprices)
    bq_loader(bqprices, bq_dataset, bq_table)
    return 'yay'


# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = local_google_credentials
scheduler = AsyncIOScheduler()
scheduler.add_job(main, 'interval', seconds=oneloopruntime)
scheduler.start()
asyncio.get_event_loop().run_forever()


