from threading import Thread
from typing import Tuple

import numpy as np
import pyautogui
from ahk import AHK
import time
import cv2 as cv
from PIL import ImageGrab
import matplotlib as plt

ahk = AHK()
ahk.set_coord_mode('Mouse', 'Screen')


def get_points_in_rect(top_left: Tuple[int, int], bottom_right: Tuple[int, int]) -> list[(int, int)]:
    points = []

    x1 = top_left[0]
    y1 = top_left[1]
    x2 = bottom_right[0]
    y2 = bottom_right[1]

    # 5 points per axis
    points_per_axis: int = 5
    for i in range(points_per_axis):
        x = int(x1 + (x2 - x1) * float(i / points_per_axis))
        for j in range(points_per_axis):
            y = int(y1 + (y2 - y1) * float(j / points_per_axis))
            points.append((x, y))

    return points


running = True


class Bot:

    @staticmethod
    def click_at(x, y):
        ahk.mouse_move(x=x, y=y, speed=3.5, blocking=True)
        ahk.click(x=x, y=y, blocking=True)
        # whhy not
        time.sleep(0.02)

    @staticmethod
    def img_exists_on_screen(img_path: str, confidence: float, region=None) -> bool:
        try:
            box = pyautogui.locateOnScreen(img_path, confidence=confidence, region=region)
            pyautogui.locateOnScreen(img_path, confidence=confidence)
        except pyautogui.ImageNotFoundException as e:
            return False

        return box is not None

    @staticmethod
    def try_click_img(img_path: str, confidence: float, search_time: float = 0, region=None) -> bool:
        try:
            box = pyautogui.locateOnScreen(img_path, confidence=confidence, minSearchTime=search_time, region=region)

            x = box.left + box.width / 2
            y = box.top + box.height / 2
            Bot.click_at(x, y)
        except pyautogui.ImageNotFoundException as e:
            return False
        return True

    @staticmethod
    def get_img_coords(img_path: str, confidence: float, search_time: float, region=None) -> Tuple[int, int] | None:
        try:
            box = pyautogui.locateOnScreen(img_path, confidence=confidence, minSearchTime=search_time, region=region)

            x = box.left + box.width / 2
            y = box.top + box.height / 2
            return int(x), int(y)
        except pyautogui.ImageNotFoundException as e:
            return None

    @staticmethod
    def try_click_img_opencv(img_path: str, confidence: float, region=None):
        haystack = np.array(ImageGrab.grab())
        needle = cv.imread(img_path, cv.IMREAD_UNCHANGED)
        needle_w, needle_h = needle.shape[1], needle.shape[0]

        # run the OpenCV algorithm
        result = cv.matchTemplate(haystack, needle, cv.TM_CCOEFF_NORMED)
        # print("1--- %s seconds ---1" % (time.time() - start_time))
        # Get the positions from the match result that exceed our threshold
        locs = np.column_stack(np.where(result >= 0.5))

        # Group rectangles to eliminate redundancy
        rectangles = [(x, y, needle_w, needle_h) for x, y in locs]
        rectangles, _ = cv.groupRectangles(rectangles, groupThreshold=1, eps=0.5)

        points = []
        print(f"found {len(rectangles)} tangles.")
        # cv.imshow('cv result', haystack)
        # cv.waitKey(500)
        if rectangles is None or len(rectangles) == 0:
            return False
        line_color = (0, 255, 0)
        line_type = cv.LINE_4

        # # Loop over all the rectangles
        for (y, x, w, h) in rectangles:
            #     # Determine the center position
            center_x, center_y = x + int(w / 2), y + int(h / 2)
            #     # Save the points
            points.append((center_x, center_y))

            # Determine the box position
            top_left, bottom_right = (x, y), (x + w, y + h)
            # Draw the box
            cv.rectangle(haystack, top_left, bottom_right, color=line_color, lineType=line_type, thickness=2)

        x, y = points[0]
        Bot.click_at(x, y)

        return True

    @staticmethod
    # THIS ONLY WORKS PERFECTLY FOR 30FPS LOL cap t hat shit
    def get_to_playarea():
        keydelay: int = 80
        ahk.send('s', key_press_duration=1000, key_delay=keydelay)
        ahk.send('a', key_press_duration=2500, key_delay=keydelay)
        ahk.send('s', key_press_duration=1250, key_delay=keydelay)
        # start going forward from the corner
        ahk.send('w', key_press_duration=3250, key_delay=keydelay)
        ahk.send('a', key_press_duration=700, key_delay=keydelay)
        ahk.send('w', key_press_duration=800, key_delay=keydelay)
        ahk.send('d', key_press_duration=210, key_delay=keydelay)
        ahk.send('w', key_press_duration=2275, key_delay=keydelay)
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
    def place_units(top_left: Tuple[int, int], bottom_right: Tuple[int, int]):
        points = get_points_in_rect(top_left, bottom_right)
        for (x, y) in points:
            ahk.send('1')
            time.sleep(0.05)
            ahk.mouse_move(x, y, speed=3)
            ahk.click(x, y)
            time.sleep(0.05)
            ahk.send('c')

    @staticmethod
    # top_left and bottom_right should be the same as the ones passed into place_units
    # UPGRADE SCREEN MUST BE ON LEFT SIDE
    def upgrade_units(top_left: Tuple[int, int], bottom_right: Tuple[int, int], client_x: int, client_y: int,
                      client_w: int, client_h: int):
        points = get_points_in_rect(top_left, bottom_right)
        for (x, y) in points:
            # click, then if an image is found with the upgrade button click it a few times and continue
            ahk.mouse_move(x, y, speed=3)
            ahk.click(x, y)
            time.sleep(0.2)
            while Bot.try_click_img('upgrade_button.jpg', confidence=0.99,
                                 region=(client_x, client_y, int(client_w/2), client_h)):
                print("Upgraded unit!")
                # clear the view for bot to detect img again
                coords = ahk.get_mouse_position()
                ahk.mouse_move(coords.x, coords.y + 125, relative=True, speed=5)
