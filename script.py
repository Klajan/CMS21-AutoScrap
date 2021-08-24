import mss
import cv2
import numpy

#from time import time, sleep
#import time
from multiprocessing import Pipe, Process, Event
from pynput.keyboard import Key, Controller, Events as KeyEvents
#sct = mss.mss() 

# config starts here
# default monitor is 1, change this if running CMS21 on a different monitor
monitor_number = 1
# config ends here

def grab(pipe, monitor, event_stop=None):
    with mss.mss() as sct:
        while not event_stop.is_set():
            pipe.send(numpy.array(sct.grab(monitor))[:,:,:3])
        print("Exiting grab worker...")

def match(pipe, start, action, event_stop=None):
    is_started = False
    active_keyboard = Controller()
    try:
        while True:
            scr = pipe.recv()
            if is_started == False:
                result = cv2.matchTemplate(scr, start, cv2.TM_CCOEFF_NORMED)
                _, max_val, _, max_loc = cv2.minMaxLoc(result)
                if max_val > 0.75:
                    active_keyboard.press(Key.space)
                    active_keyboard.release(Key.space)
                    is_started = True
            else:
                result = cv2.matchTemplate(scr, action, cv2.TM_CCOEFF_NORMED)
                _, max_val, _, max_loc = cv2.minMaxLoc(result)
                if max_val > 0.92:
                    active_keyboard.press(Key.space)
                    active_keyboard.release(Key.space)
                    is_started = False
    except:
        print("Exiting match worker...")

if __name__ == "__main__":
    monitor = mss.mss().monitors[monitor_number]

    print("Running on Monitor ", monitor_number)
    print("Press 's' to scrap")
    print("Press 'r' to repair")
    print("Press 'q' anytime to quit")

    with KeyEvents() as events:
        while True:
            event_key = events.get()
            if str(event_key.key) == "'q'":
                raise SystemExit
            if str(event_key.key) == "'s'":
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
            if str(event_key.key) == "'r'":
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
        conn1, conn2 = Pipe(False)
        event_stop = Event()
        p_grab = Process(target=grab, args=(conn2, monitor_bb, event_stop))
        p_match = Process(target=match, args=(conn1, start, action, event_stop))
        p_grab.start()
        p_match.start()
        print("Now running...")
        while True:
            event_key = events.get()
            if str(event_key.key) == "'q'":
                break;
            if event_key.key == Key.esc:
                break;
        print("Stopping Workers...")
        event_stop.set()
        conn2.close()
        conn1.close()
        p_grab.join()
        p_match.join()
    print("Done")
