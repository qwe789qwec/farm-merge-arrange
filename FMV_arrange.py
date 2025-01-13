from FMV_handler import FMV_handler as fmv
import config
import time
import pyautogui

start_time = time.time()

scna_size = 9
game = fmv(scan_size=scna_size)
game.capture_slot()
items = game.compare_slot_image()

last_i = 0
last_j = 0
limit = 12
visited = set()

def get_position(matrix, target):
    positions = []

    for row_index, row in enumerate(matrix):
        for col_index, element in enumerate(row):
            if element == target:
                positions.append((row_index, col_index))

    return positions

def get_next_position(x, y):
    index = game.scan_index[x][y]
    next_index = get_position(game.scan_index, index + 1)
    
    return next_index[0][0], next_index[0][1]

def get_last_position(x, y):
    index = game.scan_index[x][y]
    next_index = get_position(game.scan_index, index - 1)
    
    return next_index[0][0], next_index[0][1]

# game.init_screen_position()
game.screen_slider(-game.slot_gap_y*((2.3*2)-1))
play_pos = game.get_play_initial_position()
for row in items:
    print(row)
move_times = 0
last_item = 0
count = 0
for row_index, row in enumerate(items):
    if row_index == 2 or row_index == 3:
        game.screen_slider(game.slot_gap_y)
        play_pos = game.get_play_initial_position()
        limit = limit + 1
    range_cols = range(len(row)) if row_index % 2 == 0 else range(len(row) - 1, -1, -1)
    for col_index in range_cols:
        item = row[col_index]
        if col_index > limit or item <= 0:
            continue
        if last_item != item:
            count = 0
            last_item = item
        item_pos = get_position(items, item)
        if len(item_pos) == 1:
            continue

        next_row, next_col = get_next_position(row_index, col_index)
        visited.add((row_index, col_index))

        for position in item_pos:
            while items[next_row][next_col] == item or items[next_row][next_col] <= 0:
                visited.add((next_row, next_col))
                next_row, next_col = get_next_position(next_row, next_col)
                if items[next_row][next_col] == item:
                    count = count + 1
            if count >= 4:
                break
            play_next = game.slot_calculator_dia(play_pos, next_col, next_row)
            if (position[0], position[1]) not in visited and position[1] < limit:
                from_row, from_col = position[0], position[1]
                play_from = game.slot_calculator_dia(play_pos, from_col, from_row)
                game.swap_item(play_from, play_next)
                count = count + 1
                move_times = move_times + 1
                visited.add((next_row, next_col))
                # time.sleep(3)
                swap_item = items[from_row][from_col]
                items[from_row][from_col] = items[next_row][next_col]
                items[next_row][next_col] = swap_item
                next_row, next_col = get_next_position(next_row, next_col)
            if count >= 4:
                break

if config.BASIC['auto_combine']:
    combinations = 0
    game.screen_slider(-(game.slot_gap_y*2))
    play_pos = game.get_play_initial_position()
    count = 0
    for row_index, row in enumerate(items):
        if row_index == 2 or row_index == 3:
            game.screen_slider(game.slot_gap_y)
            play_pos = game.get_play_initial_position()
            limit = limit + 0.6
        range_cols = range(len(row)) if row_index % 2 == 0 else range(len(row) - 1, -1, -1)
        for col_index in range_cols:
            item = row[col_index]
            if col_index > limit or item <= 0:
                count = 0
                continue
            if last_item == item:
                count = count + 1
            else:
                count = 0
                last_item = item

            if count >= 4:
                last_row, last_col = get_last_position(row_index, col_index)
                play_now = game.slot_calculator_dia(play_pos, col_index, row_index)
                play_last = game.slot_calculator_dia(play_pos, last_col, last_row)
                game.swap_item(play_now, play_last)
                combinations = combinations + 1
                count = 0

    time.sleep(1)
    pyautogui.moveTo(game.box.x, game.box.y)
    pyautogui.click(clicks = combinations * 3)

print(move_times)
for row in items:
    print(row)

end_time = time.time()
execution_time = (end_time - start_time) / 60
print(f"total time: {execution_time:.2f} minutes")