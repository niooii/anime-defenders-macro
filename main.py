import threading
from enum import Enum

import numpy as np
import os
from time import time

import win32gui
from pynput.keyboard import Listener, Key

from bot import Bot
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
    TELEPORTING_TO_INF = 2
    PLACING_UNITS = 3
    UPGRADING_UNITS = 4
    INF_FAILED = 5
    TELEPORTING_FROM_INF = 6


gamestate = GameState.IN_LOBBY

# a list of each window's (x, y, w, h)
rblx_windows = []


# get properties of all roblox windows
def callback(hwnd, extra):
    rect = win32gui.GetWindowRect(hwnd)
    x = rect[0]
    y = rect[1]
    x = x if x > 0 else 0
    y = y if y > 0 else 0
    w = rect[2] - x
    h = rect[3] - y
    window_title: str = win32gui.GetWindowText(hwnd)
    if window_title == 'Roblox':
        rblx_windows.append((x, y, w, h))
        print("Window: %s" % window_title)
        print("\tLocation: (%d, %d)" % (x, y))
        print("\t    Size: (%d, %d)" % (w, h))


win32gui.EnumWindows(callback, None)


def switch_client(idx: int):
    x, y, w, h = rblx_windows[idx]
    bot.click_at(x + w / 2, y + h / 2)


def for_each_rblx(func):
    for x, y, w, h in rblx_windows:
        bot.click_at(x + w / 2, y + h / 2)
        func(x, y, w, h)
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
                for_each_rblx(lambda x, y, w, h: bot.get_to_playarea())
                stage = 1

            if stage == 1:
                # first client selects world rest join itwdw
                for i, (x, y, w, h) in enumerate(rblx_windows):
                    if not running:
                        break
                    bot.click_at(x + w / 2, y + h / 2)
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
                print("Teleporting to infinite...")
                gamestate = GameState.TELEPORTING_TO_INF
                continue

        case GameState.TELEPORTING_TO_INF:
            # look for sign that inf has started
            if stage == 0:
                if bot.img_exists_on_screen('skip_wave.jpg', confidence=0.85):
                    print("inf has started chat")
                    # wait until the notif goes away i guess
                    time.sleep(5)
                    stage = 1

            # look for it again to confirm wave 2 finished, we need money
            if stage == 1:
                if bot.img_exists_on_screen('skip_wave.jpg', confidence=0.85):
                    print("wave 2 started, waiting 3.5 seconds...")
                    gamestate = GameState.PLACING_UNITS
                    time.sleep(3.5)
                    stage = 0

        case GameState.PLACING_UNITS:
            # second time the skip wave thing pops up is when we got enough cash for a mythic
            print("placing units...")


            def place(x, y, w, h):
                global gamestate
                # just return if failure detected
                if gamestate != GameState.PLACING_UNITS:
                    return
                if bot.img_exists_on_screen('infinite_end_screen.jpg', confidence=0.85):
                    gamestate = GameState.INF_FAILED
                    print("Infinite failed, leaving game")
                    return
                top_left = (x + w * 0.7, y + h * 0.5)
                bot_right = (x + w * 0.95, y + h * 0.95)
                bot.place_units(top_left, bot_right)


            for_each_rblx(place)
            gamestate = GameState.UPGRADING_UNITS
            print("upgrading units...")
            stage = 0

        case GameState.UPGRADING_UNITS:
            # try placing units on all clients
            # this runs until the big red return button is spotted
            for x, y, w, h in rblx_windows:
                if not running:
                    break
                if bot.img_exists_on_screen('infinite_end_screen.jpg', confidence=0.85):
                    gamestate = GameState.INF_FAILED
                    print("Infinite failed, leaving game")
                    break
                bot.click_at(x + w / 2, y + h / 2)

                top_left = (x + w * 0.7, y + h * 0.5)
                bot_right = (x + w * 0.95, y + h * 0.95)
                bot.upgrade_units(top_left, bot_right, x, y, w, h)
            stage += 1
            if stage >= 4:
                stage = 0
                gamestate = GameState.PLACING_UNITS

        case GameState.INF_FAILED:
            # a hacky workaround because image detection just does not want to work for all 4 clients
            found_return = False
            rel_shift_x = -1
            rel_shift_y = -1


            def find_return(x, y, w, h):
                global found_return, rel_shift_x, rel_shift_y
                if found_return:
                    return
                # print(x)
                # print(y)
                # print(w)
                # print(h)
                result = bot.get_img_coords('return_lobby_button.jpg', confidence=0.75, region=(x, y, w, h),
                                            search_time=2)
                if result is not None:
                    found_return = True
                    _x = result[0]
                    _y = result[1]
                    rel_shift_x = _x - x
                    rel_shift_y = _y - y
                    return


            # goes through each roblox window and tries to find return button
            for_each_rblx(find_return)
            if not found_return:
                print("Could not find return button")
                continue


            def click_return(x, y, w, h):
                global rel_shift_x, rel_shift_y
                bot.click_at(x + rel_shift_x, y + rel_shift_y)


            for_each_rblx(click_return)

            gamestate = GameState.TELEPORTING_FROM_INF
            print("Returning to lobby...")

        case GameState.TELEPORTING_FROM_INF:
            # do a check to see if all clients have the shop button on screen
            ready_to_restart = True


            def check_if_ready(x, y, w, h):
                global ready_to_restart
                if not ready_to_restart:
                    return

                if not bot.img_exists_on_screen('shop.jpg', confidence=0.8, region=(x, y, w, h)):
                    ready_to_restart = False


            for_each_rblx(check_if_ready)

            if not ready_to_restart:
                print("Waiting for all clients to be in lobby...")
                continue

            gamestate = GameState.IN_LOBBY
            stage = 0
            print("Return to lobby successful.")
