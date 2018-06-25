# functions for a reddit comment

from utils import timetools as timesort, postgres as redditdb, coinlist as cointools
import nltk
import string
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk import tokenize

coinnames = cointools.fetch_coinnameslist_rankfilter(200, 0)
stop_words = set(nltk.corpus.stopwords.words('english'))
other_stop_words = ['doge', 'part', 'rise', 'key', 'pay', 'etc', 'bot', 'moon', 'link', 'game', 'trust', 'data', 'fun', 'block', 'key', 'karma', 'via', 'decent', 'sub', 'get', 'time', 'change', 'life', 'ok']


class RedditComment:
    def __init__(self, id, author, h, text, ups, subreddit, createdutc, parent_id):
        self.id = id
        self.author = author
        self.hash = None
        self.text = text
        self.ups = ups
        self.subreddit = subreddit
        self.createdutc = createdutc
        self.parent_id = parent_id
        self.tokenisedtext = ''
        self.coinsmentioned = []
        self.sentiment = 0

    def tokenisetext(self):
        self.tokenisedtext = nltk.word_tokenize(self.text.translate(dict.fromkeys(string.punctuation)))
        self.coinsmentioned = [word.lower() for word in self.tokenisedtext if word.lower() in coinnames and word not in stop_words and word not in other_stop_words]

    def calculatesent(self):
        sid = SentimentIntensityAnalyzer()
        sentText = tokenize.sent_tokenize(self.text)
        count = 0
        sent = 0
        for sentence in sentText:
            count += 1
            ss = sid.polarity_scores(sentence)
            sent += ss['compound']
        if count != 0:
            sent = float(sent / count)
        self.sentiment = sent

    def execute(self):
        self.tokenisetext()
        self.calculatesent()

    def printer(self):
        print(self.coinsmentioned)
        print(self.text)
        print(self.tokenisedtext)
        print('ups: ' + str(self.ups))
        print('sent: ' + str(self.sentiment))
        print('subreddit: ' + str(self.subreddit))
        print('createdepoch: ' + str(self.createdutc))
        print('createdutc: ' + str(timesort.epoch_to_utc(self.createdutc)))
        print('\n')


if __name__ == "__main__":
    testcomment = RedditComment(1, 'bob', 123, 'cant believe nano coin is still around! why do people even believe in it. I hate it. ', 2, 'altcoin', 1520516713, 123)
    testcomment.execute()
    print(testcomment.sentiment)
    testcomment.printer()