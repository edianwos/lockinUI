import visa
from random import random

class LockIn:
    def __init__(self, inst, **kwargs):
        self.inst = inst

    def initialize(self):
        self.inst.write("*RST")
        self.inst.write("FILTer:SLOPe 6")
        self.inst.write("ROUTe2 IOSC")  # reference is internal oscillator
        self._frequency = float(self.inst.query("FREQ?"))
        self._TC = float(self.inst.query("FILT:TCON?"))
        self._output = float(self.inst.query("SOUR:VOLT ?"))

    @property
    def frequency(self):
        return self._frequency

    @frequency.setter
    def frequency(self, value):
        resp = self.inst.write("FREQ {:7E}".format(value))
        if resp[1] == 0:
            self._frequency = value
        else:
            self._frequency = float(self.inst.query("FREQ?"))

    @property
    def TC(self):
        return self._TC
    
    @TC.setter
    def TC(self, value):
        resp = self.inst.write("FILT:TCON {value:7E}")
        if resp[1] == 0:
            self._TC = value
        else:
            self._TC = float(self.inst.query("FILT:TCON?"))

    @property
    def output(self):
        return self._output

    @output.setter
    def output(self, value):
        resp = self.inst.write("FILT:TCON {value:7E}")
        if resp[1] == 0:
            self._output = value
        else:
            self._output = float(self.inst.query("SOUR:VOLT ?"))

    def fetch(self):
        return self.inst.query("FETC?").strip()


def fake_measure():
    """return fake measured value in order of amplitude, phase, x, y"""
    return "{},{}".format(random(), random())


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
inst.write("SOURce:VOLTage <amplitude> )
{numeric, range 0.00000 to 1.000, setting resolution 4 digits
(at output voltage range full scale), unit Vrms} Suffix M (10-3),
 unit  V, MAX, and  MIN can be used.  Example: 100M (= 0.1) 
"""
