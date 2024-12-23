from FMV_handler import FMV_handler as fmv
import os
import time
import numpy as np
import pyautogui

scna_size = 9
game = fmv(scan_size=scna_size)
game.capture_slot()
items = game.compare_slot_image()

last_i = 0
last_j = 0
limit = 9
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

for row in game.scan_index:
    print(row)

for row in items:
    print(row)

game.init_screen_position()
game.screen_slider(game.slot_gap_y*3)
play_pos = game.get_play_initial_position()
pyautogui.moveTo(play_pos.x, play_pos.y)
time.sleep(5)


for row_index, row in enumerate(items):
    range_cols = range(len(row)) if row_index % 2 == 0 else range(len(row) - 1, -1, -1)
    for col_index in range_cols:
        item = row[col_index]
        if col_index > limit:
            continue
        item_pos = get_position(items, item)
        if len(item_pos) == 1:
            continue
        
        next_row, next_col = get_next_position(row_index, col_index)
        visited.add((row_index, col_index))

        for position in item_pos:
            while items[next_row][next_col] == item:
                visited.add((next_row, next_col))
                next_row, next_col = get_next_position(next_row, next_col)
            play_next = game.slot_calculator(play_pos, next_col, next_row)
            if (position[0], position[1]) not in visited and position[1] < limit:
                from_row, from_col = position[0], position[1]
                print(f"Swapping {from_row}, {from_col} to {next_row}, {next_col}")
                play_from = game.slot_calculator(play_pos, from_col, from_row)
                game.swap_item(play_from, play_next)
                visited.add((next_row, next_col))
                time.sleep(3)
                swap_item = items[from_row][from_col]
                items[from_row][from_col] = items[next_row][next_col]
                items[next_row][next_col] = swap_item
                next_row, next_col = get_next_position(next_row, next_col)