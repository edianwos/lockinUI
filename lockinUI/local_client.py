import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import visa
import os
from time import time, sleep
from datetime import datetime
import sqlite3
from math import cos, sin, pi

from driver import LockIn
from measurement_routine import linear_scan

## Define main window class from template
path = os.path.dirname(os.path.abspath(__file__))
uiFile = os.path.join(path, 'app.ui')
WindowTemplate, TemplateBaseClass = pg.Qt.loadUiType(uiFile)

class MainWindow(TemplateBaseClass):  
    def __init__(self):
        TemplateBaseClass.__init__(self)
        self.setWindowTitle('pyqtgraph example: Qt Designer')
        
        # Create the main window
        self.ui = WindowTemplate()
        self.ui.setupUi(self)
        
        self.show()

        self.initRS()
    
    def initRS(self):
        self.setup = Setup()
        self.setup.measured.connect(self.get_values)
        # 초기화 및 초기값 미리 칸에 적어놓는 코드 필요

    def set_output(self):
        self.setup.inst.output = float(self.ui.outputLineEdit.text())

    def set_TC(self):
        self.setup.inst.TC = float(self.ui.TCLineEdit.text())

    def sweep(self):
        start = float(self.ui.startLineEdit.text())
        end = float(self.ui.endLineEdit.text())
        number = int(self.ui.numberLineEdit.text())
        average = int(self.ui.averageLineEdit.text())
        autoTC = self.ui.autoTCCheckBox.isChecked()
        logsweep = self.ui.logsweepCheckBox.isChecked()
        print(start, end, number, average, autoTC, logsweep)

        self.setup.que = linear_scan(start, end, num=number, average=average)
        self.setup.start()

    def get_values(self):
        self.ui.ampplotter.clear()
        self.ui.ampplotter.plot(self.setup.freqs, self.setup.amps)
        self.ui.phaseplotter.clear()
        self.ui.phaseplotter.plot(self.setup.freqs, self.setup.phases)
        self.ui.xyplotter.clear()
        self.ui.xyplotter.plot(self.setup.xs, self.setup.ys)

class Setup(QtCore.QThread):
    measured = QtCore.pyqtSignal()
    sequence_over = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super().__init__()
        self.rm = visa.ResourceManager()
        self.inst = LockIn(self.rm.open_resource('GPIB0::1::INSTR'))
        self.que = []
        self.freqs = []
        self.amps = []
        self.phases = []
        self.xs = []
        self.ys = []

    def __del__(self):
        self.inst.close()
        self.rm.close()

    def run(self):
        self.freqs = []
        self.amps = []
        self.phases = []
        self.xs = []
        self.ys = []
        freq_last = self.inst.frequency
        TC_last = self.inst.TC
        for i in self.que:
            t1 = time()
            freq, TC, ST = i
            if freq_last != freq:
                self.inst.frequency = freq
                freq_last = freq
            if TC_last != TC:
                self.inst.TC = TC
                TC_last = TC
            sleep(ST)
            amp, phase = [float(i) for i in self.inst.fetch().split(",")]
            ts = datetime.now()
            self.freqs.append(freq)
            self.amps.append(amp)
            self.phases.append(phase)
            self.xs.append(amp*cos(phase*pi/180))
            self.ys.append(amp*sin(phase*pi/180))
            self.measured.emit()
            t2 = time()
            print(t2-t1)
        self.sequence_over.emit()

if __name__ == "__main__":
    app = QtGui.QApplication([])
    ex = MainWindow()
    app.exec_()
