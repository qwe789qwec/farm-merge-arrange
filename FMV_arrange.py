from FMV_handler import FMV_handler as fmv
import os
import time
import numpy as np
import pyautogui

def get_next_position(i, j, height, width):
    if i % 2 == 0:
        if j + 1 < width:
            return i, j + 1
        else:
            return i + 1, j
    else:
        if j - 1 >= 0:
            return i, j - 1
        else:
            return i + 1, j

game = fmv()
size = 9
matrix = game.scan_slot(False)
fullmap = matrix
for i in range(int((size/3)-1)):
    game.scan_go_up()
    matrix = game.scan_slot()
    item = matrix[16, 2]
    fullmap[-1, -1] = item
    fullmap = np.concatenate((fullmap, matrix), axis=1)

print(fullmap)

game.init_play_position()
width , height = fullmap.shape

print(height, width)
print(fullmap[9, 0])
print(fullmap[10, 2])

last_i = 0
last_j = 0
visited = set()
for i in range(height):
    range_cols = range(width) if i % 2 == 0 else range(width - 1, -1, -1)
    for j in range_cols:
        if (i + j) > 16:
            continue
        if fullmap[j, i] == -1:
            continue
        item = fullmap[j, i]
        where = np.where(fullmap == item)
        visited.add((j, i))

        for k in range(len(where[0])):
            next_i, next_j = get_next_position(i, j, height, width)
            if fullmap[next_j, next_i] == item or fullmap[next_j, next_i] == -1:
                visited.add((next_j, next_i))
                continue
            next_x, next_y = game.slot_calculator(game.game_x, game.game_y, next_j, next_i)
            if (where[0][k], where[1][k]) not in visited and (where[0][k] + where[1][k]) < 16:
                from_i = where[0][k]
                from_j = where[1][k]
                from_x, from_y = game.slot_calculator(game.game_x, game.game_y, from_i, from_j)
                game.swap_item(from_x, from_y, next_x, next_y)
                visited.add((next_j, next_i))
                time.sleep(1)
                swap_item = fullmap[from_i, from_j]
                fullmap[from_i, from_j] = fullmap[next_j, next_i]
                fullmap[next_j, next_i] = swap_item
                next_i, next_j = get_next_position(next_i, next_j, height, width)