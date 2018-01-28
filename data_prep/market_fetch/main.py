import requests
import json
import pprint
import datetime
import urllib.request
import operator

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


def cc_price(cc_symbol):
    parameters = {"fsym": cc_symbol, "tsyms": "BTC,USD,GBP"}
    response = requests.get("https://min-api.cryptocompare.com/data/price", params=parameters)
    data = response.json()
    pprint.pprint(data)


def market_finder(coinlist):
    kulist=[]
    for x in coinlist:
        if 'CC_markets' in coinlist[x]:
            if coinlist[x]['CC_markets']['BTC']:
                if 'Kucoin' in coinlist[x]['CC_markets']["BTC"]:
                    kulist.append(coinlist[x]['CMC_ID'])
    print(kulist)
    print(len(kulist))
    return kulist


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


def lambda_test(event,context):

    return event['test']


# Either read_local or read_current from github
coinlist = read_local()

# get latest price for coin from CC (10 sec accuracy)
cc_symbol = coinlist["BTC"]["CC_symbol"]
cc_price(cc_symbol)

# get market cap of coins for an exchange (a few minutes accuracy)
kulist = market_finder(coinlist)
kulistd = cap_finder(kulist)
sortedku = sorted(kulistd.items(), key=operator.itemgetter(1))
for x in sortedku:
    print(x)