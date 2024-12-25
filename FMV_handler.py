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
    def __init__(self, item_dir = 'item_template', scan_size = 9):
        pyautogui.PAUSE = config.BASIC['mouse_speed']*0.1
        os.makedirs(temp_dir, exist_ok=True)
        self.item_dir = item_dir
        self.scan_size = scan_size
        self.init_mouse_position()
        self.init_parameters()
        # 9-17

    def init_mouse_position(self):
        # get window position
        self.gift = self.get_item_position()
        if self.gift.x is None:
            print("Failed to get window position.")
            return
        # print(f"gift position: ({self.gift.x}, {self.gift.y})")

        # game area
        self.game_area = region(self.gift.x + config.RELATIVE['game_x'], 
                                self.gift.y + config.RELATIVE['game_y'], 
                                config.SIZE['game_width'], 
                                config.SIZE['game_height'])
        self.drag = position(self.gift.x + config.RELATIVE['drag_x'], self.gift.y + config.RELATIVE['drag_y'])
    
    def init_parameters(self):
        # (777, 348) (844, 315) (777, 282)
        # slot size
        self.item_size = size(config.SIZE['item_width'], config.SIZE['item_height'])
        self.slot_size = size(config.SIZE['slot_width'], config.SIZE['slot_height'])
        self.slot_gap = config.SIZE['slant_distance']
        self.slot_gap_y = config.SIZE['vertical_distance']
        self.slot_angle = np.arctan(0.33/0.67)

        self.scan_go_up = 199
        self.play_go_down = 330

        # light (1337, 213) | scan (1243, 223)
        self.slot_relative_position = position(config.RELATIVE['slot_x'], config.RELATIVE['slot_y'])

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
        
    def get_item_position(self, region=None, item_name=config.BASIC['scan_screen'], retries=3):
        screenshot = self.take_screenshot(region)
        template = cv2.imread(item_name, cv2.IMREAD_COLOR)
        h, w, _ = template.shape

        result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        if max_val > 0.8:  # 匹配閾值
            return position(int(max_loc[0] + h / 2), int(max_loc[1] + w / 2))
        else:
            print(f"No matching window found! Retries left: {retries}")
            if retries > 0:
                if item_name == config.BASIC['scan_screen']:
                    time.sleep(1)
                    return self.get_item_position(region, item_name, retries - 1)
                else:
                    item_name = item_name[:-4]
                    name, number = item_name.split('_')
                    number = int(number) + 1
                    return self.get_item_position(region, f"{name}_{number}.png", retries - 1)
            else:
                print("Max retries reached. Unable to find the window.")
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

    def screen_slider(self, distance):
        pyautogui.moveTo(self.drag.x, self.drag.y)
        time.sleep(0.3)
        if config.BASIC['move_method'] == 'drag':
            pyautogui.dragRel(0,distance,duration=config.BASIC['mouse_speed'],button='left')
            if config.BASIC['drag_fix'] > 0:
                pyautogui.dragRel(0,distance*config.BASIC['drag_fix'],duration=config.BASIC['mouse_speed'],button='left')
                pyautogui.dragRel(0,-distance*config.BASIC['drag_fix'],duration=config.BASIC['mouse_speed'],button='left')
        else:
            pyautogui.mouseDown(button='left')
            pyautogui.move(0, distance, duration=config.BASIC['mouse_speed'])
            if config.BASIC['drag_fix'] > 0:
                pyautogui.move(0, distance*config.BASIC['drag_fix'], duration=config.BASIC['mouse_speed'])
                pyautogui.move(0, -distance*config.BASIC['drag_fix'], duration=config.BASIC['mouse_speed'])
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
        light_pos = self.get_item_position(item_name=config.BASIC['init_slot_position'])
        relative_play_pos = position(light_pos.x + self.slot_relative_position.x, light_pos.y + self.slot_relative_position.y)
        play_pos = self.slot_calculator(relative_play_pos, -8, 0)
        return play_pos
    
    def capture_slot(self):
        # slot_matrix = np.full((17, 3), -1)
        self.init_screen_position()
        self.screen_slider(self.slot_gap_y*config.SIZE['init_scan_position'])

        for i in range(0, (len(self.farm_shape1)), 3):
            light_pos = self.get_item_position(region=self.game_area, item_name=config.BASIC['init_slot_position'])
            relative_scan = position(light_pos.x + self.slot_relative_position.x, light_pos.y + self.slot_relative_position.y)
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
                    item_region = self.item_region(scan_pos, self.item_size)
                    item_img = game_image[item_region.y:item_region.y + self.item_size.h, item_region.x:item_region.x + self.item_size.w]
                    self.save_image(item_img, temp_dir)
            if i < len(self.farm_shape1)-3:
                self.screen_slider(self.slot_gap_y*2.6)

    def compare_method(self, img1, img2):
        method = cv2.TM_CCOEFF_NORMED
        result = cv2.matchTemplate(img1, img2, method)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        # align_image = self.align_images(item_image_gray, template_image)
        # score, _ = compare_ssim(img1, img2, full=True)
        score = max_val
        return score


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
        if config.BASIC['scan_method'] == 'template':
            for i in range(0, file_number, 2):
                slot_number = i // 2
                slot_image = images.get(i)
                if slot_image is None:
                    continue
                clusters[slot_number] = self.find_matching_item(slot_image)
        else:
            for i in range(0, file_number, 2):
                slot_number = i // 2
                slot_image = images.get(i)
                if slot_image is None:
                    continue
                if scores[slot_number] == 0:
                    clusters[slot_number] = -1

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
    
    def find_matching_item(self, item_image):
        max_match_value = 0.6
        matching_item_id = None
        item_image_gray = cv2.cvtColor(item_image, cv2.COLOR_BGR2GRAY)

        # compare the item image with the template images
        for item_folder in os.listdir("item_template"):
            item_folder_path = os.path.join("item_template", item_folder)
            
            if os.path.isdir(item_folder_path):
                for template_file in os.listdir(item_folder_path):
                    template_image_path = os.path.join(item_folder_path, template_file)
                    template_image = cv2.imread(template_image_path, cv2.IMREAD_GRAYSCALE)
                    if template_image is None:
                        continue

                    score = self.compare_method(item_image_gray, template_image)
                    
                    if score > max_match_value:
                        max_match_value = score
                        matching_item_id = item_folder
                    if score > 0.8 and matching_item_id is not None:
                        # if not template_file.startswith("0_"):
                        #     new_name = f"0_{template_file}"
                        #     new_path = os.path.join(item_folder_path, new_name)
                        #     os.rename(template_image_path, new_path)
                        #     print(f"Renamed: {template_image_path} -> {new_path}")
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
            cv2.imwrite(os.path.join("item_template", new_item_id, f"{image_index}.png"), item_image)
            matching_item_id = new_item_id
        else:
            image_index = self.get_next_path_id(os.path.join("item_template", matching_item_id))
            if image_index < 500 and max_match_value < 0.8:
                cv2.imwrite(os.path.join("item_template", matching_item_id, f"{image_index}.png"), item_image)

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