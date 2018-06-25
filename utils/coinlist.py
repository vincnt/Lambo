import requests
import json
import pprint
import urllib.request

# location of existing list of coins
coinlist_location_local = '/home/vincent/Projects/Crypto/Lambo/utils/coinlist.json'
coinlist_location_github = "https://raw.githubusercontent.com/vincnt/Lambo/master/utils/coinlist.json"


###### PUBLIC FUNCTIONS #########

# read coin file
def read_local_coinlist():
    with open(coinlist_location_local) as currentlist:
        data = json.load(currentlist)
        return data


# read coin file from online location (github)
def read_github_coinlist():
    with urllib.request.urlopen(coinlist_location_github) as url:
        data = json.loads(url.read().decode())
        return data


# returns coinlist filtered by rank threshold
def fetch_coinlist_rankfilter(rankthreshold, localorgit):
    newdict = {}
    if localorgit == 1:
        data = read_github_coinlist()
    else:
        data = read_local_coinlist()
    for x in data:
        if int(data[x]['CMC_rank']) < rankthreshold:
            newdict[x] = {}
            for y in data[x]:
                newdict[x][y] = data[x][y]

    return newdict


# uses fetch_coinlist_rankfilter then returns the different names for each coin
def fetch_coinnameslist_rankfilter(rankthreshold, localorgit):
    coinnames = []
    data = fetch_coinlist_rankfilter(rankthreshold, localorgit)
    for coin in data:
        for name in data[coin]['Names']:
            coinnames.append(name)
    return set(coinnames)


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


'''
# get market cap of coins for an exchange (a few minutes accuracy)
marketlist = market_finder(coinlist, "Binance")
marketlist_d = cap_finder(marketlist)
sortedmarket = sorted(marketlist_d.items(), key=operator.itemgetter(1))
for x in sortedmarket:
    print(x)
'''


###### PRIVATE FUNCTIONS #########

# write final result to coin file
def write_new(newdata):
    with open(coinlist_location_local, 'w') as writer:
        json.dump(newdata, writer)


# add array of names for each coin to its dict eg(cardano,ada)
def namescompiler(data):
    currentcoindict = data
    for x in currentcoindict:
        temparray = []
        temparray.append(x.lower())
        temparray.append(currentcoindict[x]['CMC_ID'].lower())
        temparray.append(currentcoindict[x]['Name'].lower())
        if 'CC_ID' in currentcoindict[x]:
            temparray.append(currentcoindict[x]['CC_key'].lower())
        currentcoindict[x]['Names'] = list(set(temparray))
    return currentcoindict


# Retrieve coin data from CoinMarketCap and compiles new coins that are not in existing list
def cmc_coin_fetch(currentdata):
    response = requests.get("https://api.coinmarketcap.com/v1/ticker/?limit=0")
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


# Retrieve coin data from CryptoCompare, match to existing results from CMC and add new fields.
def cc_coin_fetch(currentdata):
    response = requests.get("https://min-api.cryptocompare.com/data/all/coinlist")
    data = response.json()
    cc_notin_cmc = []  # list of coins that are on CC but not CMC. Lower priority but must be fixed eventually.
    for x in data["Data"].keys():
        if x in currentdata:  # if CC ticker matches CMC ticker
            currentdata[x]["Protocol"] = data["Data"][x]['ProofType']
            currentdata[x]["CC_key"] = x
            currentdata[x]["CC_ID"] = data["Data"][x]['Id']
            currentdata[x]["CC_symbol"] = data["Data"][x]['Symbol']
            currentdata[x]["CC_rank"] = data["Data"][x]['SortOrder']
            currentdata[x]["CC_algo"] = data["Data"][x]['Algorithm']
            cc_symbol = data["Data"][x]['Symbol']
            currentdata[x]["CC_markets"] = {"BTC": cc_markets_adder("BTC", cc_symbol),
                                            "ETH": cc_markets_adder("ETH", cc_symbol)}
        elif x not in currentdata:  # Search for name matches if tickers dont match - prob could make this more robust
            name_cat = data["Data"][x]['CoinName'].replace(" ", "").lower()
            name_hyphen = data["Data"][x]['CoinName'].replace(" ", "-").lower()
            for y in currentdata:
                if currentdata[y]['Name'].lower() == name_cat or currentdata[y]['CMC_ID'].lower() == name_hyphen or \
                        currentdata[y]['CMC_ID'].lower() == name_cat:
                    currentdata[y]["Protocol"] = data["Data"][x]['ProofType']
                    currentdata[y]["CC_key"] = x
                    currentdata[y]["CC_symbol"] = data["Data"][x]['Symbol']
                    currentdata[y]["CC_rank"] = data["Data"][x]['SortOrder']
                    currentdata[y]["CC_algo"] = data["Data"][x]['Algorithm']
                    currentdata[y]["CC_ID"] = data["Data"][x]['Id']
                    cc_symbol = data["Data"][x]['Symbol']
                    currentdata[y]["CC_markets"] = {"BTC": cc_markets_adder("BTC", cc_symbol),
                                                    "ETH": cc_markets_adder("ETH", cc_symbol)}
                else:
                    cc_notin_cmc.append(x)
    cc_notin_cmc = list(set(cc_notin_cmc))
    cc_notin_cmc.sort()  # list of coins that are on CC but not CMC. Lower priority but must be fixed eventually.
    return currentdata


# Get the markets that the coins are in from CryptoCompare
def cc_markets_adder(coin, cc_symbol):
    try:
        temp_list = []
        parameters = {"fsym": cc_symbol, "tsym": coin}
        response = requests.get("https://www.cryptocompare.com/api/data/coinsnapshot/", params=parameters)
        data = response.json()
        for x in data["Data"]["Exchanges"]:
            temp_list.append(x['MARKET'])
        return temp_list
    except Exception:
        print(coin + ' exception: ' + cc_symbol)
        pass


# used for debugging - cleans the coinlist file
def clean_slate():
    with open(coinlist_location_local, 'w') as writer:
        json.dump({}, writer)


# main_aws function
def general_update():
    clean_slate()
    currentdata = read_local_coinlist()  # Read coin list
    newdata = cmc_coin_fetch(currentdata)  # Fetch from Coinmarketcap
    print("Markets will take a while to load...")
    newdata = cc_coin_fetch(newdata)  # Update from CryptoCompare
    newdata = namescompiler(newdata)
    combineddata = {**currentdata, **newdata}  # Add new data to existing data
    write_new(combineddata)  # Write combined new data
    print(str(len(newdata)) + " New coins added: ")
    pprint.pprint(newdata)
    print("Done!")
    return combineddata


if __name__ == "__main__":
    print(len(read_local_coinlist()))
    general_update()
