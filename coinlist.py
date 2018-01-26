import requests
import json
import pprint
import datetime


def read_current():
    with open("coinlist.json") as currentlist:
        data = json.load(currentlist)
        return data


def write_new(newdata):
    with open("coinlist.json", 'w') as writer:
        json.dump(newdata, writer)


def coin_fetch(currentdata):
    response = requests.get("https://min-api.cryptocompare.com/data/all/coinlist")
    print(response.status_code)
    print("\n")
    data = response.json()
    coin_names = data["Data"].keys()
    newlist = {}
    for x in coin_names:
        if x not in currentdata:
            newlist[x]={
                'Full Name': data["Data"][x]['CoinName'],
                'Ticker': data["Data"][x]['Symbol'],
                'Protocol': data["Data"][x]['ProofType'],
                'Cryptocompare rank': data["Data"][x]['SortOrder']
            }
    return newlist

def clean_slate():
    with open("coinlist.json", 'w') as writer:
        json.dump({}, writer)

def general_update():
    currentdata = read_current()
    newdata = coin_fetch(currentdata)
    combineddata = {**currentdata, **newdata}
    write_new(combineddata)
    pprint.pprint(newdata)

general_update();