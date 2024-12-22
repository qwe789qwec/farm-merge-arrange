import pyautogui
import time
import os
import cv2
from skimage.metrics import structural_similarity as compare_ssim
import numpy as np
from PIL import Image
import easyocr
from pathlib import Path
from collections import defaultdict

reader = easyocr.Reader(['en'], gpu = True)

class FMV_handler:
    def __init__(self, item_dir = 'item_template', scan_size = 9):
        pyautogui.PAUSE = 0.1
        self.item_dir = item_dir
        self.init_mouse_position()
        self.init_screen_position()
        # 9-17

    def init_mouse_position(self):
        # get window position
        self.gift_x, self.gift_y = self.get_game_position()
        if self.gift_x is None:
            time.sleep(1)
            self.gift_x, self.gift_y = self.get_game_position()
            if self.gift_x is None:
                print("Failed to get window position.")
                return
        print(f"gift position: ({self.gift_x}, {self.gift_y})")

        # slot size
        self.slot_w = 60
        self.slot_h = 50
        self.slot_gap = 77
        self.slot_gap_y = 68
        self.slot_angle = np.arctan(0.34/0.7)

        # game area
        self.screen_x = self.gift_x - 700
        self.screen_y = self.gift_y - 660
        self.screen_w = 1400
        self.screen_h = 770

        self.drag_x = self.gift_x + 700
        self.drag_y = self.gift_y - 300

        self.init_slot_x = self.gift_x + 10
        self.init_slot_y = self.gift_y - 196
        self.init_slot_x, self.init_slot_y = self.slot_calculator(self.init_slot_x, self.init_slot_y, -8, 0)

        self.scan_init_x, self.scan_init_y = 708, 460
        self.scan_init_x, self.scan_init_y = self.slot_calculator(self.scan_init_x, self.scan_init_y, -8, 0)

        self.game_x = self.gift_x + 10
        self.game_y = self.gift_y - 95
        self.game_x, self.game_y = self.slot_calculator(self.game_x, self.game_y, -8, 0)

    def init_screen_position(self):
        pyautogui.moveTo(self.gift_x, self.gift_y)
        pyautogui.scroll(-30, x=None, y=None)
        pyautogui.moveTo(self.drag_x, self.drag_y)
        pyautogui.drag(0, -150, duration=0.1, button='left')
        time.sleep(1.5)
        pyautogui.drag(0, -150, duration=0.1, button='left')
        time.sleep(1.5)
        # pyautogui.drag(0, 40, duration=1, button='left')

    def init_play_position(self):
        pyautogui.moveTo(self.gift_x, self.gift_y)
        pyautogui.scroll(-30, x=None, y=None)
        pyautogui.moveTo(self.drag_x, self.drag_y)
        pyautogui.drag(0, -150, duration=0.1, button='left')
        time.sleep(1.5)
        pyautogui.drag(0, -150, duration=0.1, button='left')
        time.sleep(1.5)
        pyautogui.drag(0, 40, duration=0.6, button='left')
        time.sleep(1.5)
    
    def scan_go_up(self):
        pyautogui.moveTo(self.drag_x, self.drag_y)
        time.sleep(0.3)
        pyautogui.mouseDown(button='left')
        pyautogui.move(0, 199, duration=1)
        time.sleep(0.3)
        pyautogui.mouseUp(button='left')
        pyautogui.click()
    
    def play_go_up(self):
        pyautogui.moveTo(self.drag_x, self.drag_y)
        time.sleep(0.3)
        pyautogui.mouseDown(button='left')
        pyautogui.move(0, 330, duration=1)
        time.sleep(0.3)
        pyautogui.mouseUp(button='left')
        pyautogui.click()

    def play_go_down(self):
        pyautogui.moveTo(self.drag_x, self.drag_y)
        time.sleep(0.3)
        pyautogui.mouseDown(button='left')
        pyautogui.move(0, -330, duration=1)
        time.sleep(0.3)
        pyautogui.mouseUp(button='left')
        pyautogui.click()

    def slot_calculator(self, x, y, dir_x, dir_y):
        goal_x = x + self.slot_gap * dir_x * np.cos(self.slot_angle)
        goal_y = y - self.slot_gap * dir_x * np.sin(self.slot_angle)
        goal_y = goal_y - self.slot_gap_y * dir_y
        return int(goal_x), int(goal_y)
    
    def slot_region(self, pos_x, pos_y):
        slot_x = pos_x - (self.slot_w / 2)
        slot_y = pos_y - self.slot_h
        return int(slot_x), int(slot_y)

    def get_game_position(self):
        screenshot = pyautogui.screenshot()
        screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        template = cv2.imread('buttons/get_gift.png', cv2.IMREAD_COLOR)
        # size of the template image
        h, w, _ = template.shape
        result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        # get window position
        if max_val > 0.8:  # matching threshold
            # print(f"window position: {max_loc}")
            return int(max_loc[0] + h/2), int(max_loc[1] + w/2)
        else:
            print("no matching window found!")
            return None, None
    
    def take_screenshot(self):
        pyautogui.moveTo(self.drag_x, self.drag_y)
        pyautogui.click()
        screenshot = pyautogui.screenshot(region=(self.screen_x, self.screen_y, self.screen_w, self.screen_h))
        frame = np.array(screenshot)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        self.latest_image = frame

    def adjust_position(self, x, y):
        slot_x, slot_y = self.slot_calculator(x, y, 8, 0)
        scan_x, scan_y = self.slot_region(slot_x, slot_y)
        slot_img = self.latest_image[scan_y:scan_y + self.slot_h, scan_x:scan_x + self.slot_w]
        index = self.find_matching_item(slot_img)
        print("get", index)
        game_image_gray = cv2.cvtColor(self.latest_image, cv2.COLOR_BGR2GRAY)
        template_image_path = os.path.join("item_template", str(index), "0.png")
        template_image = cv2.imread(template_image_path, cv2.IMREAD_GRAYSCALE)
        method = cv2.TM_CCOEFF_NORMED
        result = cv2.matchTemplate(game_image_gray, template_image, method)
        _, _, _, max_loc = cv2.minMaxLoc(result)
        print("location", max_loc)
        loc_x, loc_y = max_loc
        if (loc_x + loc_y) - (scan_x + scan_y) > 150:
            print("too far")
            return x, y
        adj_x, adj_y = self.slot_calculator(int(loc_x + (self.slot_w/2)), int(loc_y + (self.slot_h/2)), -8, 0)

        return adj_x, adj_y

    def scan_slot(self, is_scan=True):
        slot_matrix = np.full((17, 3), -1)
        self.take_screenshot()
        # self.scan_init_x, self.scan_init_y = self.adjust_position(self.scan_init_x, self.scan_init_y)

        if is_scan:
            slot_x, slot_y = self.slot_calculator(self.scan_init_x, self.scan_init_y, 16, -1)
            scan_x, scan_y = self.slot_region(slot_x, slot_y)
            slot_img = self.latest_image[scan_y:scan_y + self.slot_h, scan_x:scan_x + self.slot_w]
            index = self.find_matching_item(slot_img)
            if index > 150:
                slot_matrix[16, 2] = -1
            else:
                slot_matrix[16, 2] = index
            time.sleep(0.1)
        else:
            slot_matrix[16, 2] = -1
            time.sleep(0.1)
        
        for i in range(17*3-1):
            row, col = divmod(i, 17)
            slot_x, slot_y = self.slot_calculator(self.scan_init_x, self.scan_init_y, col, row)
            scan_x, scan_y = self.slot_region(slot_x, slot_y)
            slot_img = self.latest_image[scan_y:scan_y + self.slot_h, scan_x:scan_x + self.slot_w]
            index = self.find_matching_item(slot_img)
            if index > 150:
                slot_matrix[col, row] = -1
            else:
                slot_matrix[col, row] = index
            time.sleep(0.1)

        return slot_matrix

    def swap_item(self, from_x, from_y, to_x, to_y):
        pyautogui.moveTo(from_x, from_y)
        pyautogui.mouseDown(button='left')
        pyautogui.moveTo(to_x, to_y, duration=0.5)
        pyautogui.mouseUp(button='left')

    def save_image(self, image, dir):
        if image is None:
            print("No image to save.")
            return
        pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        next_item_id = self.get_next_path_id(dir)
        filename = f"{next_item_id}.png"
        pil_image.save(os.path.join(dir, filename))

    def get_score(self, take_screenshot=True):
        score_str = None
        score = 0
        check_time = 0

        while score is None and check_time < 2:
            score_region = self.latest_image[self.score_y:self.score_y + self.score_h, self.score_x:self.score_x + self.score_w]
            gray = cv2.cvtColor(score_region, cv2.COLOR_BGR2GRAY)
            _, thresh_image = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
            score_str = reader.readtext(thresh_image)
            check_time += 1
            if score_str is None and check_time < 2 and take_screenshot:
                time.sleep(1)
                self.take_screenshot()
        
        if score_str == [] or score_str is None:
            score = 0
        else:
            try:
                if score_str[0][1].count(',') > 0:
                    score = int(score_str[0][1].replace(',', ''))
                else:
                    score = int(score_str[0][1])
                self.last_score = score
            except ValueError:
                return self.last_score
        self.score = score
        return self.score
    
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
                    # align_image = self.align_images(item_image_gray, template_image)
                    score, _ = compare_ssim(item_image_gray, template_image, full=True)
                    # method = cv2.TM_CCOEFF_NORMED
                    # result = cv2.matchTemplate(item_image_gray, template_image, method)
                    # _, score, _, _ = cv2.minMaxLoc(result)
                    
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
            new_item_id = str(self.get_next_path_id("item_template"))
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
    
    def get_next_path_id(self, folder_path):
        existing_ids = []
        for item_folder in os.listdir(folder_path):
            folder_name, _ = os.path.splitext(item_folder)
            if folder_name.isdigit():
                existing_ids.append(int(folder_name))

        if not existing_ids:
            return 0

        return max(existing_ids) + 1

test = False
if test:
    size = 9
    game = FMV_handler(scan_size=size)
    print("scan position:", game.scan_init_x, game.scan_init_y)
    game.take_screenshot()
    game.scan_init_x, game.scan_init_y = game.adjust_position(game.scan_init_x, game.scan_init_y)
    print("scan position2:", game.scan_init_x, game.scan_init_y)
    # game_x, game_y = game.slot_calculator(game.game_x, game.game_y, 8, 0)
    # print("game position:", game_x, game_y)
    # game_x, game_y = game.adjust_position(game.game_x, game.game_y)
    # print("game position2:", game_x, game_y)