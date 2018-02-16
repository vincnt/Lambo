from data_prep.scrape_basic import db as redditdb
import pprint
import time


postarray_time_position = 10  # array index of the epoch time in a post


def getlasttime(records_array):
    epoch = (records_array[0][postarray_time_position])
    print(epoch_to_utc(epoch))
    return epoch


def epoch_to_utc(x):
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(x))


def time_loop_creator(records, currentlast):
    current = currentlast
    timestep = current - 3600
    newarray = []
    while current>0:
        for x in records:
            if timestep < records[x][postarray_time_position] <= current:
                newarray.append(records[x])
            else:
                current = timestep
                timestep = currentlast - 3600
    return


def time_looper(start, end):
    return


records = redditdb.get_posts()
currentlast = getlasttime(records)
