import mss
import cv2
import numpy
import keyboard
#from time import time, sleep
import time
from pynput import keyboard as pykeyboard
from pynput.keyboard import Key, Controller
sct = mss.mss() 

# config starts here
# default monitor is 1, change this if running CMS21 on a different monitor
monitor_number = 1
# config ends here

print("Running on Monitor ", monitor_number)
print("Press 's' to scrap")
print("Press 'r' to repair")
print("Press 'q' anytime to quit")
is_started = False

input_keyboard = Controller()
monitor = sct.monitors[monitor_number]


with pykeyboard.Events() as events:
    while True:
        event = events.get()
        if str(event.key) == "'q'":
            raise SystemExit
        if str(event.key) == "'s'":
            monitor_bb = {
                "left": int(monitor["left"] + monitor["width"] * 33 / 100),
                "top": int(monitor["top"] + monitor["height"] * 41 / 100),
                "width": int(monitor["width"] * 34 // 100),
                "height": int(monitor["height"] * 20 // 100),
                "mon": int(monitor_number)
            }
            action_base = cv2.imread('Ressources/perfect.png')
            start_base = cv2.imread('Ressources/start_scrap.png')
            break

        if str(event.key) == "'r'":
            monitor_bb = {
                "left": int(monitor["left"] + monitor["width"] * 33 / 100),
                "top": int(monitor["top"] + monitor["height"] * 32 / 100),
                "width": int(monitor["width"] * 34 / 100),
                "height": int(monitor["height"] * 20 / 100),
                "mon": int(monitor_number)
            }
            action_base = cv2.imread('Ressources/repair.png')
            start_base = cv2.imread('Ressources/start_repair.png')
            break

# scale images to match screen size
# templates were captured on 1440p screen
scale = monitor["height"] / 1440;
if scale == 1.0:
    start = start_base
    action = action_base
else:
    dim_start = (
        int(round(start_base.shape[1] * scale)),
        int(round(start_base.shape[0] * scale))
        )
    dim_action = (
        int(round(action_base.shape[1] * scale)),
        int(round(action_base.shape[0] * scale))
        )
    start = cv2.resize(start_base, dim_start)
    action = cv2.resize(action_base, dim_action)

# start script
print("Now running...")
while True:
    if keyboard.is_pressed('q'):
        break
    scr = numpy.array(sct.grab(monitor_bb))
    scr_remove = scr[:,:,:3]
    if is_started == False:
        result = cv2.matchTemplate(scr_remove, start, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)
        if max_val > 0.75:
            keyboard.press_and_release('space')
            is_started = True
    else:
        result = cv2.matchTemplate(scr_remove, action, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)
        if max_val > 0.92:
            input_keyboard.press(Key.space)
            input_keyboard.release(Key.space)
            is_started = False
