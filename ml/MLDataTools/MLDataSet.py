import pandas as pd
import numpy as np
from typing import List


class MLDataSet:
    # so one x sample is equal to the num steps in an rnn; makes sense

    def __init__(self, dataframe: pd.DataFrame, features: List[str] = None, targets: List[str] = None):
        """
        MLDataSet uses pandas DataFrame wrapped in common ml methods to make ml more convenient
        :param dataframe: pandas DataFrame containing the dataset
        :param features: features in the dataset used for training; column(s) in the DataFrame
        :param targets: targets to be predicted; column(s) in the DataFrame
        """
        self.df = dataframe
        self.shape = self.df.shape

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

        train_set = MLDataSet(self.df[0:end_row], features=self.features,
                              targets=self.targets)
        test_set = MLDataSet(self.df[end_row:], features=self.features,
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

    def generate_epoch(self, batch_size: int, gap: int):
        """
        Used when to iteratively generate batches for one epoch
        :param gap: time series gap
        :param batch_size: size of the batch
        :return: x, y np matrices of floats
        """
        batch_indicies = list(range(self.shape[0] // batch_size))
        np.random.shuffle(batch_indicies)

        for i in batch_indicies:
            batch = MLDataSet(self.df[i * batch_size: (i + 1) * batch_size], features=self.features,
                              targets=self.targets)
            yield batch.time_series_split(gap)

    def time_series_split(self, gap: int):
        """
        take a time gap and produce inputs and targets based on gap
        :return: x, y np matrices of floats
        """
        # select the right columns
        inputs = self.df[self.features]
        targets = self.df[self.targets]

        x = np.array([inputs[i:i + gap].values for i in range(inputs.shape[0] - gap)])
        y = np.array([targets.iloc[gap + i] for i in range(targets.shape[0] - gap)])  # works when 1d

        return x, y
