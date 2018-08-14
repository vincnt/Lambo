from google.cloud import bigquery
import os
import pprint
from google.oauth2 import service_account
from pandas.io import gbq

local_google_credentials = '/home/vincent/Lambo-89cff3bde0ba.json'

try:
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = local_google_credentials
    client = bigquery.Client()
except:
    client = bigquery.Client()


def list_datasets():
    datasets = list(client.list_datasets())
    project = client.project

    if datasets:
        print('Datasets in project {}:'.format(project))
        for dataset in datasets:  # API request(s)
            print('\t{}'.format(dataset.dataset_id))
    else:
        print('{} project does not contain any datasets.'.format(project))


def list_tables(dataset):
    dataset_ref = client.dataset(dataset)
    tables = list(client.list_tables(dataset_ref))
    print('Tables in dataset {}:'.format(dataset))
    for table in tables:
        print('\t{}'.format(table.table_id))


def get_table_meta(dataset, table):
    dataset_id = dataset
    table_id = table
    dataset_ref = client.dataset(dataset_id)
    table_ref = dataset_ref.table(table_id)
    table = client.get_table(table_ref)
    pprint.pprint(table.schema)
    print("Table Description: " + str(table.description))
    print("Number of rows: " + str(table.num_rows))


def tail_rows(dataset_id, table_id):
    dataset_ref = client.dataset(dataset_id)
    table_ref = dataset_ref.table(table_id)
    table = client.get_table(table_ref)
    rows = client.list_rows(table, max_results=10)
    return rows


def prettyprintrows(rows):
    format_string = '{!s:<16} ' * len(rows.schema)
    field_names = [field.name for field in rows.schema]
    print(format_string.format(*field_names))  # prints column headers
    for row in rows:
        print(format_string.format(*row))


def insertrows(rows_to_insert,dataset_id,table_id):
    '''
    rows_to_insert = [
        (u'Phred Phlyntstone', 32),
        (u'Wylma Phlyntstone', 29),
    ]
    '''
    dataset_ref = client.dataset(dataset_id)
    table_ref = dataset_ref.table(table_id)
    table = client.get_table(table_ref)
    errors = client.insert_rows(table, rows_to_insert)
    assert errors == []


# SELECT * FROM [lambo-192519:Market_Fetch.raw_prices] WHERE CMC_ID = "revain" ORDER BY Timestamp DESC LIMIT 100
def bqqueryquery(cmc_id):
    query = """
        SELECT CMC_ID, CC_USD_PRICE, Timestamp
        FROM `lambo-192519.Market_Fetch.raw_prices`
        WHERE CMC_ID = @cmcid
        ORDER BY Timestamp DESC
        LIMIT 10;
    """
    query_params = [
        bigquery.ScalarQueryParameter('cmcid', 'STRING', cmc_id),
    ]
    job_config = bigquery.QueryJobConfig()
    job_config.query_parameters = query_params
    query_job = client.query(
        query, job_config=job_config)  # API request - starts the query
    results = query_job.result()  # Waits for job to complete.
    print(type(results))

    # Print the results
    for row in results:
        print(row)
        print(type(row))
        print('{}: {} \t {}'.format(row.CMC_ID, row.CC_USD_PRICE, row.Timestamp))

    assert query_job.state == 'DONE'

def bqtopd():
    query = """
            SELECT CMC_ID, CC_USD_PRICE, Timestamp
            FROM Market_Fetch.raw_prices
            WHERE CMC_ID = 'revain'
            ORDER BY Timestamp DESC
            LIMIT 10;
        """
    data_frame = gbq.read_gbq(query, "lambo-192519")
    print(data_frame.head())


def bqmain():
    #list_datasets()
    #list_tables("Market_Fetch")
    #get_table_meta("Market_Fetch", "raw_prices")
    #rowz = tail_rows("Market_Fetch", "raw_prices")
    #prettyprintrows(rowz)
    #bqqueryquery("revain")
    bqtopd()


bqmain()