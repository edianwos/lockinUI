import aiohttp
from aiohttp import web
from driver import *

async def hello(request):
    return web.Response(text="Server is alive!")

async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    async for msg in ws:
        if msg.type == aiohttp.WSMsgType.TEXT:
            if msg.data == 'close':
                await ws.close()
            else:
                resp = msg_parse(msg)
                await ws.send_str(resp)
        elif msg.type == aiohttp.WSMsgType.ERROR:
            print('ws connection closed with exception %s' %
                  ws.exception())

    print('websocket connection closed')

    return ws


def msg_parse(msg):
    order = msg.json()
    if order['action'] == 'measure':
        return str(fake_measure())
    elif order['action'] == 'set':
        return 'success'
    else:
        return 'wrong message!'

app = web.Application()
app.add_routes([web.get('/', hello)])
app.add_routes([web.get('/ws', websocket_handler)])
web.run_app(app)
