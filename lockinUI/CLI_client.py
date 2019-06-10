from datetime import datetime
from time import sleep, time
import pyqtgraph as pg
from db import *
from measure import *
import asyncio
import aiohttp


data_fields = {'amplitude': 'real', 'phase': 'real', 'TC': 'real',
                'ST': 'real', 'timestamp': 'timestamp'}
records_fields = {'name': 'text NOT NULL'}
db_file = "db.db"

datetime_format = '%Y%m%d%H%M%S'


async def sweep(sweep: Sequence):
    async with aiohttp.ClientSession() as session:
        async with session.ws_connect('http://localhost:8080/ws') as ws:
            freq_last = 0
            TC_last = 0
            for i in sweep:
                freq, TC, ST = i
                if freq_last != freq:
                    set_frequency(freq)
                    freq_last = freq
                if TC_last != TC:
                    set_TC(TC)
                    TC_last = TC
                sleep(ST) # await asyncio.sleep(ST) <- 고려해야 함
                await ws.send_json({'action': 'measure'})
                msg = await ws.receive()
                amp, phase = [float(i) for i in msg.data[1:-1].split(", ")]
                print(amp, phase)
                ts = datetime.now()
                with conn:
                    insert_datum(conn, (rec_id, amp, phase, TC, ST, ts))


if __name__ == "__main__":
    conn = init_db(db_file, records_fields, data_fields)
    r = linear_scan(1000, 2000, num=6, TC=0.1)
    rec_id = datetime.now().strftime(datetime_format)
    print(rec_id)
    with conn:
        insert_record(conn, (rec_id, ))
    t1 = time()
    asyncio.run(sweep(r))
    t2 = time()
    print(t2-t1)
    
    conn.close()