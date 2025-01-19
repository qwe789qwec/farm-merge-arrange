from FMV_handler import FMV_handler as fmv
import config
import time
import numpy as np
import pyautogui

start_time = time.time()

class FMV_arrange:
    def __init__(self, limit = config.BASIC['farm_size']):
        self.game = fmv()
        self.limit = limit
        self.arrange_flag = False
        self.stop_flag = False
        self.buttons_list = ["buttons/train_box.png",
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

    def get_position(self, matrix, row, col):
        positions = []
        target = matrix[row][col]

        for row_index, row in enumerate(matrix):
            for col_index, element in enumerate(row):
                if element == target and (row_index, col_index) != (row, col):
                    positions.append((row_index, col_index))

        return positions
    
    def get_rel_position(self, x, y, rel):
        index = self.scan_index[x][y]
        next_index = self.get_position(self.scan_index, index + rel)
        
        return next_index[0][0], next_index[0][1]
    
    def print_items(self):
        for row in self.items:
            print(row)

    def valid_position(self, row, col):
        # print("check row: ", row, "check col: ", col)
        if row < 0 or row >= len(self.items):
            # print("check row:", row)
            # print("row length:", len(self.items))
            return False
        if col < 0 or col >= len(self.items[row]):
            # print("check col:", col)
            # print("col length:", len(self.items[row]))
            return False
        if (row + col) >= self.limit:
            # print("limit: ", self.limit)
            return False
        if self.items[row][col] == -1:
            # print("row: ", row, "col: ", col,"got -1")
            return False
        # print("item: ", self.items[row][col])
        return True

    def find_connected_elements(self, start_row, start_col):
        target_value = self.items[start_row][start_col]
        visited = set()
        result = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        queue = [(start_row, start_col)]
        visited.add((start_row, start_col))

        while queue:
            current_row, current_col = queue.pop(0)
            result.append((current_row, current_col))

            for dr, dc in directions:
                new_row, new_col = current_row + dr, current_col + dc
                if (self.valid_position(new_row, new_col) and
                    (new_row, new_col) not in visited):
                    if self.items[new_row][new_col] == target_value:
                        queue.append((new_row, new_col))
                        visited.add((new_row, new_col))
        return result

    def run_arrange2(self):
        self.play_pos = self.game.get_play_initial_position()
        directions = [(0, -1), (-1, 0), (1, 0), (0, 1)]
        visited = set()
        self.limit = config.BASIC['farm_size']
        for row_index, row in enumerate(self.items):
            if row_index == 2 or row_index == 3:
                self.game.screen_slider(self.game.slot_gap_y)
                self.play_pos = self.game.get_play_initial_position()
                self.limit = self.limit + 2.5
            for col_index, item in enumerate(row):
                if not self.valid_position(row_index, col_index):
                    continue
                if item <= -2 or (item >= 0 and (item % 5 == 4 or item % 5 == 0)):
                    print("stop item: ", item)
                    self.stop_flag = True
                    break
                item_pos = self.get_position(self.items, row_index, col_index)
                if len(item_pos) == 0:
                    continue

                for position in item_pos:
                    item_row, item_col = position
                    connected_item = self.find_connected_elements(row_index, col_index)
                    for position in connected_item:
                        visited.add(position)
                    if len(connected_item) >= 5:
                        break
                    if not self.valid_position(item_row, item_col):
                        continue
                    if (item_row, item_col) in visited:
                        continue
                    for dr, dc in directions:
                        next_row, next_col = row_index + dr, col_index + dc
                        if not self.valid_position(next_row, next_col):
                            continue
                        if (next_row, next_col) in visited:
                            continue
                        if self.items[next_row][next_col] == item:
                            visited.add((next_row, next_col))
                            continue
                        play_next = self.game.slot_calculator_dia(self.play_pos, next_col, next_row)
                        play_from = self.game.slot_calculator_dia(self.play_pos, item_col, item_row)
                        self.game.swap_item(play_from, play_next)
                        swap_item = self.items[item_row][item_col]
                        self.items[item_row][item_col] = self.items[next_row][next_col]
                        self.items[next_row][next_col] = swap_item
                        visited.add((next_row, next_col))
                        time.sleep(3)
                        break
 
        if not config.BASIC['auto_combine']:
            self.stop_flag = True
            print("no set combine")
        else:
            self.arrange_flag = True
            self.game.rebuild_tempfile()


    
    def run_arrange(self):
        self.game.screen_slider(-self.game.slot_gap_y*((config.SIZE['scan_step']*2)-1))
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
                if item <= -2 or (item >= 0 and (item % 5 == 4 or item % 5 == 0)):
                    print("stop item: ", item)
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

        if not config.BASIC['auto_combine']:
            self.stop_flag = True
            print("no set combine")
        else:
            self.arrange_flag = True
            self.game.rebuild_tempfile()

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
                    if (cols_len-1) == col_index:
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
        if combinations == 0:
            self.stop_flag = True
            print("no combine")

    def run_combine2(self, move = True):
        combinations = 0
        self.play_pos = self.game.get_play_initial_position()
        count = 0
        self.limit = config.BASIC['farm_size']
        visited = set()
        ticket_pos = None
        for row_index, row in enumerate(self.items):
            if move:
                if row_index == 2 or row_index == 3:
                    self.game.screen_slider(self.game.slot_gap_y)
                    self.play_pos = self.game.get_play_initial_position()
                    self.limit = self.limit + 2.5
            for col_index, item in enumerate(row):
                if item == 200:
                    ticket_pos = (row_index, col_index)
                if not self.valid_position(row_index, col_index):
                    continue
                if (row_index, col_index) in visited:
                    continue
                item_pos = self.find_connected_elements(row_index, col_index)
                item_num = len(item_pos)
                if item_num < 4:
                    continue
                for position in item_pos:
                    visited.add(position)
                if item_num == 4:
                    all_item_pos = self.get_position(self.items, row_index, col_index)
                    if len(all_item_pos) > 4:
                        for position in all_item_pos:
                            if position in visited:
                                continue
                            if not self.valid_position(position[0], position[1]):
                                continue
                            visited.add(position)
                            play_other = self.game.slot_calculator_dia(self.play_pos, position[1], position[0])
                            play_first = self.game.slot_calculator_dia(self.play_pos, col_index, row_index)
                            self.game.swap_item(play_other, play_first)
                            combinations = combinations + 3
                            break
                if item_num > 4:
                    if not self.valid_position(item_pos[4][0], item_pos[4][1]):
                        continue
                    play_other = self.game.slot_calculator_dia(self.play_pos, item_pos[4][1], item_pos[4][0])
                    play_first = self.game.slot_calculator_dia(self.play_pos, col_index, row_index)
                    self.game.swap_item(play_other, play_first)
                    combinations = combinations + 3
                if item_num > 5:
                    combinations = combinations + (item_num - 3 + 2)

        if ticket_pos is not None:
            row, col = ticket_pos
            play_now = self.game.slot_calculator_dia(self.play_pos, col, row)
            pyautogui.moveTo(play_now.x, play_now.y)
            pyautogui.click()
            pyautogui.moveTo(self.game.box.x, self.game.box.y)
            pyautogui.click()

        time.sleep(1)
        pyautogui.moveTo(self.game.box.x, self.game.box.y)
        pyautogui.click(clicks = combinations)
        if combinations == 0:
            self.stop_flag = True
            print("no combine")
        return combinations

    def run_train(self, times = config.TRAIN['times']):
        run_times = 0
        time.sleep(5)
        while run_times < times:
            self.game.click_item("buttons/train.png")
            if not self.game.click_item("buttons/train_ticket.png"):
                self.game.init_screen_position()
                self.game.screen_slider(self.game.slot_gap_y*7)
                if not self.game.click_item("buttons/train_ticket.png"):
                    print("Unable to find the ticket.")
                    break
            else:
                print("get ticket")

            time.sleep(3)
            if not self.game.click_item("buttons/train_visit_B.png"):
                time.sleep(2)
                if not self.game.click_item("buttons/train_visit_B.png"):
                    print("Unable to find the visit button.")
                    break
            else:
                print("visiting")
            time.sleep(5)
            visit = set()
            finished_flag = False
            for slider_times in range(9):
                for button in self.buttons_list:
                    if button in visit:
                        continue
                    if not self.game.click_item(button, retry = 0):
                        continue
                    visit.add(button)
                    if button == "buttons/train_finish.png":
                        finished_flag = True
                        print("finished")
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
            else:
                print("returning")

        if run_times >= 3:
            self.stop_flag = True