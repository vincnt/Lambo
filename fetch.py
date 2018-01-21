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
    parameters = {}
    response = requests.get("https://min-api.cryptocompare.com/data/all/coinlist", params=parameters)
    print(response.status_code)
    print("\n")
    data = response.json()
    print(data.keys())
    pprint.pprint(data["Data"].keys())
    print(len(data["Data"]))
    pprint.pprint(data["Data"]["BTC"])
    #pprint.pprint(data)

def lambda_test(event):
    #cmctest()
    cctest()
    print(event[1])
