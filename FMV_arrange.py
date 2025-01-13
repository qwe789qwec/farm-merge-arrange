from FMV_handler import FMV_handler as fmv
import config
import time
import numpy as np
import pyautogui

start_time = time.time()

class FMV_arrange:
    def __init__(self):
        self.game = fmv()
        self.limit = 12
        self.arrange_flag = False
        self.stop_flag = False
        self.buttons_list = ["buttons/train_gift.png",
                            "buttons/train_coin.png",
                            "buttons/train_water.png",
                            "buttons/train_heart.png",
                            "buttons/train_power.png",
                            "buttons/train_fource.png",
                            "buttons/train_finish.png",]

        self.scan_index = []
        current_index = 0
        for row_size in self.game.farm_shape1:
            if row_size % 2 == 1:
                row = np.arange(current_index, current_index + row_size)
            else:
                row = np.arange(current_index + row_size - 1, current_index - 1, -1)
            self.scan_index.append(row)
            current_index += row_size
    
    def scan_slot(self):
        self.game.capture_slot()
        self.items = self.game.compare_slot_image()

    def get_position(self, matrix, target):
        positions = []

        for row_index, row in enumerate(matrix):
            for col_index, element in enumerate(row):
                if element == target:
                    positions.append((row_index, col_index))

        return positions
    
    def get_rel_position(self, x, y, rel):
        index = self.scan_index[x][y]
        next_index = self.get_position(self.scan_index, index + rel)
        
        return next_index[0][0], next_index[0][1]
    
    def print_items(self):
        for row in self.items:
            print(row)
    
    def run_arrange(self):
        self.game.screen_slider(-self.game.slot_gap_y*((2.3*2)-1))
        self.play_pos = self.game.get_play_initial_position()
        self.print_items()
        move_times = 0
        last_item = 0
        item_count = 0
        visited = set()
        for row_index, row in enumerate(self.items):
            if row_index == 2 or row_index == 3:
                self.game.screen_slider(self.game.slot_gap_y)
                self.play_pos = self.game.get_play_initial_position()
                self.limit = self.limit + 1
            range_cols = range(len(row)) if row_index % 2 == 0 else range(len(row) - 1, -1, -1)
            for col_index in range_cols:
                item = row[col_index]
                if item <= -2:
                    self.stop_flag = True
                    break
                if col_index > self.limit or item <= 0 or item == 200:
                    continue
                if last_item != item:
                    item_count = 0
                    last_item = item
                item_pos = self.get_position(self.items, item)
                if len(item_pos) == 1:
                    continue

                next_row, next_col = self.get_rel_position(row_index, col_index, 1)
                visited.add((row_index, col_index))

                for position in item_pos:
                    while self.items[next_row][next_col] == item or self.items[next_row][next_col] <= 0:
                        visited.add((next_row, next_col))
                        next_row, next_col = self.get_rel_position(next_row, next_col, 1)
                        if self.items[next_row][next_col] == item:
                            item_count = item_count + 1
                    if item_count >= 4:
                        break
                    play_next = self.game.slot_calculator_dia(self.play_pos, next_col, next_row)
                    if (position[0], position[1]) not in visited and position[1] < self.limit:
                        from_row, from_col = position[0], position[1]
                        play_from = self.game.slot_calculator_dia(self.play_pos, from_col, from_row)
                        self.game.swap_item(play_from, play_next)
                        item_count = item_count + 1
                        move_times = move_times + 1
                        visited.add((next_row, next_col))
                        swap_item = self.items[from_row][from_col]
                        self.items[from_row][from_col] = self.items[next_row][next_col]
                        self.items[next_row][next_col] = swap_item
                        next_row, next_col = self.get_rel_position(next_row, next_col, 1)
                    if item_count >= 4:
                        break

            if self.stop_flag:
                break
            self.arrange_flag = True

    def run_combine(self):
        combinations = 0
        self.game.screen_slider(-(self.game.slot_gap_y*2))
        self.play_pos = self.game.get_play_initial_position()
        count = 0
        last_item = 0
        for row_index, row in enumerate(self.items):
            if row_index == 2 or row_index == 3:
                self.game.screen_slider(self.game.slot_gap_y)
                self.play_pos = self.game.get_play_initial_position()
                self.limit = self.limit + 0.6
            range_cols = range(len(row)) if row_index % 2 == 0 else range(len(row) - 1, -1, -1)
            for col_index in range_cols:
                item = row[col_index]
                if col_index > self.limit or item <= 0:
                    count = 0
                    continue
                if last_item == item:
                    count = count + 1
                else:
                    count = 0
                    last_item = item
                if item == 200:
                    play_now = self.game.slot_calculator_dia(self.play_pos, col_index, row_index)
                    pyautogui.moveTo(play_now.x, play_now.y)
                    pyautogui.click()
                    pyautogui.moveTo(self.game.box.x, self.game.box.y)
                    pyautogui.click()

                if count >= 4:
                    cols_len = len(range_cols)
                    last_row, last_col = self.get_rel_position(row_index, col_index, -1)
                    if cols_len == last_col:
                        play_now = self.game.slot_calculator_dia(self.play_pos, last_row, last_col)
                        last_row, last_col = self.get_rel_position(last_row, last_col, -1)
                    else:
                        play_now = self.game.slot_calculator_dia(self.play_pos, col_index, row_index)
                    play_last = self.game.slot_calculator_dia(self.play_pos, last_col, last_row)
                    self.game.swap_item(play_now, play_last)
                    combinations = combinations + 1
                    count = 0

        time.sleep(1)
        pyautogui.moveTo(self.game.box.x, self.game.box.y)
        pyautogui.click(clicks = combinations * 3)

    def run_train(self, times = config.TRAIN['times']):
        run_times = 0
        while run_times < times:
            self.game.click_item("buttons/train.png")
            if not self.game.click_item("buttons/train_ticket.png"):
                self.game.init_screen_position()
                self.game.screen_slider(self.game.slot_gap_y*7)
                if not self.click_item("buttons/train_ticket.png"):
                    print("Unable to find the ticket.")
                    break
            time.sleep(2)
            if not self.game.click_item("buttons/train_visit.png"):
                time.sleep(2)
                if not self.game.click_item("buttons/train_visit.png"):
                    print("Unable to find the visit button.")
                    break
            time.sleep(5)
            visit = set()
            finished_flag = False
            for slider_times in range(8):
                for button in self.buttons_list:
                    if button in visit:
                        continue
                    if not self.game.click_item(button, retry = 1):
                        continue
                    visit.add(button)
                    if button == "buttons/train_finish.png":
                        finished_flag = True
                        break
                if finished_flag:
                    break
                self.game.screen_slider(self.game.slot_gap_y*7)
            run_times = run_times + 1
            if finished_flag:
                time.sleep(5)
                continue

            if not self.game.click_item("buttons/train_return.png"):
                print("Unable to find the return button.")
                break
            time.sleep(5)
            
        if run_times == times:
            self.stop_flag = True