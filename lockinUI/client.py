import asyncio
import aiohttp
from datetime import datetime
import sqlite3
import pyqtgraph as pg
from pyqtgraph.Qt import QtWidgets, QtCore

from measurement_routine import linear_scan

from time import time, sleep

data_fields = {'frequency': 'real', 'amplitude': 'real', 'phase': 'real',
               'TC': 'real', 'ST': 'real', 'timestamp': 'timestamp'}
records_fields = {'name': 'integer NOT NULL'}
db_file = "db.db"

datetime_format = '%Y%m%d%H%M%S'

records_sql = """
CREATE TABLE IF NOT EXISTS records (
id integer PRIMARY KEY,
{}
);""".format(',\n'.join([i+' '+j for i, j in records_fields.items()]))

data_sql = """
CREATE TABLE IF NOT EXISTS data (
id integer PRIMARY KEY,
records_name integer NOT NULL,
{},
FOREIGN KEY (records_name) REFERENCES records (name)
);""".format(',\n'.join([i+' '+j for i, j in data_fields.items()]))

record_insert_sql = 'INSERT INTO records ({}) VALUES ({})'.format(
    ", ".join(records_fields.keys()), ", ".join(['?']*(len(records_fields))))

datum_insert_sql = 'INSERT INTO data (records_name, {}) VALUES(?, {})'.format(
    ", ".join(data_fields.keys()), ", ".join(['?']*(len(data_fields))))


def init_db(db_file: str):
    """initialize db"""
    try:
        conn = sqlite3.connect(db_file)
        with conn:
            conn.execute(records_sql)
            conn.execute(data_sql)
    except Exception as e:
        print(e)
    return conn


def insert_record(conn, record: tuple):
    conn.execute(record_insert_sql, record)


def insert_datum(conn, datum: tuple):
    conn.execute(datum_insert_sql, datum)


def set_frequency(freq: float):
    return {'action': 'set', "target": "frequency", "value": freq}


def set_TC(TC: float):
    return {'action': 'set', "target": "TC", "value": TC}


class MyApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()
        self.initRS()

    def initUI(self):
        self.xs = []
        self.ys = []
        self.websocket = Websocket()
        self.plotter = pg.PlotWidget(self)
        self.button = QtWidgets.QPushButton("start", self)
        self.vbox = QtWidgets.QVBoxLayout()
        self.vbox.addWidget(self.plotter)
        self.vbox.addWidget(self.button)
        self.setLayout(self.vbox)

        self.button.clicked.connect(self.ws_start)
        self.websocket.measured.connect(self.get_values)

        self.setWindowTitle("Lockin-sweeper")
        self.setGeometry(300, 300, 600, 500)
        self.show()

    def initRS(self):
        self.db_conn = init_db(db_file)

    def ws_start(self):
        self.xs = []
        self.ys = []
        self.websocket.que = linear_scan(32000, 33000, num=100, TC=0.1)
        self.websocket.rec_id = datetime.now().strftime(datetime_format)
        print(self.websocket.rec_id)
        with self.db_conn:
            insert_record(self.db_conn, (self.websocket.rec_id, ))
        self.websocket.start()

    @QtCore.pyqtSlot('PyQt_PyObject')
    def get_values(self, resp):
        freq, amp, phase, TC, ST, ts = resp
        row = (self.websocket.rec_id, freq, amp, phase, TC, ST, ts)
        with self.db_conn:
            insert_datum(self.db_conn, row)
        self.xs.append(freq)
        self.ys.append(amp)
        self.plotter.clear()
        self.plotter.plot(self.xs, self.ys)


class Websocket(QtCore.QThread):
    measured = QtCore.pyqtSignal('PyQt_PyObject')
    sequence_over = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super().__init__()
        self.que = []

    def run(self):
        asyncio.run(self.connect())

    async def connect(self):
        async with aiohttp.ClientSession() as session:
            async with session.ws_connect('http://localhost:8080/ws') as ws:
                freq_last = 0
                TC_last = 0
                for i in self.que:
                    freq, TC, ST = i
                    if freq_last != freq:
                        await ws.send_json(set_frequency(freq))
                        msg = await ws.receive()
                        assert msg.data == 'success'
                        freq_last = freq
                    if TC_last != TC:
                        await ws.send_json(set_TC(freq))
                        msg = await ws.receive()
                        assert msg.data == 'success'
                        TC_last = TC
                    t1 = time()
                    await asyncio.sleep(ST)
                    t2 = time()
                    print(t2-t1)
                    await ws.send_json({'action': 'measure'})
                    msg = await ws.receive()
                    amp, phase = [float(i) for i in msg.data.split(",")]
                    ts = datetime.now()
                    self.measured.emit((freq, amp, phase, TC, ST, ts))
        self.sequence_over.emit()


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    ex = MyApp()
    app.exec_()
