import logging
import sys

logger = logging.getLogger('pandas_gbq')
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler(stream=sys.stdout))

import pandas_gbq


def bq2df(prpject_id, query, pickle_file=None):
    """Big Query table to Pandas DataFrame"""
    data_frame = pandas_gbq.read_gbq(query, prpject_id, dialect='standard')
    if pickle_file is not None:
        data_frame.to_pickle(pickle_file)
    else:
        return data_frame
