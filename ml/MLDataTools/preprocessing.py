from typing import List
import numpy as np


def relative_change_rates(seq: List) -> List:
    """:returns normalized sequence that represents relative changes"""
    return [seq[0] / seq[0][0] - 1.0] + [
        curr / seq[i][-1] - 1.0 for i, curr in enumerate(seq[1:])]


def chunks(seq, feature_len: int):
    """ :returns an array split into smalled feature_len arrays"""
    return [np.array(seq[i * feature_len: (i + 1) * feature_len])
            for i in range(len(seq) // feature_len)]
