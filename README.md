# FMV Farm Merge Valley auto arrange Guide
Currently still in testing. This is the test [video](https://www.youtube.com/watch?v=c2oZA5ccOqs).  
This guide provides instructions on how to set up and troubleshoot the FMV_arrange.py script. Follow the steps below to ensure proper functionality.
## Installation and Initial Setup
1. Download and Install [python](https://www.python.org/)
2. Create a Virtual Environment (Optional but Recommended):
   ```
   python3 -m venv FMV
   source FMV/bin/activate
   ```
3. Install Dependencies:
   ```
   pip install -r requirements.txt
   ```
4. After installation, please follow the adjustment steps.
## Note
1. Only the first farm is being sorted.
2. Because the sorting algorithm is based on the swap, it is recommended that both the first and second farms be full, otherwise the objects will be unpredictable.
3. It is recommended to play the game in single player, otherwise the player joining window may be clicked.
4. The auto-combine is still under development and may not always achieve 5 combine.
5. Limited testing has been conducted for 2K and 4K displays, so issues may arise.
6. Mouse over the bottom right corner of the screen during program execution to force an end to the program.
## Adjustment Steps
1. Run the adjustment script:
   ```
   python adjustment.py
   ```
3. If the program displays "`game not found check the screen_ref or dictionary image`", manually update the `buttons/dictionary.png` and `buttons/screen_ref.png` image:
   * Replace the existing image in the `buttons` folder with your updated version.
   * Alternatively, place your custom image in the `buttons` folder and update the `game_capture` and `screen_ref` setting in `config.py` to match the new image's name.
4. After successfully capturing the screen, the program will generate `game_area_x.png`, indicating the scanning area.
   * Modify the following parameters in `config.py` to adjust the scanning range
   * `game_x` and `game_y`: Coordinates of the top-left corner of the scanning area.
   * `game_width` and `game_height`: Width and height of the scanning area.
4. If the program displays "`slot not found check the slot_ref image`", update `buttons/farm_1.png`, follow the same replacement process as in Step 2.
   * Modify the following parameters in `config.py` to adjust the scanning range
   * `slant_distance`: slant distance between objects。
   * `vertical_distance`: Vertical distance between objects.
   * Refer to `example.png` for verification.
5. Configure Features in `config.py`
   * `auto_farm`: Automatically arrange the farm.
   * `auto_combine`: Automatically combines objects (recommended to using with auto_farm).
   * `auto_train`: Automatically run train.
7. After completing all adjustments, run the main program:
   ```
   python FMV_main.py
   ```
## Troubleshooting
1. Ensure the game screen is displayed in the foreground; otherwise, the program may fail to capture it.
2. Windows may have some extra slide, try to modify `config.py` to fix it.
   * `drag_fix` Recommended to set it to 0.01 or higher.
   * `mouse_speed` Recommended to set it to 6 or higher.
   * You can adjust the above parameters and test your own optimal speed.
3. Additional issues may still occur. Please report any problems you encounter.

Follow these steps carefully to ensure a smooth setup and operation. If you have any questions or need further assistance, don’t hesitate to reach out!

## 如何安裝
1. 請先下載並安裝 [python](https://www.python.org/)
2. 建立虛擬環境（可選但建議）:
   ```
   python3 -m venv FMV
   source FMV/bin/activate
   ```
3. 安裝依賴項:
   ```
   pip install -r requirements.txt
   ```
4. 安裝完之後請執行調整步驟
## 注意事項
1. 目前只針對第一塊農場做排序
2. 因為排序演算法是基於互換原則，所以建議第一第二區都要是滿的，不然物件會亂跑。
3. 建議單人遊戲遊玩，不然玩家加入視窗可能會點到。
4. 自動合成目前並不完善，可能沒辦法總是5和2。
5. 目前對 2k 和 4k 的畫面測試不足可能會有未知的問題。
6. 在程式執行中將滑鼠移至螢幕右下角強制結束運行。
## 調整步驟
1. 運行調整腳本:
   ```
   python adjustment.py
   ```
2. 如果程式顯示「`game not found check the screen_ref or dictionary image`」，請手動更新 `buttons/dictionary.png` 與 `buttons/screen_ref.png` 圖片：
   * 將更新後的圖片替換至 `buttons` 資料夾中覆蓋原文件。
   * 或者將自定義圖片放入 `buttons` 資料夾，並在 `config.py` 中將 `game_capture` 與 `screen_ref` 設置為新圖片的名稱。
3. 如果成功擷取畫面會出現 `game_area_x.png` 這是程式的掃描範圍
   * 可以透過調整 `config.py` 文件中的參數改變掃描範圍。
   * `game_x` 與 `game_y`: 起始位置也就是圖片左上角的位置。
   * `game_width` 與 `game_height`: 掃描的範圍大小。
4. 如果程式顯示「`slot not found check the slot_ref image`」，請手動更新 `buttons/farm_1.png` 圖片，替換方式同步驟 2。
5. 如果成功掃描畫面會出現 `game_scan_x.png` 這是程式的掃描位置
   * 可以透過調整 `config.py` 文件中的參數改變掃描位置。
   * `slant_distance`: 物件的斜角距離。
   * `vertical_distance`: 物件的垂直距離。
   * 調整結果可以參考 `example.png`。
6. 在 `config.py` 內可以設定功能
   * `auto_farm`: 自動農場整理。
   * `auto_combine`: 自動物件合成(建議搭配自動整理)。
   * `auto_train`: 自動火車。
7. 完成所有調整後，運行主程式:
   ```
   python FMV_main.py
   ```
## 疑難排解
1. 確保遊戲畫面顯示在最前方，否則程式可能無法捕捉畫面。
2. Windows 可能會有多餘的螢幕滑動，建議的 `config.py` 修正。
   * `drag_fix` 建議設定0.01以上。
   * `mouse_speed` 建議設定6以上。
   * 可以自行調整以上參數並測試自己最適合的速度
3. 可能仍會遇到其他問題，可以跟我回報您遇到的問題。

請仔細按照這些步驟操作，以確保順利完成設定和使用。如果有任何疑問或需要進一步的幫助，請隨時與我聯繫！
