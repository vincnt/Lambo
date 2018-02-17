from data_prep.scrape_basic import db as redditdb
import pprint
import time


postarray_time_position = 10  # array index of the epoch time in a post
timestep = 300  # 5 minutes


def getlasttime(records_array):
    epoch = (records_array[0][postarray_time_position])
    print((records_array[0][postarray_time_position]))
    print(epoch_to_utc(epoch))
    return epoch


def epoch_to_utc(x):
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(x))


def fetchpasttimestep(records_array):
    newarray = []
    for x in records_array:
        if x[postarray_time_position] > time.time()-timestep:
            newarray.append(x)
    return newarray

records = redditdb.get_posts()
print(fetchpasttimestep(records))


