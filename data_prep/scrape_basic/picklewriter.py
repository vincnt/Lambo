from data_prep.scrape_basic import db as scrape_db
from data_prep.scrape_basic.redditcomment import RedditComment
import pickle


def writepickle(objecttowrite):
    with open("commentarray", "wb") as commentarray:
        pickle.dump(objecttowrite, commentarray)
        print('pickle updated')


def apply_nlp(objectarray):
    xcount, oldcount = 0, 0
    print("NLP might take a while. Number of comments processing: " + str(len(objectarray)))
    for x in objectarray:
        x.main()
        xcount += 1
        newcount = (xcount / len(objectarray)) * 100
        if newcount - oldcount >= 1:
            oldcount = newcount
            print(str(round(newcount)) + "% completed.")
    return objectarray


newarray, existingarray = scrape_db.fetch_past3hours('reddit_replies', 'commentarray')
#finalarray = existingarray + apply_nlp([RedditComment(*x) for x in newarray])
finalarray = apply_nlp([RedditComment(*x) for x in newarray])
writepickle(finalarray)



