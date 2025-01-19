from FMV_arrange import FMV_arrange as fmv_arrange
import config
import pyautogui
import time

arrange = fmv_arrange()

while True:


    if config.BASIC['auto_farm']:
        arrange.game.init_screen_position()
        if arrange.game.click_item("buttons/item_ticket.png", retry=1):
            pyautogui.moveTo(arrange.game.box.x, arrange.game.box.y)
            pyautogui.click()
            time.sleep(1)
        arrange.game.screen_slider(arrange.game.slot_gap_y*config.SIZE['init_scan_position'])
        arrange.scan_slot()
        arrange.print_items()
        arrange.game.screen_slider(-arrange.game.slot_gap_y*((config.SIZE['scan_step']*2)-1))
        # if config.BASIC['auto_combine']:
        #     if arrange.run_combine2(move = False) > 0:
        #         arrange.game.rebuild_tempfile()
        #         continue
        #     arrange.stop_flag = False
        # arrange.game.screen_slider(arrange.game.slot_gap_y)
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
        arrange.game.screen_slider(-(arrange.game.slot_gap_y*2))
        arrange.run_combine2()

    if arrange.stop_flag:
        print("no combine stopped")
        break

    if config.BASIC['auto_combine']:
        time.sleep(2)
        if arrange.game.click_item("buttons/item_ticket.png", retry=1):
            pyautogui.moveTo(arrange.game.box.x, arrange.game.box.y)
            pyautogui.click()
            time.sleep(1)

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