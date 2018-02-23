import psycopg2
from utils import postgres_config as config
from utils import timetools


def connectdb():
    conn = psycopg2.connect(database=config.postgres_config['database'],
                            user=config.postgres_config['user'],
                            password=config.postgres_config['password'],
                            host=config.postgres_config['host'],
                            port=config.postgres_config['port'])
    return conn


def listtables():
    conn = connectdb()
    cursor = conn.cursor()
    cursor.execute("select relname from pg_class where relkind='r' and relname !~ '^(pg_|sql_)';")
    return cursor.fetchall()


def listcolumns(table):
    conn = connectdb()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM " + table + " LIMIT 1")
    colnames = [desc[0] for desc in cursor.description]
    return colnames


def returnwholetable(table):
    conn = connectdb()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM " + table + " ORDER BY createdutc DESC")
    print("Fetching table... \n")
    records = cursor.fetchall()
    return records


def tailtable(table):
    conn = connectdb()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM " + table + " ORDER BY createdutc DESC LIMIT 10")
    records=cursor.fetchall()
    for x in records:
        print(timetools.epoch_to_utc(int(x[7])))
    return records


# put in a return table from specified date function