# main function that intiates the process to fetch items from PostGres, apply calculations and save to pickle

from data_prep.scrape_basic import db_pickle_utils as scrape_db
from data_prep.scrape_basic.redditcomment import RedditComment
import pickle
from utils import timetools as timesort, postgres as redditdb, coinlist as cointools



def writepickle(objecttowrite):
    with open("commentarray", "wb") as commentarray:
        pickle.dump(objecttowrite, commentarray)
        print('pickle updated')


# iterate through objectarray and call the reddicomment class functions on itself
def apply_nlp(objectarray):
    xcount, oldcount = 0, 0
    print("NLP might take a while. Number of comments processing: " + str(len(objectarray)))
    for x in objectarray:
        x.execute()
        xcount += 1
        newcount = (xcount / len(objectarray)) * 100
        if newcount - oldcount >= 1:
            oldcount = newcount
            print(str(round(newcount)) + "% completed.")
    return objectarray


# gotta make the pickle file name, which is currently 'comment array' also OOP
# retrieves the object array based on input time then applies stuff and then writes to pickle
def main(timevar, table):
    if timevar == '3 hours' and table == 'reddit_replies':
        newarray, existingarray = scrape_db.fetch_past3hours('reddit_replies', 'commentarray')
        finalarray = existingarray + apply_nlp([RedditComment(*x) for x in newarray])
        writepickle(finalarray)
    if timevar == '1 day' and table == 'reddit_replies':
        newarray, existingarray = scrape_db.fetch_pastday('reddit_replies', 'commentarray')
        finalarray = existingarray + apply_nlp([RedditComment(*x) for x in newarray])
        writepickle(finalarray)
    if timevar == 'new entries' and table == 'reddit_replies':
        newarray, existingarray = scrape_db.fetch_newentries('reddit_replies', 'commentarray')
        finalarray = existingarray + apply_nlp([RedditComment(*x) for x in newarray])
        writepickle(finalarray)
    if timevar == 'all time' and table == 'reddit_replies':
        newarray, existingarray = scrape_db.fetch_all('reddit_replies')
        finalarray = existingarray + apply_nlp([RedditComment(*x) for x in newarray])
        writepickle(finalarray)


if __name__ == '__main__':
    lasttime = timesort.currenttime() - (60 * 60 * 3)
    result = redditdb.returnwholetablefromtime('reddit_replies', lasttime)
    finalarray = apply_nlp([RedditComment(*x) for x in result])
    writepickle(finalarray)