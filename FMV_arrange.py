from FMV_handler import FMV_handler as fmv
import os
import time
import numpy as np
import pyautogui

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

new_matrix, swaps = game.rearrange_and_track_swaps(fullmap)
print(new_matrix)
print(swaps)
for original_pos, new_pos in swaps:
    if (original_pos[0] + original_pos[1] + 1 > 16) or (new_pos[0] + new_pos[1] + 1 > 16):
        continue
    else:
        from_x, from_y = game.slot_calculator(game.game_x, game.game_y, original_pos[0], original_pos[1])
        to_x, to_y = game.slot_calculator(game.game_x, game.game_y, new_pos[0], new_pos[1])
        # pyautogui.moveTo(from_x, from_y)
        # pyautogui.moveTo(to_x, to_y)
        game.swap_item(from_x, from_y, to_x, to_y)
        time.sleep(3)