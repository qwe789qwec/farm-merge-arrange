from FMV_arrange import FMV_arrange as fmv_arrange
import config
import pyautogui
import time

arrange = fmv_arrange()

while True:
    if config.BASIC['auto_farm']:
        arrange.scan_slot()
        arrange.print_items()
        if config.BASIC['arrange_method'] == 'cluster':
            arrange.run_arrange2()
        else:
            arrange.run_arrange()
        arrange.print_items()
        
    if arrange.stop_flag:
        print("auto farm stopped")
        break

    if config.BASIC['auto_combine']:
        pyautogui.click(arrange.game.drag.x, arrange.game.drag.y)
        if not arrange.arrange_flag:
            arrange.scan_slot()
        arrange.run_combine2()

    if arrange.stop_flag:
        print("no combine stopped")
        break

    if config.BASIC['auto_combine']:
        if arrange.game.click_item("buttons/item_ticket.png", retry=1):
            pyautogui.moveTo(arrange.game.box.x, arrange.game.box.y)
            pyautogui.click()
            time.sleep(2)

    if config.BASIC['auto_train']:
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