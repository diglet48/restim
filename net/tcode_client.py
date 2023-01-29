import asyncio
import time
import websockets
import numpy as np

from net.tcode import TCodeCommand


class TCodeWebsocketClient:
    def __init__(self, url):
        self.url = url

    async def start(self, update_frequency):
        async for websocket in websockets.connect(self.url):
            try:
                while 1:
                    await self.send_state(websocket)
                    await asyncio.sleep(1.0 / update_frequency)
            except websockets.ConnectionClosed as e:
                print(e)
                continue

    # override me
    def get_state(self):
        x = np.cos(time.time() * 3)
        y = np.sin(time.time() * 2.4)
        v = 1.0
        return (x, y, v)

    # or override me
    async def send_state(self, websocket):
        x, y, v = self.get_state()
        state = "{}\n{}\n{}\n".format(
            TCodeCommand("L0", (x + 1.0) * 0.5),
            TCodeCommand("L1", (y + 1.0) * 0.5),
            TCodeCommand("L2", v))
        await websocket.send(state)


if __name__ == '__main__':
    ws_server = TCodeWebsocketClient("ws://localhost:12346")
    asyncio.run(ws_server.start(40))

