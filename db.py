import pymongo
import pprint

uri = "mongodb://golang-spider:tZGjo1OZddxRtczjGQf6GRt8KUoo7dE7DcmZdLdhCIVv0aqDojsIUoXFp7GVFpf2M0EQa0dmMAdlAn58ZJJJwA==@golang-spider.documents.azure.com:10255/?ssl=true&replicaSet=globaldb"
client = pymongo.MongoClient(uri)
print(client.database_names())
db = client['Gateway']
collection = db.collection_names(include_system_collections=False)
for collect in collection:
    print(collect)