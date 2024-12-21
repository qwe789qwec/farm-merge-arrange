from FMV_handler import FMV_handler as fmv
import os
import time

game = fmv()
# game.init_screen_position()
# time.sleep(1)
# game.scan_go_up()
# time.sleep(1)
# game.scan_go_up()
# time.sleep(1)

game.init_play_position()
game.play_go_up()
time.sleep(1)