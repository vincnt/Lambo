import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
from typing import List


class MLDataSeries:
    # so one x sample is equal to the num steps in an rnn; makes sense

    def __init__(self, dataframe: pd.DataFrame, symbol_column: str = None,
                 features: List[str] = None,
                 targets: List[str] = None,
                 ):

        """
        MLDataSet uses pandas DataFrame wrapped in common ml methods to make ml more convenient
        :param dataframe: pandas DataFrame containing the dataset
        :param features: features in the dataset used for training; column(s) in the DataFrame
        :param targets: targets to be predicted; column(s) in the DataFrame
        """

        self.df = dataframe
        self.shape = self.df.shape
        self.symbol_column = symbol_column

        if features is None:  # assume all columns are features
            self.features = list(self.df)
        else:
            self.features = features

        if targets is None:  # assume all columns are targets
            self.targets = list(self.df)
        else:
            self.targets = targets

    def separate(self, ratio: float):
        """

        :param ratio: size ratio of train/test
        :return: MLDataSet objects train_set and test_set
        """
        end_row = int(self.shape[0] * ratio)

        train_set = MLDataSeries(self.df[0:end_row],
                                 symbol_column=self.symbol_column,
                                 features=self.features,
                                 targets=self.targets)
        test_set = MLDataSeries(self.df[end_row:],
                                symbol_column=self.symbol_column,
                                features=self.features,
                                targets=self.targets)

        return train_set, test_set,

    def split(self):
        """
        split data set into targets and features
        :param sep_label:
        :return: x, y np matrices of floats
        """
        y = self.df[self.targets].values
        x = self.df.drop(self.targets, axis=1).values
        return x, y

    def generate_epoch(self, batch_size: int, tgap: int):
        """
        Used when to iteratively generate batches for one epoch
        :param gap: time series gap
        :param batch_size: size of the batch
        :return: x, y np matrices of floats
        """
        batch_indicies = list(range((self.shape[0] - tgap) // batch_size))
        np.random.shuffle(batch_indicies)

        for i in batch_indicies:
            batch = MLDataSeries(self.df[i * batch_size: (i + 1) * batch_size + tgap],
                                 features=self.features,
                                 targets=self.targets,
                                 symbol_column=self.symbol_column)
            yield batch.time_series_split(tgap)

    def time_series_split(self, tgap: int):
        """
        take a time gap and produce inputs and targets based on gap
        :return: symbols, x, y np matrices of floats
        """
        # select the right columns
        inputs = self.df[self.features]
        targets = self.df[self.targets]
        x = np.array([inputs[i:i + tgap].values for i in range(inputs.shape[0] - tgap)])
        y = np.array([targets.iloc[tgap + i] for i in range(targets.shape[0] - tgap)])  # works when 1d
        symbols = np.array([self.df[self.symbol_column].iloc[0]] * (inputs.shape[0] - tgap))
        symbols = np.reshape(symbols, (-1, 1))
        return symbols, x, y

    def encode_labels(self, column_name: str = None):
        """
        maps label names onto integers
        :param column_name: name of column in pandas dataframe to be encoded
        :return: void
        """

        if column_name is None:
            if self.symbol_column is None:
                print("No column given, exiting")
                return
            else:
                column_name = self.symbol_column

        values = self.df[column_name].unique()
        enc = LabelEncoder()
        enc.fit(values)
        self.df[column_name] = enc.transform(self.df[column_name])
        self.label_encoder = enc
