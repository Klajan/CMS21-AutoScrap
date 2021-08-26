import mss
import cv2
import numpy
from multiprocessing import Pipe, Process, Event, freeze_support as mp_freeze_support
from pynput.keyboard import Key, Controller, Events as KeyEvents

import time

# config starts here
# default monitor is 1, change this if running CMS21 on a different monitor
monitor_number = 1
# config ends here

def grab(pipe, monitor, event_stop=None):
    with mss.mss() as sct:
        i=0
        t1 = 0
        while not event_stop.is_set():
            t0 = time.perf_counter()
            pipe.send(numpy.array(sct.grab(monitor))[:,:,:3])
            i += 1
            t1 += time.perf_counter() - t0
            if i == 1000:
                print(t1 / 1000)

        print("Exiting grab worker...")

def match(pipe, start, action, arrow):
    is_started = False
    is_found = False
    match_width = action.shape[1]
    match_height = 0
    match_x = 0
    match_y = 0
    
    # limit to red channel for better matching across backgrounds
    arrow_grey = arrow[:,:,2:3]
    
    active_keyboard = Controller()
    try:
        while True:
            scr = pipe.recv()
            if is_started == False:
                # find bounding box height once
                if match_height == 0:
                    match_height = scr.shape[0]
                    print(match_height)
                result = cv2.matchTemplate(scr, start, cv2.TM_CCOEFF_NORMED)
                _, max_val, _, max_loc = cv2.minMaxLoc(result)
                if max_val > 0.75:
                    active_keyboard.press(Key.space)
                    active_keyboard.release(Key.space)
                    is_started = True
            else:
                if is_found == False:
                    # find all matches for pattern and select leftmost
                    result = cv2.matchTemplate(scr, action, cv2.TM_CCOEFF_NORMED)
                    (y, x) = numpy.where(result > 0.85)
                    if y.size > 0:
                        is_found = True
                        match_x = min(x)
                        match_y = min(y)
                        cv2.imwrite("test.png", scr[0:match_height, match_x:match_x+match_width, :])
                else:
                    # limit search to directly above matched area in red channel and find the arrow
                    scr_crop = scr[0:match_y, match_x:match_x+match_width, 2:3]
                    #scr_crop = scr[0:match_height, match_x:match_x+match_width, :]
                    result = cv2.matchTemplate(scr_crop, arrow_grey, cv2.TM_CCOEFF_NORMED)
                    _, max_val, _, max_loc = cv2.minMaxLoc(result)
                    if max_val > 0.9:
                        active_keyboard.press(Key.space)
                        active_keyboard.release(Key.space)
                        is_started = False
                        is_found = False
    except EOFError:
        print("Exiting match worker...")

if __name__ == "__main__":
    # fix for broken mp if build to exe
    mp_freeze_support()

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
                break
            if str(event_key.key) == "'r'":
                monitor_bb = {
                    "left": int(monitor["left"] + monitor["width"] * 33 / 100),
                    "top": int(monitor["top"] + monitor["height"] * 32 / 100),
                    "width": int(monitor["width"] * 34 / 100),
                    "height": int(monitor["height"] * 20 / 100),
                    "mon": int(monitor_number)
                }
                action_base = cv2.imread('Ressources/good.png')
                break

        start_base = cv2.imread('Ressources/start.png')
        arrow_base = cv2.imread('Ressources/arrow.png')
        scale = monitor["height"] / 1440;
        print("Scale is: ", scale)
        if scale == 1.0:
            start = start_base
            action = action_base
            arrow = arrow_base
        else: 
            dim_start = (
                int(round(start_base.shape[1] * scale)),
                int(round(start_base.shape[0] * scale))
                )
            dim_action = (
                int(round(action_base.shape[1] * scale)),
                int(round(action_base.shape[0] * scale))
                )
            dim_arrow = (
                int(round(arrow_base.shape[1] * scale)),
                int(round(arrow_base.shape[0] * scale))
                )
            start = cv2.resize(start_base, dim_start)
            action = cv2.resize(action_base, dim_action)
            arrow = cv2.resize(arrow_base, dim_arrow)

        # start script
        conn1, conn2 = Pipe(False)
        event_stop = Event()
        p_grab = Process(target=grab, args=(conn2, monitor_bb, event_stop))
        p_match = Process(target=match, args=(conn1, start, action, arrow))
        p_grab.start()
        p_match.start()
        print("Now running...")
        while True:
            event_key = events.get()
            if (event_key.key == Key.esc or
                    event_key.key == Key.enter or
                    str(event_key.key) == "'q'"):
                break
        print("Stopping Workers...")
        event_stop.set()
        conn2.close()
        conn1.close()
        p_grab.join()
        p_match.join()
    print("Done")
