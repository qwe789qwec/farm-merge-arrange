import pyautogui
import time
import shutil
import os
import cv2
from skimage.metrics import structural_similarity as compare_ssim
import numpy as np
from PIL import Image
from pathlib import Path
from collections import namedtuple

slant_distance = 77 # adjust this value
vertical_distance = 69 # adjust this value

position = namedtuple('position', ['x', 'y'])
region = namedtuple('region', ['x', 'y', 'w', 'h'])
size = namedtuple('size', ['w', 'h'])
temp_dir = "temp_images"

class FMV_handler:
    def __init__(self, item_dir = 'item_template', scan_size = 9):
        pyautogui.PAUSE = 0.1
        os.makedirs(temp_dir, exist_ok=True)
        print(f"Temporary directory created: {temp_dir}")
        self.item_dir = item_dir
        self.scan_size = scan_size
        self.init_mouse_position()
        self.init_parameters()
        self.init_screen_position()
        # 9-17

    def init_mouse_position(self):
        # get window position
        self.gift = self.get_item_position()
        if self.gift.x is None:
            time.sleep(1)
            self.gift = self.get_item_position()
            if self.gift.x is None:
                print("Failed to get window position.")
                return
        print(f"gift position: ({self.gift.x}, {self.gift.y})")

        # game area
        self.game_area = region(self.gift.x - 700, self.gift.y - 600, 1400, 700)
        self.drag = position(self.gift.x + 700, self.gift.y - 300)
    
    def init_parameters(self):
        # (777, 348) (844, 315) (777, 282)
        # slot size
        self.item_size = size(45, 50)
        self.slot_size = size(80, 80)
        self.slot_gap = slant_distance
        self.slot_gap_y = vertical_distance
        self.slot_angle = np.arctan(0.33/0.67)

        self.scan_go_up = 199
        self.play_go_down = 330

        # light (1337, 213) | scan (1243, 223)
        self.slot_relative_position = position(-90, 10)

        self.farm_shape1 = [9, 10, 11, 12, 13, 14, 15, 16, 17]

        self.scan_index = []
        current_index = 0
        for row_size in self.farm_shape1:
            if row_size % 2 == 1:
                row = np.arange(current_index, current_index + row_size)
            else:
                row = np.arange(current_index + row_size - 1, current_index - 1, -1)
            self.scan_index.append(row)
            current_index += row_size

    def take_screenshot(self, region=None):
        # pyautogui.moveTo(self.drag.x, self.drag.y)
        # pyautogui.click()
        screenshot = pyautogui.screenshot()
        frame = np.array(screenshot)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        if region is not None:
            frame = frame[region.y:region.y + region.h, region.x:region.x + region.w]
        return frame
    
    def get_item_position(self, region=None,item_name='buttons/gift_button.png'):
        screenshot = self.take_screenshot(region)
        template = cv2.imread(item_name, cv2.IMREAD_COLOR)
        # size of the template image
        h, w, _ = template.shape
        result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        # get window position
        if max_val > 0.8:  # matching threshold
            # print(f"window position: {max_loc}")
            return position(int(max_loc[0] + h/2), int(max_loc[1] + w/2))
        else:
            print("no matching window found!")
            return position(None, None)
        
    def init_screen_position(self):
        pyautogui.moveTo(self.gift.x, self.gift.y)
        pyautogui.scroll(-30, x=None, y=None)
        pyautogui.moveTo(self.drag.x, self.drag.y)
        pyautogui.drag(0, -150, duration=0.1, button='left')
        time.sleep(1.5)
        pyautogui.moveTo(self.drag.x, self.drag.y)
        pyautogui.drag(0, -150, duration=0.1, button='left')
        time.sleep(1.5)
        # pyautogui.drag(0, 40, duration=1, button='left')

    def init_play_position(self):
        self.init_screen_position()
        pyautogui.drag(0, 40, duration=0.6, button='left')
        time.sleep(1.5)

    def screen_slider(self, distance):
        pyautogui.moveTo(self.drag.x, self.drag.y)
        time.sleep(0.3)
        pyautogui.mouseDown(button='left')
        pyautogui.move(0, distance, duration=1)
        time.sleep(0.3)
        pyautogui.mouseUp(button='left')
        pyautogui.click()

    def slot_calculator(self, pos, dir_x, dir_y):
        goal_x = int(pos.x + self.slot_gap * dir_x * np.cos(self.slot_angle))
        goal_y = pos.y - self.slot_gap * dir_x * np.sin(self.slot_angle)
        goal_y = int(goal_y - self.slot_gap_y * dir_y)
        return position(goal_x, goal_y)
    
    def item_region(self, pos, region_size):
        slot_x = int(pos.x - (region_size.w / 2))
        if region_size.h > 75:
            slot_y = int(pos.y - ((region_size.h/4) * 3))
        else:
            slot_y = int(pos.y - region_size.h + 10)
        return region(slot_x, slot_y, region_size.w, region_size.h)
    
    def make_rectangle(self, image, region, color=(255,0,0), thickness=3):
        start = (region.x, region.y)
        end = (region.x + region.w, region.y + region.h)
        cv2.rectangle(image, start, end, color, thickness)
        return image
    
    def get_play_initial_position(self):
        light_pos = self.get_item_position(item_name='buttons/light.png')
        relative_play_pos = position(light_pos.x + self.slot_relative_position.x, light_pos.y + self.slot_relative_position.y)
        play_pos = self.slot_calculator(relative_play_pos, -8, 0)
        return play_pos
    
    def check_slot(self):
        self.init_screen_position()
        self.screen_slider(self.slot_gap_y/2)

        for i in range(len(self.farm_shape1)):
            light_pos = self.get_item_position(region=self.game_area, item_name='buttons/light.png')
            relative_scan = position(light_pos.x + self.slot_relative_position.x, light_pos.y + self.slot_relative_position.y)
            init_scan = self.slot_calculator(relative_scan, -(self.farm_shape1[i] - 1), i)
            game_image = self.take_screenshot(region=self.game_area)
            img = game_image

            for j in range(self.farm_shape1[i]):
                scan_pos = self.slot_calculator(init_scan, j, 0)
                slot_region = self.item_region(scan_pos, self.slot_size)
                img = self.make_rectangle(img, slot_region)
                item_region = self.item_region(scan_pos, self.item_size)
                img = self.make_rectangle(img, item_region)

            self.screen_slider(self.slot_gap_y)
            self.save_image(img, "buttons")

    def capture_slot(self):
        # slot_matrix = np.full((17, 3), -1)
        self.init_screen_position()
        self.screen_slider(self.slot_gap_y*0.6)

        for i in range(len(self.farm_shape1)):
            light_pos = self.get_item_position(region=self.game_area, item_name='buttons/light.png')
            relative_scan = position(light_pos.x + self.slot_relative_position.x, light_pos.y + self.slot_relative_position.y)
            init_scan = self.slot_calculator(relative_scan, -(self.farm_shape1[i] - 1), i)
            game_image = self.take_screenshot(region=self.game_area)

            for j in range(self.farm_shape1[i]):
                scan_pos = self.slot_calculator(init_scan, j, 0)
                slot_region = self.item_region(scan_pos, self.slot_size)
                slot_img = game_image[slot_region.y:slot_region.y + self.slot_size.h, slot_region.x:slot_region.x + self.slot_size.w]
                self.save_image(slot_img, temp_dir)
                item_region = self.item_region(scan_pos, self.item_size)
                item_img = game_image[item_region.y:item_region.y + self.item_size.h, item_region.x:item_region.x + self.item_size.w]
                self.save_image(item_img, temp_dir)

            if i < 8:
                self.screen_slider(self.slot_gap_y)
    
    def compare_method(self, img1, img2):
        result = cv2.matchTemplate(img1, img2, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        return max_val


    def compare_slot_image(self):
        image_id = [
            int(name)
            for name in (os.path.splitext(image_file)[0] for image_file in os.listdir(temp_dir))
            if name.isdigit()
        ]

        file_number = max(image_id, default=0)
        if file_number <= 0:
            raise ValueError("No valid images found in the directory.")

        threshold = 0.8
        slot_size = (file_number + 1) // 2
        clusters = np.zeros((slot_size,), dtype=int)
        scores = np.zeros((slot_size,), dtype=int)

        # preloading images
        images = {int(os.path.splitext(file)[0]): cv2.imread(os.path.join(temp_dir, file))
                for file in os.listdir(temp_dir)
                if os.path.splitext(file)[0].isdigit()}

        for i in range(0, file_number, 2):
            slot_number = i // 2
            slot_image = images.get(i)
            if slot_image is None:
                continue
            if scores[slot_number] == 0:
                clusters[slot_number] = slot_number

            for j in range(1, file_number, 2):
                item_number = (j - 1) // 2
                if slot_number == item_number:
                    continue
                item_image = images.get(j)
                if item_image is None:
                    continue

                score = self.compare_method(slot_image, item_image)
                if score > threshold and score > scores[item_number]:
                    clusters[item_number] = slot_number
                    scores[item_number] = score

        result = []
        current_index = 0
        for row_length in self.farm_shape1:
            if current_index + row_length > len(clusters):
                raise ValueError("Farm shape exceeds cluster array size.")
            row = clusters[current_index:current_index + row_length]
            result.append(row)
            current_index += row_length

        return result

    def swap_item(self, from_pos, to_pos):
        pyautogui.moveTo(from_pos.x, from_pos.y)
        pyautogui.mouseDown(button='left')
        pyautogui.moveTo(to_pos.x, to_pos.y, duration=0.5)
        pyautogui.mouseUp(button='left')

    def save_image(self, image, dir):
        if image is None:
            print("No image to save.")
            return
        pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        next_item_id = self.get_next_path_id(dir)
        filename = f"{next_item_id}.png"
        pil_image.save(os.path.join(dir, filename))
    
    def get_next_path_id(self, folder_path):
        existing_ids = []
        for item_folder in os.listdir(folder_path):
            folder_name, _ = os.path.splitext(item_folder)
            if folder_name.isdigit():
                existing_ids.append(int(folder_name))

        if not existing_ids:
            return 0

        return max(existing_ids) + 1
    
    def __del__(self):
        shutil.rmtree(temp_dir)
        print(f"Temporary directory deleted: {temp_dir}")

test = False
if test:
    scna_size = 9
    game = FMV_handler(scan_size=scna_size)
    # game.screen_slider(game.slot_gap_y * 1.4)
    # game.save_image(game.take_screenshot(region=game.game_area), "buttons")
    # light_pos = game.get_item_position(region=game.game_area, item_name='buttons/light.png')
    # light_pos = game.get_item_position(region=game.game_area, item_name='buttons/light.png')
    # print(light_pos)
    # init_game = position(light_pos.x + game.scan_relative_position.x, light_pos.y + game.scan_relative_position.y)
    # scan_pos = game.slot_calculator(init_game, -16, 0)
    # pyautogui.moveTo(scan_pos.x, scan_pos.y)

    game.check_slot()

    # play_pos = game.get_play_initial_position()
    # pyautogui.moveTo(play_pos.x, play_pos.y)