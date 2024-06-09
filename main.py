import threading
from enum import Enum

import numpy as np
import os
from time import time

from pynput.keyboard import Listener, Key

from bot import Bot
from windowcapture import WindowCapture
import pyautogui
from threading import Thread
import time
from ahk import AHK
import ahk.directives as directives

running = True

ahk = AHK()
ahk.set_coord_mode('Mouse', 'Screen')


def stop():
    global running
    running = False


ahk.add_hotkey('f1', stop)
ahk.start_hotkeys()

# Change the working directory to the folder this script is in.
# Doing this because I'll be putting the files from each video in their own folder on GitHub
os.chdir(os.path.dirname(os.path.abspath(__file__)))


# f1 to exit program
def on_press(key):
    global running
    if key in [Key.f1]:
        running = False
        print("Set running to false")


listener = Listener(on_press=on_press)
listener.daemon = True
listener.start()

bot = Bot()


class GameState(Enum):
    IN_LOBBY = 1
    PLACING_UNITS = 2
    UPGRADING_UNITS = 3
    TELEPORTING_TO_INF = 4


gamestate = GameState.IN_LOBBY

# list of where to click to activate window focus. make configurable
centers = [
    (612, 350),
    (612, 930),
    (1923, 966)
]


def switch_client(idx: int):
    x, y = centers[idx]
    bot.click_at(x, y)


def for_each_rblx(func):
    for x, y in centers:
        bot.click_at(x, y)
        func()
        if not running:
            return


stage = 0

# while True:
#     if not bot.try_click_img('windmill_village_button.jpg', 0.8):
#         print("failed to find img")
#     time.sleep(1)

while running:
    match gamestate:
        case GameState.IN_LOBBY:
            if stage == 0:
                for_each_rblx(bot.get_to_playarea)
                stage = 1

            if stage == 1:
                # first client selects world rest join it
                for i, (x, y) in enumerate(centers):
                    bot.click_at(x, y)
                    bot.enter_portal()
                    if i == 0:
                        # select world and shit
                        if not bot.try_click_img('windmill_village_button.jpg', 0.8, 2):
                            print("could not find windmill village button")
                            continue
                        if not bot.try_click_img('inf_mode_button.jpg', 0.8, 2):
                            print("could not find inf mode button")
                            continue
                        if not bot.try_click_img('confirm_inf.jpg', 0.8, 2):
                            print("could not find 'confirm' button")
                            continue

                # start inf after all clients made it in
                switch_client(0)
                if not bot.try_click_img('start_inf.jpg', 0.8, 2):
                    print("could not find 'start' button")
                    continue
                gamestate = GameState.TELEPORTING_TO_INF
                continue

        case GameState.TELEPORTING_TO_INF:
            # look for sign that inf has started
            if bot.img_exists_on_screen('skip_wave.jpg', confidence=0.85):
                print("inf has started chat")
                gamestate = GameState.PLACING_UNITS

        case GameState.PLACING_UNITS:
            ahk.mouse_move(500, 500)
            time.sleep(2)
            # try placing units on all clients
            ...

        case GameState.UPGRADING_UNITS:
            # try placing units on all clients
            # this runs until the big red return button is spotted
            ...
