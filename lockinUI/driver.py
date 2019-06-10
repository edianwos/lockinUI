import visa
from typing import Tuple, Sequence
from random import random
from collections import namedtuple

Point = namedtuple("Point", ['frequency', 'TC', 'ST'])
Datum = namedtuple("Datum", ['amplitude', 'phase', 'TC', 'ST', 'timestamp'])


def initialization():
    rm = visa.ResourceManager()
    inst = rm.open_resource(rm.list_resources()[0])
    assert "LI5660" in inst.query("*IDN?")
    inst.write("*RST")
    inst.write("FILTer:SLOPe 6")
    inst.write("ROUTe2 IOSC") # reference is internal oscillator
    return rm, inst


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


"""
inst.write("INP:COU AC") # or DC
inst.write("INPUT:FILTER:NOTCH1 ON") # or OF, 1, 2
inst.write("INPUT:FILTER:NOTCH2 ON") # or OF, 1, 2
inst.write("INPUT:IMPedance 1E6") # or 50
inst.write("INPut:LOW FLOat") # or GROund
inst.write("ROUTe:TERMinals  A") # {A|AB|C|I|HF}
inst.write("FILTer:SLOPe 24") #{6|12|18|24}


inst.write("FILTer:TCONstant 1") #<time constant in sec> 
inst.query("FETCH?")
inst.write("FREQ {:7E}".format(freq)) #1.234567E+05 
"""