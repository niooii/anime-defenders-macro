from threading import Thread

import pyautogui
from ahk import AHK
import time
from enum import Enum
from pynput.keyboard import Key, Listener

ahk = AHK()
ahk.set_coord_mode('Mouse', 'Screen')


def get_points_in_rect(top_left: int, bottom_right: int) -> list[(int, int)]:
    ...


running = True


class Bot:

    @staticmethod
    def click_at(x, y):
        ahk.mouse_move(x=x, y=y, speed=4, blocking=True)
        ahk.click(x=x, y=y, blocking=True)
        # whhy not
        time.sleep(0.05)

    @staticmethod
    def img_exists_on_screen(img_path: str, confidence: float):
        try:
            box = pyautogui.locateOnScreen(img_path, confidence=confidence)
        except pyautogui.ImageNotFoundException as e:
            return False

        return box is not None

    @staticmethod
    def try_click_img(img_path: str, confidence: float, search_time: float):
        try:
            box = pyautogui.locateOnScreen(img_path, confidence=confidence, minSearchTime=search_time)
            x = box.left + box.width / 2
            y = box.top + box.height / 2
            Bot.click_at(x, y)
        except pyautogui.ImageNotFoundException as e:
            return False
        return True

    @staticmethod
    # THIS ONLY WORKS PERFECTLY FOR 15FPS LOL cap t hat shit
    def get_to_playarea():
        keydelay: int = 80
        ahk.send('s', key_press_duration=2000, key_delay=keydelay)
        ahk.send('a', key_press_duration=2500, key_delay=keydelay)
        ahk.send('s', key_press_duration=1250, key_delay=keydelay)
        # start going forward from the corner
        ahk.send('w', key_press_duration=3250, key_delay=keydelay)
        ahk.send('a', key_press_duration=330, key_delay=keydelay)
        ahk.send('w', key_press_duration=2500, key_delay=keydelay)
        ahk.send('a', key_press_duration=350, key_delay=keydelay)
        ahk.send('w', key_press_duration=925, key_delay=keydelay)
        ahk.send('a', key_press_duration=350, key_delay=keydelay)
        ahk.send('w', key_press_duration=350, key_delay=keydelay)
        ahk.send('a', key_press_duration=350, key_delay=keydelay)
        ahk.send('w', key_press_duration=350, key_delay=keydelay)
        ahk.send('a', key_press_duration=350, key_delay=keydelay)
        ahk.send('w', key_press_duration=1250, key_delay=keydelay)

    @staticmethod
    def enter_portal():
        keydelay: int = 80
        for n in range(5):
            ahk.send('d', key_press_duration=350, key_delay=keydelay)
            ahk.send('w', key_press_duration=350, key_delay=keydelay)

    @staticmethod
    # top_left and bottom_right define a rectangular region to interpolate over and try placing down units
    def place_units(top_left: int, bottom_right: int):
        points = get_points_in_rect(top_left, bottom_right)
        for (x, y) in points:
            ...
        ...

    @staticmethod
    # top_left and bottom_right should be the same as the ones passed into place_units
    def upgrade_units(top_left: int, bottom_right: int):
        points = get_points_in_rect(top_left, bottom_right)
        for (x, y) in points:
            # click, then if an image is found with the upgrade button click it a few times and continue
            ...
        ...
