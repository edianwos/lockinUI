from collections import namedtuple
from math import log10, pi

Point = namedtuple("Point", ['frequency', 'TC', 'ST'])
twopi = pi*2

# TC 계산을 합리적으로 하는 방법 강구해야 함
def linear_scan(start, end, num=11, step=0, TCauto=True, STmult=5, average=1):
    span = end - start
    if step == 0:
        step = span / (num-1)
    if TCauto == True:
        TC = 1 / (twopi * abs(step))

    ST = TC * STmult
    freq = start
    for i in range(num):
        for j in range(average):
            yield Point(freq, TC, ST)
        freq += step


def log_scan(start, end, num=11, step=0, TCauto=True, STmult=5, average=1):
    assert step == 0
    assert TCauto == True

    log_start = log10(start)
    log_end = log10(end)
    log_span = log_end - log_start
    log_step = log_span / (num-1)
    log_freq = log_start
    freq_last = 10 ** (log_start-log_step)
    print(freq_last, log_freq, log_step)
    for i in range(num):
        for j in range(average):
            freq = 10**log_freq
            TC = 1 / abs(twopi*(freq-freq_last))
            ST = TC * STmult
            freq_last = freq
            log_freq += log_step
            yield Point(freq, TC, ST)