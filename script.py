import mss
import cv2
import numpy
import keyboard
from time import time, sleep
from pynput.keyboard import Key, Controller
sct = mss.mss() 


print("Press 's' to start")
print("Once started to stop the program press 'q'")
is_started = False
keyboard.wait('s')

perfect = cv2.imread('Ressources/perfect.jpg')
start = cv2.imread('Ressources/start.jpg')
monitor = {"top": 446, "left": 646, "width": 650, "height": 200}

input_keyboard = Controller()

i = 0

while True:
    scr = numpy.array(sct.grab(monitor))
    scr_remove = scr[:,:,:3]
    if is_started == False:
        result = cv2.matchTemplate(scr_remove, start, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)
        if max_val > 0.9:
            keyboard.press_and_release('space')
            is_started = True
    else:
        result = cv2.matchTemplate(scr_remove, perfect, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)
        if max_val > 0.9:
            input_keyboard.press(Key.space)
            input_keyboard.release(Key.space)
            is_started = False
    if keyboard.is_pressed('q'):
        break
    i += 1