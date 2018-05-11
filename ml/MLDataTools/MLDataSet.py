import pandas as pd
import numpy as np
from MLDataTools.MLDataSeries import MLDataSeries


class MLDataSet:
    def __init__(self, dictionary={}):
        """
        MLDataSet is essentially a wrapper for a python dictionary in the format {label_of_series: MLDataSeries}
        labels will be integers
        :param dictionary: the python dictionary
        """

        self._d = dictionary
        self.label_map = {}

    def __getitem__(self, item):
        return self._d[item]

    def add(self, dseries: MLDataSeries):
        index_of_next_item = len(self._d)
        true_value = dseries.df[dseries.symbol_column].unique()[0]
        self.label_map[index_of_next_item] = true_value
        dseries.df[dseries.symbol_column] = [index_of_next_item] * dseries.shape[0]
        self._d[index_of_next_item] = dseries

    def generate_epoch(self):
        indicies = list(range(len(self._d)))
        np.random.shuffle(indicies)
        for index in indicies:
            yield self._d[index]

    def separate(self, split_ratio=0.9):
        indicies = list(range(len(self._d)))
        test_set_index = np.random.choice(indicies)
        train, test = self._d[test_set_index].separate(ratio=split_ratio)
        self._d[test_set_index] = train
        test_true_label = self.label_map[test.df[test.symbol_column].unique()[0]]
        return test, test_true_label

    def __len__(self):
        return len(self._d)
