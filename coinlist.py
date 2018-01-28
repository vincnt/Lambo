import requests
import json
import pprint


coinlist_location = "coinlist.json"


def read_current():
    with open(coinlist_location) as currentlist:
        data = json.load(currentlist)
        return data


def write_new(newdata):
    with open(coinlist_location, 'w') as writer:
        json.dump(newdata, writer)


def cmc_coin_fetch(currentdata):
    response=requests.get("https://api.coinmarketcap.com/v1/ticker/?limit=0")
    data = response.json()
    newlist = {}
    for x in data:
        if x['symbol'] not in currentdata:
            newlist[x['symbol']] = {
                                    "Name": x['name'],
                                    "CMC_rank": x['rank'],
                                    "CMC_ID": x['id'],
                                    "CMC_lastupdated": x['last_updated']
                                    }
    return newlist


def cc_coin_fetch(currentdata):
    response = requests.get("https://min-api.cryptocompare.com/data/all/coinlist")
    data = response.json()
    cc_notin_cmc = []
    for x in data["Data"].keys():
        if x in currentdata:
            currentdata[x]["Protocol"] = data["Data"][x]['ProofType']
            currentdata[x]["CC_key"] = x
            currentdata[x]["CC_ID"] = data["Data"][x]['Id']
            currentdata[x]["CC_ticker"] = data["Data"][x]['Symbol']
            currentdata[x]["CC_rank"] = data["Data"][x]['SortOrder']
            currentdata[x]["CC_algo"] = data["Data"][x]['Algorithm']
        elif x not in currentdata:
            name_cat = data["Data"][x]['CoinName'].replace(" ","").lower()
            name_hyphen = data["Data"][x]['CoinName'].replace(" ","-").lower()
            for y in currentdata:
                if currentdata[y]['Name'].lower()== name_cat or currentdata[y]['CMC_ID'].lower() == name_hyphen or currentdata[y]['CMC_ID'].lower() == name_cat:
                    currentdata[y]["Protocol"]=data["Data"][x]['ProofType']
                    currentdata[y]["CC_key"] = x
                    currentdata[y]["CC_ticker"] = data["Data"][x]['Symbol']
                    currentdata[y]["CC_rank"] = data["Data"][x]['SortOrder']
                    currentdata[y]["CC_algo"] = data["Data"][x]['Algorithm']
                    currentdata[y]["CC_ID"] = data["Data"][x]['Id']
                else:
                    cc_notin_cmc.append(x)
    cc_notin_cmc = list(set(cc_notin_cmc))
    cc_notin_cmc.sort()
    return currentdata


def clean_slate():
    with open("coinlist.json", 'w') as writer:
        json.dump({}, writer)


def general_update():
    #clean_slate()
    currentdata = read_current()
    newdata = cmc_coin_fetch(currentdata)
    newdata = cc_coin_fetch(newdata)
    combineddata = {**currentdata, **newdata}
    write_new(combineddata)
    print(str(len(newdata)) + " New coins added: ")
    pprint.pprint(newdata)


general_update()
