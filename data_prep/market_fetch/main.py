import requests
import json
import pprint
import datetime

def cmctest():
    parameters = {"limit": 2}
    response = requests.get("https://api.coinmarketcap.com/v1/ticker/", params=parameters)
    print(response.status_code)
    print("\n")
    data = response.json()
    pprint.pprint(data)
    timez = int((data[1]["last_updated"]))
    print(datetime.datetime.fromtimestamp(timez).strftime('%c'))


def cctest():
    parameters = {"fsym": "ETH", "tsym": "BTC"}
    response = requests.get("https://www.cryptocompare.com/api/data/coinsnapshot/", params=parameters)
    print(str(response.status_code) + "\n")
    data = response.json()
    exchangedata = data["Data"]["Exchanges"]
    for x in exchangedata:
        pprint.pprint(x['MARKET'])


def lambda_test(event,context):
    #cmctest()
    cctest()
    return event['test']

wcctest()