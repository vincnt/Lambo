import time


# converts epoch time to utc, type string
def epoch_to_utc(x):
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(x))


# return current time in epoch
def currenttime():
    return time.time()


# creates an array of timestamps by the interval specified.
def timearray_pastxintervals(interval, steps):
    current = int(currenttime()) - int(currenttime()) % interval
    timearray = []
    for x in range(steps):
        timearray.append(current)
        current -= interval
    return timearray


# creates an array of timestamps with the given start and end time and interval
def timearray_range(start, end, interval):
    timearray = []
    return timearray

