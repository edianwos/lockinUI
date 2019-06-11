import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import visa
import sqlite3

import os
from time import time, sleep
from datetime import datetime
from math import cos, sin, pi

from driver import LockIn
from db import DataBase
from measurement_routine import linear_scan


datetime_format = '%Y%m%d%H%M%S'

db_file = "db.db"

data_fields = {'frequency': 'real', 'amplitude': 'real',
               'phase': 'real', 'TC': 'real', 'ST': 'real',
               'timestamp': 'timestamp'}
records_fields = {'name': 'integer NOT NULL'}

# Define main window class from template
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
        self.setup.measured.connect(self.save_values)
        self.db = DataBase(db_file, records_fields, data_fields)
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

        self.freqs = []
        self.amps = []
        self.phases = []
        self.xs = []
        self.ys = []

        self.setup.rec_id = datetime.now().strftime(datetime_format)
        self.db.insert_record((self.setup.rec_id,))

        self.setup.que = linear_scan(start, end, num=number, average=average)
        self.setup.start()

    def save_values(self, data):
        freq, amp, phase, TC, ST, ts = data
        self.freqs.append(freq)
        self.amps.append(amp)
        self.phases.append(phase)
        self.xs.append(amp*cos(phase*pi/180))
        self.ys.append(amp*sin(phase*pi/180))
        self.db.insert_datum((self.setup.rec_id, freq, amp, phase, TC, ST, ts))
        self.ui.ampplotter.clear()
        self.ui.ampplotter.plot(self.freqs, self.amps)
        self.ui.phaseplotter.clear()
        self.ui.phaseplotter.plot(self.freqs, self.phases)
        self.ui.xyplotter.clear()
        self.ui.xyplotter.plot(self.xs, self.ys)


class Setup(QtCore.QThread):
    measured = QtCore.pyqtSignal('PyQt_PyObject')
    sequence_over = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super().__init__()
        self.rm = visa.ResourceManager()
        self.inst = LockIn(self.rm.open_resource('GPIB0::1::INSTR'))
        self.que = []

    def __del__(self):
        self.inst.close()
        self.rm.close()
        self.db.conn.close()

    def run(self):
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
            self.measured.emit((freq, amp, phase, TC, ST, ts))
            t2 = time()
            print(t2-t1)
        self.sequence_over.emit()


if __name__ == "__main__":
    app = QtGui.QApplication([])
    ex = MainWindow()
    app.exec_()
