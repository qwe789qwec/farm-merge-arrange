from FMV_arrange import FMV_arrange as fmv_arrange
import config
import pyautogui
import time

arrange = fmv_arrange()

while True:
    if config.BASIC['auto_farm']:
        arrange.scan_slot()
        arrange.print_items()
        arrange.run_arrange2()
        
    if arrange.stop_flag:
        print("auto farm stopped")
        break

    if config.BASIC['auto_combine']:
        if not arrange.arrange_flag:
            arrange.scan_slot()
        arrange.run_combine()

    if arrange.stop_flag:
        print("no combine stopped")
        break

    if config.BASIC['auto_train']:
        if config.BASIC['auto_combine']:
            if arrange.game.click_item("buttons/item_ticket.png"):
                pyautogui.moveTo(arrange.game.box.x, arrange.game.box.y)
                pyautogui.click()
            else:
                arrange.game.init_screen_position()
                arrange.game.screen_slider(arrange.game.slot_gap_y*7)
                if arrange.game.click_item("buttons/item_ticket.png"):
                    pyautogui.moveTo(arrange.game.box.x, arrange.game.box.y)
                    pyautogui.click()
        arrange.run_train()
        if config.BASIC['auto_farm']:
            time.sleep(3)
            pyautogui.moveTo(arrange.game.drag.x, arrange.game.drag.y)
            pyautogui.click()
            time.sleep(3)
            pyautogui.scroll(30, x=None, y=None)
            pyautogui.scroll(-100, x=None, y=None)
            pyautogui.scroll(30, x=None, y=None)
            pyautogui.scroll(-100, x=None, y=None)

    if arrange.stop_flag:
        print("auto train stopped")
        break