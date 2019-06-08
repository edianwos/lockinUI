from datetime import datetime
from time import sleep, time
import pyqtgraph as pg
from db import *
from measure import *


data_fields = {'amplitude': 'real', 'phase': 'real', 'TC': 'real',
                'ST': 'real', 'timestamp': 'timestamp'}
records_fields = {'name': 'text NOT NULL'}
db_file = "db.db"

datetime_format = '%Y%m%d%H%M%S'

if __name__ == "__main__":
    conn = init_db(db_file, records_fields, data_fields)
    r = linear_scan(1000, 2000, num=11, TC=0.1)
    rec_id = datetime.now().strftime(datetime_format)
    print(rec_id)
    with conn:
        insert_record(conn, (rec_id, ))
    t1 = time()
    freq_last = 0
    TC_last = 0
    for i in r:
        freq, TC, ST = i
        if freq_last != freq:
            set_frequency(freq)
            freq_last = freq
        if TC_last != TC:
            set_TC(TC)
            TC_last = TC
        sleep(ST)
        amp, phase = fake_measure()
        ts = datetime.now()
        with conn:
            insert_datum(conn, (rec_id, amp, phase, TC, ST, ts))
        pg.plot()
    t2 = time()
    print(t2-t1)
    
    conn.close()