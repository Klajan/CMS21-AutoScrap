import mss
import cv2
import numpy
from multiprocessing import Process, Event, Lock, freeze_support as mp_freeze_support
from multiprocessing.managers import SharedMemoryManager
from pynput.keyboard import Key, Controller, Events as KeyEvents

import time

# config starts here
# default monitor is 1, change this if running CMS21 on a different monitor
monitor_number = 1
# config ends here

def run(monitor_bb, start, action, arrow, event_stop):
    is_started = False
    is_found = False
    monitor = monitor_bb
    match_width = action.shape[1]
    arrow_grey = arrow[:,:,2:3]
    active_keyboard = Controller()
    with mss.mss() as sct:
        while not event_stop.is_set():
            if is_started == True and is_found == True:
                #scr = numpy.array(sct.grab(monitor))[0:match_y, match_x:match_x+match_width, 2:3]
                scr = numpy.array(sct.grab(monitor))[:,:,2:3]
            else:
                scr = numpy.array(sct.grab(monitor))[:,:,:3]
            if is_started == False:
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
                        monitor = {
                            "left": int(monitor_bb["left"] + match_x),
                            "top": monitor_bb["top"],
                            "width": int(match_width),
                            "height": int(match_y),
                            "mon": monitor_bb["mon"]
                            }
                else:
                    cv2.imwrite("test.png", scr)
                    # limit search to directly above matched area in red channel and find the arrow
                    # scr_crop = scr_base[0:match_y, match_x:match_x+match_width, 2:3]
                    result = cv2.matchTemplate(scr, arrow_grey, cv2.TM_CCOEFF_NORMED)
                    _, max_val, _, max_loc = cv2.minMaxLoc(result)
                    if max_val > 0.9:
                        active_keyboard.press(Key.space)
                        active_keyboard.release(Key.space)
                        is_started = False
                        is_found = False
                        monitor = monitor_bb



def grab(shared_mem: tuple, lock, event_stop, monitor):
    with mss.mss() as sct:
        buf = numpy.ndarray(shared_mem[1], shared_mem[2] ,shared_mem[0].buf)
        while not event_stop.is_set():
            lock.acquire()
            buf[:] = numpy.array(sct.grab(monitor))
            lock.release()
            

        print("Exiting grab process...")

def match(shared_mem: tuple, lock, event_stop, start, action, arrow):
    is_started = False
    is_found = False
    match_width = action.shape[1]
    match_height = 0
    match_x = 0
    match_y = 0
    
    # limit to red channel for better matching across backgrounds
    arrow_grey = arrow[:,:,2:3]
    
    active_keyboard = Controller()
    scr_base = numpy.ndarray(shared_mem[1], shared_mem[2] ,shared_mem[0].buf)
    
    while not event_stop.is_set():
        # wait for screenshot to be taken
        #event_sync.wait()
        lock.acquire()
        if is_started == True and is_found == True:
            scr = scr_base[0:match_y, match_x:match_x+match_width, 2:3]
        else:
            scr = scr_base[:,:,:3]
        lock.release()
        if is_started == False:
            # find bounding box height once
            if match_height == 0:
                match_height = scr.shape[0]
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
            else:
                # limit search to directly above matched area in red channel and find the arrow
                # scr_crop = scr_base[0:match_y, match_x:match_x+match_width, 2:3]
                result = cv2.matchTemplate(scr, arrow_grey, cv2.TM_CCOEFF_NORMED)
                _, max_val, _, max_loc = cv2.minMaxLoc(result)
                if max_val > 0.9:
                    active_keyboard.press(Key.space)
                    active_keyboard.release(Key.space)
                    is_started = False
                    is_found = False

    print("Exiting match process...")

if __name__ == "__main__":
    # fix for broken mp if build to exe
    mp_freeze_support()


    monitor = mss.mss().monitors[monitor_number]

    print("Running on Monitor", monitor_number, monitor["width"], "x", monitor["height"] )
    print("Press 's' to scrap")
    print("Press 'r' to repair")
    print("Press 'q' anytime to quit")

    with KeyEvents() as events:
        top = 0
        while True:
            event_key = events.get()
            if str(event_key.key) == "'q'":
                raise SystemExit
            if str(event_key.key) == "'s'":
                top = int(monitor["top"] + monitor["height"] * 41.00 / 100)
                action_base = cv2.imread('Ressources/perfect.png')
                break
            if str(event_key.key) == "'r'":
                top = int(monitor["top"] + monitor["height"] * 32.75 / 100)
                action_base = cv2.imread('Ressources/good.png')
                break

        monitor_bb = {
                    "left": int(monitor["left"] + monitor["width"] * 33.75 / 100),
                    "top": top,
                    "width": int(monitor["width"] * 32.50 / 100),
                    "height": int(monitor["height"] * 18.50 / 100),
                    "mon": int(monitor_number)
                }
        start_base = cv2.imread('Ressources/start.png')
        arrow_base = cv2.imread('Ressources/arrow.png')
        scale = monitor["height"] / 1440;
        #print("Scale is: ", scale)
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
        def getMemSizeAndScale():
            x = numpy.array(mss.mss().grab(monitor_bb))
            return (x.size * x.itemsize, x.shape, x.dtype)

        with SharedMemoryManager() as smm:
            mem_size, shape, dtype = getMemSizeAndScale()
            scr_arr = smm.SharedMemory(mem_size)
            lock = Lock()
            event_stop = Event()
            #p_grab = Process(target=grab, args=((scr_arr, shape, dtype), lock, event_stop, monitor_bb))
            #p_match = Process(target=match, args=((scr_arr, shape, dtype), lock, event_stop, start, action, arrow))
            #p_grab.start()
            #p_match.start()
            p_run = Process(target=run, args=(monitor_bb , start, action, arrow, event_stop))
            p_run.start()
            print("Now running...")
            while True:
                event_key = events.get()
                if (event_key.key == Key.esc or
                        event_key.key == Key.enter or
                        str(event_key.key) == "'q'"):
                    break
            
            event_stop.set()
        print("Stopping Workers...")
        p_run.join()
        #p_grab.join()
        #p_match.join()
    print("Done")
