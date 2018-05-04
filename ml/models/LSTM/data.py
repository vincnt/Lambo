from MLDataTools import bq2df

import os
projectid = "lambo-192519"

QUERY = (
    "SELECT CMC_ID, CC_USD_PRICE, Timestamp FROM `Market_Fetch.raw_prices`"
    "WHERE (CMC_ID IS NOT NULL AND CC_USD_PRICE IS NOT NULL AND Timestamp IS NOT NULL )"
)
pickle_file = '../../data/raw_prices.pickle'

if not os.path.isfile(pickle_file):
    print("WARNING: dir might not exist")

bq2df(projectid, QUERY, pickle_file)