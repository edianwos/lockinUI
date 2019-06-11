from collections import namedtuple

Point = namedtuple("Point", ['frequency', 'TC', 'ST'])


def linear_scan(start, end, num=11, step=0, TC=0, ST=0, average=1):
    span = end - start
    if step == 0:
        step = span / (num-1)
    if TC == 0:
        TC = 1 / abs(step)
    if ST == 0:
        ST = TC * 5
    freq = start
    for i in range(num):
        for j in range(average):
            yield Point(freq, TC, ST)
        freq += step