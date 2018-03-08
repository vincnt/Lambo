from data_prep.scrape_basic import dbloader
from data_prep.scrape_basic.redditcomment import RedditComment
import pickle


def writepickle(objecttowrite):
    with open("commentarray", "wb") as commentarray:
        pickle.dump(objecttowrite, commentarray)


def apply_nlp(objectarray, existingarray):
    print("NLP might take a while. Number of comments processing: " + str(len(objectarray)))
    xcount = 0
    oldcountp = 0
    for x in objectarray:
        x.main()
        existingarray.append(x)
        xcount += 1
        newcountp = (xcount / len(objectarray)) * 100
        if newcountp - oldcountp >= 1:
            oldcountp = newcountp
            print(str(round(newcountp)) + "% completed.")
    return existingarray


newarray, existingarray = dbloader.fetch_pastday('reddit_replies','commentarray')
fillednewarray = [RedditComment(*x) for x in newarray]
finalarray = apply_nlp(fillednewarray, existingarray)
writepickle(finalarray)
print('pickle updated')
