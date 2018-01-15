import pymongo
import pprint

uri = "mongodb://golang-spider:tZGjo1OZddxRtczjGQf6GRt8KUoo7dE7DcmZdLdhCIVv0aqDojsIUoXFp7GVFpf2M0EQa0dmMAdlAn58ZJJJwA==@golang-spider.documents.azure.com:10255/?ssl=true&replicaSet=globaldb"
client = pymongo.MongoClient(uri)
print(client.database_names())
db = client['Gateway']
c = db.pages
<<<<<<< HEAD
print(c.count())
=======
for page in c.find():
    pprint.pprint(page)
>>>>>>> e0b27b5a8af32572511157fbe774885356942e99
