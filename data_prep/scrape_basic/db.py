import psycopg2
import sys
import pprint


def get_posts():
    # get a connection, if a connect cannot be made an exception will be raised here
    conn = psycopg2.connect(database='reddit', user='vincnttan', password='Spider123Crypto', host='spider.cx0iyrecje9a.eu-west-2.rds.amazonaws.com', port='5432')

    # conn.cursor will return a cursor object, you can use this cursor to perform queries
    cursor = conn.cursor()
    print("Connected!\n")
    cursor.execute("select relname from pg_class where relkind='r' and relname !~ '^(pg_|sql_)';")
    print(cursor.fetchall())

    cursor.execute("SELECT * FROM reddit_posts ORDER BY createdutc DESC")
    records = cursor.fetchall()
    colnames = [desc[0] for desc in cursor.description]
    print(colnames)
    return records


def get_comments():
    # get a connection, if a connect cannot be made an exception will be raised here
    conn = psycopg2.connect(database='reddit', user='vincnttan', password='Spider123Crypto', host='spider.cx0iyrecje9a.eu-west-2.rds.amazonaws.com', port='5432')

    # conn.cursor will return a cursor object, you can use this cursor to perform queries
    cursor = conn.cursor()
    print("Connected!\n")
    cursor.execute("select relname from pg_class where relkind='r' and relname !~ '^(pg_|sql_)';")
    print(cursor.fetchall())

    cursor.execute("SELECT * FROM reddit_replies ORDER BY createdutc")
    records = cursor.fetchall()
    pprint.pprint(records)
    colnames = [desc[0] for desc in cursor.description]
    print(colnames)