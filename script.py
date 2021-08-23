import mss
import cv2
import numpy
import keyboard
from time import time, sleep
from pynput.keyboard import Key, Controller
sct = mss.mss() 

# config starts here
# default monitor is 1, change this if running CMS21 on a different monitor
monitor_number = 1
# config ends here

print("Running on Monitor ", monitor_number)
print("Press 's' to start")
print("Once started to stop the program press 'q'")
is_started = False
keyboard.wait('s')
monitor = sct.monitors[monitor_number]
perfect_base = cv2.imread('Ressources/perfect.png')
start_base = cv2.imread('Ressources/start.png')

# replace static bbox with dynamic
# based on monitor = {"top": 446, "left": 646, "width": 650, "height": 200}
# 33.65% from the left rounted down to int
# 41.30% from the top rounted down to int
# 33.85% width rounted up to int
# 18.52% height rounted up to int
monitor_bb = {
    "left": monitor["left"] + monitor["width"] * 33 // 100,
    "top": monitor["top"] + monitor["height"] * 41 // 100,
    "width": monitor["width"] * 34 // 100,
    "height": monitor["height"] * 19 // 100,
    "mon": monitor_number
    }

# scale images to match screen size
# templates were captured on 1440p screen
scale = monitor["height"] / 1440;
if scale == 1.0:
    start = start_base
    perfect = perfect_base
else:
    dim_start = (
        int(round(start_base.shape[1] * scale)),
        int(round(start_base.shape[0] * scale))
        )
    dim_perfect = (
        int(round(perfect_base.shape[1] * scale)),
        int(round(perfect_base.shape[0] * scale))
        )
    start = cv2.resize(start_base, dim_start)
    perfect = cv2.resize(perfect_base, dim_perfect)

# start script
print("Now running...")
input_keyboard = Controller()

i = 0
while True:
    scr = numpy.array(sct.grab(monitor_bb))
    scr_remove = scr[:,:,:3]
    if is_started == False:
        result = cv2.matchTemplate(scr_remove, start, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)
        if max_val > 0.75:
            keyboard.press_and_release('space')
            is_started = True
    else:
        result = cv2.matchTemplate(scr_remove, perfect, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)
        if max_val > 0.92:
            input_keyboard.press(Key.space)
            input_keyboard.release(Key.space)
            is_started = False
    if keyboard.is_pressed('q'):
        break
    i += 1