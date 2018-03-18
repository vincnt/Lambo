# functions to graph data
import requests
import matplotlib.dates
import matplotlib.pyplot as plt


def grapher(coinswithtime, cointosearch, cointosearchccname):
    cointime = []
    coincount = []
    for x in coinswithtime[cointosearch]:
        cointime.append(matplotlib.dates.epoch2num(x))
        coincount.append(coinswithtime[cointosearch][x])

    response = requests.get("https://min-api.cryptocompare.com/data/histohour?fsym="+cointosearchccname+"&tsym=BTC&aggregate=1&limit=500")
    data = response.json()
    print('Cryptocompare fetch data')
    print(data['Data'])
    coinprice = []
    for x in cointime:
        for y in data['Data']:
            if x == matplotlib.dates.epoch2num(y['time']):
                coinprice.append(y['open'])
    print('\ncoin count')
    print(coincount)
    print('\ncoinprice before')
    print(coinprice)
    coinprice = [((x-min(coinprice))/(max(coinprice)-min(coinprice))) for x in coinprice]
    coincount = [(x-min(coincount))/(max(coincount)-min(coincount)) for x in coincount]
    print('\ncoinpriceafter')
    print(coinprice)

    fig, ax = plt.subplots()
    # Plot the date using plot_date rather than plot
    ax.plot_date(cointime, coincount, '*-', label='coincount')
    ax.plot_date(cointime, coinprice, '--', label='coinprice')
    # Choose your xtick format string
    date_fmt = '%d-%m %H:%M'
    # Use a DateFormatter to set the data to the correct format.
    date_formatter = matplotlib.dates.DateFormatter(date_fmt)
    ax.xaxis.set_major_formatter(date_formatter)
    # Sets the tick labels diagonal so they fit easier.
    fig.autofmt_xdate()
    ax.xaxis.set_major_locator(matplotlib.dates.MinuteLocator(interval=240))
    fig.suptitle(cointosearch, fontsize=20)
    ax.legend(loc='lower right')
    plt.show()
