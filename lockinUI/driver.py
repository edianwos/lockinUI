from typing import Tuple, Sequence
from random import random
from collections import namedtuple

Point = namedtuple("Point", ['frequency', 'TC', 'ST'])
Datum = namedtuple("Datum", ['amplitude', 'phase', 'TC', 'ST', 'timestamp'])


def set_frequency(freq):
    pass
    return


def set_TC(TC):
    pass
    return


def linear_scan(start, end, num=11, step=0, TC=0, ST=0, average=1):
    span = end - start
    if TC == 0:
        TC = 1 / step
    if ST == 0:
        ST = TC * 5
    if step == 0:
        step = span / (num-1)
    freq = start
    for i in range(num):
        for j in range(average):
            yield Point(freq, TC, ST)
        freq += step


def fake_measure() -> Tuple[float, float]:
    """return fake measured value in order of amplitude, phase, x, y"""
    return random(), random()