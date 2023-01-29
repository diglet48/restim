import numpy as np
import asyncio
import time
import threading

import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, RadioButtons
from matplotlib.animation import FuncAnimation

from stim_math import trig, calibration
from net.tcode import TCodeCommand
from net.tcode_client import TCodeWebsocketClient



def f(x, y, params):
    interp = calibration.SevenPointCalibration((params))
    return interp.get_scale(x, y)


init = [.45, .54, .70, 1.0, .65, .45, .6]  # [0/3pi, 1/3pi, 2/3pi, 3/3pi, 4/3pi, 5/3pi, center]


fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})
ax.set_thetagrids([0, 120, 240])
ax.set_xlim(0, 2*np.pi)
ax.set_ylim(0, 1.05)
plt.subplots_adjust(bottom=0.5)
t = np.arange(0.0, np.pi * 2, 0.001)
delta_f = 0.01
s = f(np.cos(t), np.sin(t), init)
l, = plt.plot(t, s, lw=2)
p, = plt.plot([0.1], [0.5], c='red', marker='o')
ax.margins(x=0)


axcolor = 'lightgoldenrodyellow'

axradio = plt.axes([0.05, 0.55, 0.25, 0.35], facecolor=axcolor)
radio = RadioButtons(axradio, ('cw', 'ccw', '80% height', '50% height', '20% height', '0% height', '\ slope', '| slope',  '/ slope', 'small ccw', 'spiral'))

axtheta = plt.axes([0.125, 0.40, 0.775, 0.03], facecolor=axcolor)
ax0 = plt.axes([0.125, 0.35, 0.775, 0.03], facecolor=axcolor)
ax1 = plt.axes([0.125, 0.30, 0.775, 0.03], facecolor=axcolor)
ax2 = plt.axes([0.125, 0.25, 0.775, 0.03], facecolor=axcolor)
ax3 = plt.axes([0.125, 0.20, 0.775, 0.03], facecolor=axcolor)
ax4 = plt.axes([0.125, 0.15, 0.775, 0.03], facecolor=axcolor)
ax5 = plt.axes([0.125, 0.10, 0.775, 0.03], facecolor=axcolor)
ax6 = plt.axes([0.125, 0.05, 0.775, 0.03], facecolor=axcolor)

stheta = Slider(axtheta, 'speed', 0.1, 10.0, valinit=1.0)
s0 = Slider(ax0, '0/3π', 0.1, 1.0, valinit=init[0], valstep=delta_f)
s1 = Slider(ax1, '1/3π', 0.1, 1.0, valinit=init[1], valstep=delta_f)
s2 = Slider(ax2, '2/3π', 0.1, 1.0, valinit=init[2], valstep=delta_f)
s3 = Slider(ax3, '3/3π', 0.1, 1.0, valinit=init[3], valstep=delta_f)
s4 = Slider(ax4, '4/3π', 0.1, 1.0, valinit=init[4], valstep=delta_f)
s5 = Slider(ax5, '5/3π', 0.1, 1.0, valinit=init[5], valstep=delta_f)
s6 = Slider(ax6, 'center', 0.1, 1.0, valinit=init[6], valstep=delta_f)


