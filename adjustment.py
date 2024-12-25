from FMV_handler import FMV_handler as fmv
import cv2
from collections import namedtuple
import config
import pyautogui

position = namedtuple('position', ['x', 'y'])
region = namedtuple('region', ['x', 'y', 'w', 'h'])
size = namedtuple('size', ['w', 'h'])

check_size = size(config.SIZE['item_width'], config.SIZE['item_height'])

def make_rectangle(image, region, color=(255,0,0), thickness=3):
    start = (region.x, region.y)
    end = (region.x + region.w, region.y + region.h)
    cv2.rectangle(image, start, end, color, thickness)
    return image

scna_size = 9
game = fmv(scan_size=scna_size)
print(f"init position: ({game.gift.x}, {game.gift.y})")
light_pos = game.get_item_position(item_name=config.BASIC['init_slot_position'])
game_relative = position(light_pos.x + game.slot_relative_position.x, light_pos.y + game.slot_relative_position.y)
pyautogui.moveTo(game_relative.x, game_relative.y)

light_pos = game.get_item_position(region=game.game_area, item_name=config.BASIC['init_slot_position'])
relative_scan = position(light_pos.x + game.slot_relative_position.x, light_pos.y + game.slot_relative_position.y)
print(f"init scan position: ({relative_scan.x}, {relative_scan.y})")
light_region = game.item_region(light_pos, game.slot_size)
init_region = game.item_region(relative_scan, game.slot_size)
game_image = game.take_screenshot(region=game.game_area)
img = game_image
img = make_rectangle(img, init_region)
img = make_rectangle(img, light_region, color=(0,0,255))
for i in range(17):
    for j in range(9):
        scan_pos = game.slot_calculator(relative_scan, -i, j)
        slot_region = game.item_region(scan_pos, check_size)
        img = make_rectangle(img, slot_region)

game.save_image(img, "buttons")

if config.BASIC['test_init_postion']:
    game.init_screen_position()
    game.screen_slider(game.slot_gap_y*config.SIZE['init_scan_position'])

if config.BASIC['get_farm']:
    game.init_screen_position()
    for i in range(((config.BASIC['farm_size']*9)//5)+1):
        game.screen_slider(game.slot_gap_y*5)
        game_image = game.take_screenshot(region=game.game_area)
        light_pos = game.get_item_position(region=game.game_area, item_name=config.BASIC['init_slot_position'])
        farm_position = game.slot_calculator(light_pos, 0, 5)
        farm_img = game_image[farm_position.y:farm_position.y+80, farm_position.x:farm_position.x+70]
        game.save_image(farm_img, "buttons", "farm_")
