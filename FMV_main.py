from FMV_arrange import FMV_arrange as fmv_arrange
import config

arrange = fmv_arrange()

while True:
    if config.BASIC['auto_farm']:
        arrange.scan_slot()
        arrange.run_arrange()
        
    if arrange.stop_flag:
        break

    if config.BASIC['auto_combine']:
        if not arrange.arrange_flag:
            arrange.scan_slot()
        arrange.run_combine()

    if config.BASIC['auto_train']:
        arrange.run_train()

    if arrange.stop_flag:
        break