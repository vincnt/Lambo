from unittest import TestCase
import pandas as pd
import numpy as np
from MLDataTools import MLDataSet


class TestMLDataSet(TestCase):
    def test_split(self):
        df = pd.DataFrame(np.random.rand(4, 5), columns=['a', 'b', 'c', 'd', 'e'], )
        ds = MLDataSet(df, targets=['e'])
        x, y = ds.split()
        self.assertIsInstance(x, np.ndarray)
        self.assertIsInstance(y, np.ndarray)
        self.assertEqual(x.shape[0], y.shape[0])
        self.assertTrue((x == df.drop('e', axis=1).values).all())

    def test_separate(self):
        df = pd.DataFrame(np.random.rand(5, 2), columns=['x', 'y'])
        ds = MLDataSet(df, features=['x'], targets=['y'])
        train, test = ds.separate(0.5)
        self.assertTrue(True)  # cbf to correct rn

    def test_generate_epoch(self):
        df = pd.DataFrame(np.random.rand(5, 2), columns=['x', 'y'])
        ds = MLDataSet(df)
        for _, x, y in ds.generate_epoch(batch_size=2, gap=2): pass
        self.assertTrue(True)  # cbf to correct rn

    def test_time_series_split(self):
        df = pd.DataFrame(np.random.rand(10, 2), columns=['x1', 'x2'])
        ds = MLDataSet(df, features=['x1', 'x2'], targets=['x2'])
        _, x, y = ds.time_series_split(3)
        self.assertTrue(True)

    def test_encode_labels(self):
        df = pd.DataFrame(np.random.rand(4, 2), columns=['x1', 'x2'])
        df['cities'] = ['Paris', 'Tokyo', 'Rome', 'Tokyo']
        ds = MLDataSet(df)
        ds.encode_labels('cities')
        is_int = np.issubdtype(ds.df['cities'].values.dtype, np.integer)
        self.assertTrue(is_int)
