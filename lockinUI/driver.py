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
        try:
            return self._frequency
        except AttributeError:
            return float(self.inst.query("SOUR:FREQ?"))

    @frequency.setter
    def frequency(self, value):
        resp = self.inst.write("SOUR:FREQ {:7E}".format(value))
        if resp[1] == 0:
            self._frequency = value
        else:
            raise Exception

    @property
    def TC(self):
        try:
            return self._TC
        except AttributeError:
            return float(self.inst.query("FILT:TCON?"))

    @TC.setter
    def TC(self, value):
        resp = self.inst.write("FILT:TCON {:7E}".format(value))
        if resp[1] == 0:
            self._TC = value
        else:
            raise Exception

    @property
    def output(self):
        return float(self.inst.query("SOUR:VOLT?"))
        # return self._output

    @output.setter
    def output(self, value):
        resp = self.inst.write("SOUR:VOLT {}".format(value))
        if resp[1] == 0:
            self._output = value
        else:
            raise Exception

    def fetch(self):
        return self.inst.query("FETC?").strip()

    def close(self):
        self.inst.close()


def fake_measure():
    """return fake measured value in order of amplitude, phase, x, y"""
    return "{},{}".format(random(), random())


list_of_commands = """inst.write("INP:COU AC") # or DC
inst.write("INPUT:FILTER:NOTCH1 ON") # or OF, 1, 2
inst.write("INPUT:FILTER:NOTCH2 ON") # or OF, 1, 2
inst.write("INPUT:IMPedance 1E6") # or 50
inst.write("INPut:LOW FLOat") # or GROund
inst.write("ROUTe:TERMinals  A") # {A|AB|C|I|HF}
inst.write("FILTer:SLOPe 24") #{6|12|18|24}

inst.write("FILTer:TCONstant 1") #<time constant in sec> 
inst.query("FETCH?")
inst.write("SOUR:FREQ {:7E}".format(freq)) #1.234567E+05 
inst.write("SOURce:VOLTage <amplitude> )
{numeric, range 0.00000 to 1.000, setting resolution 4 digits
(at output voltage range full scale), unit Vrms} Suffix M (10-3),
 unit  V, MAX, and  MIN can be used.  Example: 100M (= 0.1)"""


if __name__ == "__main__":
    rm = visa.ResourceManager()
    inst = LockIn(rm.open_resource('GPIB0::1::INSTR'))

    inst.frequency = 2000
    inst.inst.query("FREQ?")
    inst.inst.write("FREQ 3000")
