import threading
import sys
import config
import pyautogui
import time
from FMV_handler import FMV_handler as fmv

game = fmv(scan_size=9)

def check_exit():
    while True:
        user_input = input("press 0 to exit：")
        if user_input == "0":
            print("get key zero...")
            sys.exit()

thread = threading.Thread(target=check_exit, daemon=True)
thread.start()

times = 0
while times < config.TRAIN['times']:
    times += 1
    print("start...")
    game.init_screen_position()
    game.screen_slider(game.slot_gap_y*7)
    time.sleep(1)
    ticket_pos = game.get_item_position(item_name="buttons/train_ticket.png")
    pyautogui.moveTo(ticket_pos.x, ticket_pos.y)
    pyautogui.click()
    time.sleep(1)
    visit_pos = game.get_item_position(item_name="buttons/train_visit.png")
    pyautogui.moveTo(visit_pos.x, visit_pos.y)
    pyautogui.click()
    time.sleep(5)
    buttons_list = ["buttons/train_gift.png",
                 "buttons/train_coin.png",
                 "buttons/train_water.png",
                 "buttons/train_heart.png",
                 "buttons/train_power.png",
                 "buttons/train_finish.png",]
    visit = set()
    finished_flag = False
    for slider_times in range(9):
        for button in buttons_list:
            if button in visit:
                continue
            button_pos = game.get_item_position(item_name=button, retries=0)
            if button_pos.x is None:
                # print(f"Unable to find the {button}.")
                continue
            visit.add(button)
            pyautogui.moveTo(button_pos.x, button_pos.y)
            pyautogui.click()
            time.sleep(0.3)
            if button == "buttons/train_finish.png":
                finished_flag = True
                break
        if finished_flag:
            break
        game.screen_slider(game.slot_gap_y*7)
            
    if finished_flag:
        time.sleep(5)
        continue
    
    return_pos = game.get_item_position(item_name="buttons/train_return.png")
    pyautogui.moveTo(return_pos.x, return_pos.y)
    pyautogui.click()
    time.sleep(5)