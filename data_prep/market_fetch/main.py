import requests
import json
import pprint
import datetime


# location of existing list of coins
coinlist_location = "/home/vincent/Projects/Crypto/Lambo/coinlist.json"


# read coin file
def read_current():
    with open(coinlist_location) as currentlist:
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



def lambda_test(event,context):

    return event['test']


coinlist = read_current()
cc_symbol = coinlist["BTC"]["CC_symbol"]
cc_price(cc_symbol)