class Script:
    def __init__(self):
        self.theta = 0
        self.last_time = time.time()

    def get_pos(self, latency):
        new_time = time.time()
        elapsed = new_time - self.last_time
        self.last_time = new_time

        if radio.value_selected == 'cw':
            angular_velocity = -stheta.val
            self.theta += angular_velocity * elapsed
            theta = self.theta + angular_velocity * latency
            return np.cos(theta), np.sin(theta)
        if radio.value_selected == 'ccw':
            angular_velocity = stheta.val
            self.theta += angular_velocity * elapsed
            theta = self.theta + angular_velocity * latency
            return np.cos(theta), np.sin(theta)
        if radio.value_selected == '80% height':
            angular_velocity = stheta.val
            self.theta += angular_velocity * elapsed
            theta = self.theta + angular_velocity * latency
            return np.cos(theta), np.sin(theta) * 0.8
        if radio.value_selected == '50% height':
            angular_velocity = stheta.val
            self.theta += angular_velocity * elapsed
            theta = self.theta + angular_velocity * latency
            return np.cos(theta), np.sin(theta) * 0.5
        if radio.value_selected == '20% height':
            angular_velocity = stheta.val
            self.theta += angular_velocity * elapsed
            theta = self.theta + angular_velocity * latency
            return np.cos(theta), np.sin(theta) * 0.2
        if radio.value_selected == '0% height':
            angular_velocity = stheta.val
            self.theta += angular_velocity * elapsed
            theta = self.theta + angular_velocity * latency
            return np.cos(theta), np.sin(theta) * 0.0
        if radio.value_selected == '\ slope':
            angular_velocity = stheta.val
            self.theta += angular_velocity * elapsed
            theta = self.theta + angular_velocity * latency
            return np.cos(theta) * .5**.5, -np.cos(theta)*.5**.5
        if radio.value_selected == '| slope':
            angular_velocity = stheta.val
            self.theta += angular_velocity * elapsed
            theta = self.theta + angular_velocity * latency
            return 0, np.cos(theta)
        if radio.value_selected == '/ slope':
            angular_velocity = stheta.val
            self.theta += angular_velocity * elapsed
            theta = self.theta + angular_velocity * latency
            return np.cos(theta) * .5**.5, np.cos(theta) * .5**.5
        if radio.value_selected == 'small ccw':
            angular_velocity = stheta.val
            self.theta += angular_velocity * elapsed
            theta = self.theta + angular_velocity * latency
            return np.cos(theta) * .5, np.sin(theta) * .5
        if radio.value_selected == 'spiral':
            angular_velocity = stheta.val
            self.theta += angular_velocity * elapsed
            theta = self.theta + angular_velocity * latency
            return np.cos(theta / 6) * .5 + np.cos(theta) * 0.5, np.sin(theta / 6) * 0.5 + np.sin(theta) * .5

script = Script()


def update_animation(frame_number):
    x, y = script.get_pos(-.10)
    theta = np.arctan2(y, x)
    norm = trig.norm(x, y)
    p.set_data([theta], [norm])

animation = FuncAnimation(fig, update_animation, interval=100)


def update_data(val):
    x = np.cos(t)
    y = np.sin(t)
    params = [s0.val, s1.val, s2.val, s3.val, s4.val, s5.val, s6.val]
    print('params updated to:', params)
    l.set_ydata(f(x, y, params))
    fig.canvas.draw_idle()


s0.on_changed(update_data)
s1.on_changed(update_data)
s2.on_changed(update_data)
s3.on_changed(update_data)
s4.on_changed(update_data)
s5.on_changed(update_data)
s6.on_changed(update_data)

resetax = plt.axes([0.8, 0.00, 0.1, 0.04])
button = Button(resetax, 'Reset', color=axcolor, hovercolor='0.975')

def reset(event):
    s0.reset()
    s1.reset()
    s2.reset()
    s3.reset()
    s4.reset()
    s5.reset()
    s6.reset()

button.on_clicked(reset)



class CalibratingTCodeWebsocketClient(TCodeWebsocketClient):
    def __init__(self, url):
        super(CalibratingTCodeWebsocketClient, self).__init__(url)

    def get_state(self):
        x, y = script.get_pos(0)
        v = f(x, y, [s0.val, s1.val, s2.val, s3.val, s4.val, s5.val, s6.val])
        return (x, y, v)

    async def send_state(self, websocket):
        x, y, v = self.get_state()
        state = "\n".join([
            TCodeCommand("L0", (x + 1.0) * 0.5).format_cmd(),
            TCodeCommand("L1", (y + 1.0) * 0.5).format_cmd(),
            TCodeCommand("L2", v).format_cmd(),
            TCodeCommand('C0', s0.val).format_cmd(),
            TCodeCommand('C1', s1.val).format_cmd(),
            TCodeCommand('C2', s2.val).format_cmd(),
            TCodeCommand('C3', s3.val).format_cmd(),
            TCodeCommand('C4', s4.val).format_cmd(),
            TCodeCommand('C5', s5.val).format_cmd(),
            TCodeCommand('C6', s6.val).format_cmd(),
        ])
        await websocket.send(state)


client = CalibratingTCodeWebsocketClient("ws://localhost:12346")

loop = asyncio.new_event_loop()
def ff(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()


thread = threading.Thread(target=ff, args=(loop,))
thread.start()
asyncio.run_coroutine_threadsafe(client.start(40), loop)
plt.show()
loop.stop()
