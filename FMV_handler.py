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
import config

position = namedtuple('position', ['x', 'y'])
region = namedtuple('region', ['x', 'y', 'w', 'h'])
size = namedtuple('size', ['w', 'h'])
temp_dir = "temp_images"

class FMV_handler:
    def __init__(self, scan_size):
        pyautogui.PAUSE = config.BASIC['mouse_speed']*0.1
        os.makedirs(temp_dir, exist_ok=True)
        capture = cv2.imread(config.BASIC['screen_ref'])
        base_height, base_width, _ = capture.shape
        screen_ref = cv2.imread(config.BASIC['game_capture'])
        h, w, _ = screen_ref.shape
        if (base_height / w) > 1.1 or (base_height / w) < 0.9:
            self.scale = size(base_width / w, base_height / h)
        else:
            self.scale = size(1, 1)


        self.item_dir = 'item_template'
        self.scan_size = 9
        self.init_mouse_position()
        self.init_parameters()
        # 9-17

    def align_images(self, image):
        if self.scale.w > 1.1 or self.scale.w < 0.9:
            image = cv2.resize(image, (0, 0), fx=self.scale.w, fy=self.scale.h)
        return image
    
    def init_mouse_position(self):
        # get window position
        self.game_ref = self.get_item_position()
        if self.game_ref.x is None:
            print("Failed to get window position.")
            return

        # game area
        self.game_area_pos = position(self.game_ref.x + config.RELATIVE['game_x'] * self.scale.w, 
                                      self.game_ref.y + config.RELATIVE['game_y'] * self.scale.h)
        self.game_area = region(self.game_area_pos.x, 
                                self.game_area_pos.y, 
                                config.SIZE['game_width'] * self.scale.w,
                                config.SIZE['game_height'] * self.scale.h)
        self.drag = position(self.game_ref.x + config.RELATIVE['drag_x'] * self.scale.w,
                             self.game_ref.y + config.RELATIVE['drag_y'] * self.scale.h)
    
    def init_parameters(self):
        # (777, 348) (844, 315) (777, 282)
        # slot size
        self.item_size = size(config.SIZE['item_width'] * self.scale.w, 
                              config.SIZE['item_height'] * self.scale.h)
        self.slot_size = size(config.SIZE['slot_width'] * self.scale.w, 
                              config.SIZE['slot_height'] * self.scale.h)
        self.slot_gap = config.SIZE['slant_distance'] * self.scale.w
        self.slot_gap_y = config.SIZE['vertical_distance'] * self.scale.h
        self.slot_angle = np.arctan(0.33/0.67) # 19.5 degree

        self.slot_relative = position(config.RELATIVE['slot_x'] * self.scale.w, 
                                      config.RELATIVE['slot_y'] * self.scale.h)

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
        screenshot = pyautogui.screenshot()
        frame = np.array(screenshot)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        if region is not None:
            frame = frame[region.y:region.y + region.h, region.x:region.x + region.w]
        return frame
        
    def get_item_position(self, region=None, item_name=config.BASIC['game_capture'], retries=3):
        screenshot = self.take_screenshot(region)
        template = cv2.imread(item_name, cv2.IMREAD_COLOR)
        template = self.align_images(template)
        h, w, _ = template.shape

        result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        if max_val > 0.8:  # 匹配閾值
            return position(int(max_loc[0] + w / 2), int(max_loc[1] + h / 2))
        else:
            # print(f"No matching window found! Retries left: {retries}")
            if retries > 0:
                only_item_name = item_name[:-4]
                name, number = only_item_name.split('_')
                try:
                    number = int(number) + 1
                    return self.get_item_position(region, f"{name}_{number}.png", retries - 1)
                except ValueError:
                    time.sleep(1)
                    return self.get_item_position(region, item_name, retries - 1)
            else:
                # print(f"Max retries reached. Unable to find the {item_name}.")
                return position(None, None)

        
    def init_screen_position(self):
        pyautogui.moveTo(self.drag.x, self.drag.y)
        pyautogui.scroll(-30, x=None, y=None)
        pyautogui.moveTo(self.drag.x, self.drag.y)
        pyautogui.drag(0, -150, duration=0.1, button='left')
        time.sleep(1.5)
        pyautogui.moveTo(self.drag.x, self.drag.y)
        pyautogui.drag(0, -150, duration=0.1, button='left')
        time.sleep(1.5)
        # pyautogui.drag(0, 40, duration=1, button='left')

    def screen_slider(self, distance):
        pyautogui.moveTo(self.drag.x, self.drag.y)
        time.sleep(0.3)
        pyautogui.mouseDown(button='left')
        pyautogui.move(0, distance * (1 + config.BASIC['drag_fix']), duration=config.BASIC['mouse_speed'])
        pyautogui.move(0, -distance * config.BASIC['drag_fix'], duration=config.BASIC['mouse_speed'])
        time.sleep(config.BASIC['mouse_speed']*0.3)
        pyautogui.mouseUp(button='left')

    def slot_calculator(self, pos, dir_x, dir_y):
        goal_x = int(pos.x + self.slot_gap * dir_x * np.cos(self.slot_angle))
        goal_y = pos.y - self.slot_gap * dir_x * np.sin(self.slot_angle)
        goal_y = int(goal_y - self.slot_gap_y * dir_y)
        return position(goal_x, goal_y)
    
    def slot_calculator_dia(self, pos, dir_x, dir_y):
        goal_x = pos.x + self.slot_gap * dir_x * np.cos(self.slot_angle)
        goal_y = pos.y - self.slot_gap * dir_x * np.sin(self.slot_angle)
        goal_x = int(goal_x - self.slot_gap * dir_y * np.cos(self.slot_angle))
        goal_y = int(goal_y - self.slot_gap * dir_y * np.sin(self.slot_angle))
        return position(goal_x, goal_y)
    
    def item_region(self, pos, region_size):
        slot_x = int(pos.x - (region_size.w / 2))
        if region_size.h > 75:
            slot_y = int(pos.y - (region_size.h * 0.5))
        else:
            slot_y = int(pos.y - (region_size.h * 0.5))
        return region(slot_x, slot_y, region_size.w, region_size.h)
    
    def get_play_initial_position(self):
        light_pos = self.get_item_position(item_name=config.BASIC['slot_ref'])
        relative_play_pos = position(light_pos.x + self.slot_relative.x, light_pos.y + self.slot_relative.y)
        play_pos = self.slot_calculator(relative_play_pos, -8, 0)
        return play_pos
    
    def game_to_screen(self, pos):
        return position(self.game_area_pos.x + pos.x, self.game_area_pos.y + pos.y)
    
    def capture_slot(self):
        # slot_matrix = np.full((17, 3), -1)
        self.init_screen_position()
        self.screen_slider(self.slot_gap_y*config.SIZE['init_scan_position'])

        for i in range(0, (len(self.farm_shape1)), 3):
            light_pos = self.get_item_position(region=self.game_area, item_name=config.BASIC['slot_ref'])
            relative_scan = position(light_pos.x + self.slot_relative.x, light_pos.y + self.slot_relative.y)
            game_image = self.take_screenshot(region=self.game_area)
            for j in range(i, i+3):
                init_scan = self.slot_calculator(relative_scan, -(self.farm_shape1[j] - 1), j)
                if j > len(self.farm_shape1):
                    break
                for size in range(self.farm_shape1[j]):
                    scan_pos = self.slot_calculator(init_scan, size, 0)
                    slot_region = self.item_region(scan_pos, self.slot_size)
                    slot_img = game_image[slot_region.y:slot_region.y + self.slot_size.h, slot_region.x:slot_region.x + self.slot_size.w]
                    self.save_image(slot_img, temp_dir)
            if i < len(self.farm_shape1)-3:
                self.screen_slider(self.slot_gap_y*2.6)

    def compare_slot_image(self):
        # load images
        images = {}
        all_files = os.listdir(temp_dir)
        numeric_files = sorted(
            [file for file in all_files if os.path.splitext(file)[0].isdigit()],
            key=lambda x: int(os.path.splitext(x)[0])
        )
        for file in numeric_files:
            file_path = os.path.join(temp_dir, file)
            image = cv2.imread(file_path)
            if image is not None:
                file_number = int(os.path.splitext(file)[0])
                images[file_number] = image
        
        clusters = {}
        cross_compare = []
        for key, value in images.items():
            item_id = self.find_matching_item(value)
            clusters[key] = item_id
            if item_id == -2:
                cross_compare.append(key)
        
        visited = set()
        compare_id = 200
        for key in cross_compare:
            if key in visited:
                continue
            visited.add(key)
            compare_flag = False
            for key2 in cross_compare:
                if key2 in visited:
                    continue
                score = self.compare_method(images[key], self.crop_image(images[key2], self.item_size))
                if score > 0.8:
                    if not compare_flag:
                        clusters[key] = compare_id
                        compare_id += 1
                    compare_flag = True
                    clusters[key2] = clusters[key]
                    visited.add(key2)

        # Sort clusters by keys and transform into a list
        sorted_keys = sorted(clusters.keys())
        sorted_clusters = [clusters[key] for key in sorted_keys]
            
        result = []
        current_index = 0
        for row_length in self.farm_shape1:
            if current_index + row_length > len(sorted_clusters):
                raise ValueError("Farm shape exceeds cluster array size.")
            row = sorted_clusters[current_index:current_index + row_length]
            result.append(row)
            current_index += row_length

        return result
    
    def compare_method(self, img1, img2):
        method = cv2.TM_CCOEFF_NORMED
        result = cv2.matchTemplate(img1, img2, method)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        # align_image = self.align_images(item_image_gray, template_image)
        # score, _ = compare_ssim(img1, img2, full=True)
        score = max_val
        return score
    
    def crop_image(self, image, size):
        w, h, _ = image.shape
        x = int(w/2 - size.w/2)
        y = int(h/2 - size.h/2)
        return image[x:x+size.w, y:y+size.h]
    
    def find_matching_item(self, slot_image):
        max_match_value = 0.6
        matching_item_id = None
        slot_image_gray = cv2.cvtColor(slot_image, cv2.COLOR_BGR2GRAY)

        # compare the item image with the template images
        for item_folder in os.listdir("item_template"):
            item_folder_path = os.path.join("item_template", item_folder)
            score = 0
            if os.path.isdir(item_folder_path):
                for template_file in os.listdir(item_folder_path):
                    template_image_path = os.path.join(item_folder_path, template_file)
                    template_image = cv2.imread(template_image_path, cv2.IMREAD_GRAYSCALE)
                    if template_image is None:
                        continue

                    score = self.compare_method(slot_image_gray, template_image)
                    
                    if score > max_match_value:
                        max_match_value = score
                        matching_item_id = item_folder
            if score > 0.8 and matching_item_id is not None:
                break

        # if no matching item found, create a new folder
        # else, save the new item image
        if matching_item_id is None:
            print("No match found, creating a new folder for this item.")
            # new_item_id = str(self.get_next_path_id("item_template"))
            new_item_id = str(-2)
            new_folder = os.path.join("item_template", new_item_id)
            new_folder = Path(new_folder)
            new_folder.mkdir(parents=True, exist_ok=True)
            image_index = self.get_next_path_id(new_folder)
            save_img = self.crop_image(slot_image, self.item_size)
            cv2.imwrite(os.path.join("item_template", new_item_id, f"{image_index}.png"), save_img)
            matching_item_id = new_item_id
        else:
            if max_match_value < 0.8:
                image_index = self.get_next_path_id(os.path.join("item_template", matching_item_id))
                save_img = self.crop_image(slot_image, self.item_size)
                cv2.imwrite(os.path.join("item_template", matching_item_id, f"{image_index}.png"), save_img)

        return int(matching_item_id)

    def swap_item(self, from_pos, to_pos):
        pyautogui.moveTo(from_pos.x, from_pos.y)
        pyautogui.mouseDown(button='left')
        pyautogui.moveTo(to_pos.x, to_pos.y, duration=0.5)
        pyautogui.mouseUp(button='left')

    def save_image(self, image, dir, file_name=None):
        if image is None:
            print("No image to save.")
            return
        pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        next_item_id = self.get_next_path_id(dir, file_name)
        if file_name is None:
            file_name = f"{next_item_id}.png"
        else:
            file_name = file_name + f"{next_item_id}.png"
        pil_image.save(os.path.join(dir, file_name))
    
    def get_next_path_id(self, folder_path, file_name=None):
        existing_ids = []
        for file in os.listdir(folder_path):
            folder_name, _ = os.path.splitext(file)
            if file_name is not None:
                if folder_name.startswith(file_name):
                    folder_name = folder_name[len(file_name):]
                else:
                    continue
            if folder_name.isdigit():
                existing_ids.append(int(folder_name))

        if not existing_ids:
            return 0

        return max(existing_ids) + 1
    
    def __del__(self):
        shutil.rmtree(temp_dir)