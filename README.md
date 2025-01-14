# FMV Farm Merge Valley auto arrange Guide
Currently still in testing. This is the test [video](https://www.youtube.com/watch?v=c2oZA5ccOqs).  
This guide provides instructions on how to set up and troubleshoot the FMV_arrange.py script. Follow the steps below to ensure proper functionality.
## Installation and Initial Setup
1. Use a computer to install Python and OpenCV.
   * If there are any uninstalled you can refer to `requirements.txt`
2. Run the `FMV_arrange.py` directly.  
If the script does not work as expected, proceed to the adjustment steps below.
## Note
1. Only the first farm is being sorted.
2. Because the sorting algorithm is based on the swap, it is recommended that both the first and second farms be full, otherwise the objects will be unpredictable.
3. It is recommended to play the game in single player, otherwise the player joining window may be clicked.
## Adjustment Steps
1. Run the `adjustment.py`.
2. If the program displays "Failed to get window position.", manually update the gift_button.png image:
   * Replace the existing image in the `buttons` folder with your updated version.
   * Alternatively, place your custom image in the `buttons` folder and update the `scan_screen` setting in `config.py` to match the new image's name.
3. If the game screen is successfully captured, check the `buttons` folder for images similar to `example.png`.
4. Adjust the `slant_distance` and `vertical_distance` values in the `config.py` to ensure the item fits within the rectangle like the `example.png`.
7. Once all adjustments are complete, re-run `FMV_arrange.py` to verify functionality.
## Troubleshooting
1. Ensure the game screen is displayed in the foreground; otherwise, the program may fail to capture it.
2. Windows may have some extra slide, try to change the `slide_speed` in `config.py` to fix it.
3. Additional issues may still occur. Please report any problems you encounter.

## beta function
* You can change the `scan_method` to cluster, it can be sort for anything but by test is not robust.

Follow these steps carefully to ensure a smooth setup and operation. If you have any questions or need further assistance, don’t hesitate to reach out!

## 如何安裝
1. 請先下載並安裝python.
2. 可略過本步驟，但是建議依照以下步驟建立環境。
   ```
   python3 -m venv FMV
   source myenv/bin/activate
   ```
4. 安裝依賴項
   ```
   pip install -r requirements.txt
   ```
6. 安裝完之後建議執行調整步驟
## 注意事項
1. 目前只針對第一塊農場做排序
2. 因為排序演算法是基於互換原則，所以建議第一第二區都要是滿的，不然物件會亂跑。
3. 建議單人遊戲遊玩，不然玩家加入視窗可能會點到。
4. 自動合成目前並不完善，可能沒辦法總是5和2。
5. 目前對 2k 和 4k 的畫面測試不足可能會有未知的問題。
## 調整步驟
1. 運行調整腳本
   ```
   python adjustment.py
   ```
2. 如果程式顯示「`game not found check the screen_ref or dictionary image`」，請手動更新 `buttons/dictionary.png` 與 `buttons/screen_ref.png` 圖片：
   * 將更新後的圖片替換至 `buttons` 資料夾中覆蓋原文件。
   * 或者將自定義圖片放入 `buttons` 資料夾，並在 `config.py` 中將 `scan_screen` 設置為新圖片的名稱。
3. 如果成功擷取畫面會出現 `game_area_x.png` 這是程式的掃描範圍
   * 可以透過調整 `config.py` 文件中的參數改變掃描範圍。
   * `game_x` 與 `game_y` 是起始位置也就是圖片左上角的位置。
   * `game_width` 與 `game_height` 是掃描的範圍大小。
4. 如果程式顯示「`slot not found check the slot_ref image`」，請手動更新 `buttons/farm_1.png` 圖片，替換方式同步驟 2。
5. 如果成功掃描畫面會出現 `game_scan_x.png` 這是程式的掃描位置
   * 可以透過調整 `config.py` 文件中的參數改變掃描位置。
   * `slant_distance` 是每個物件的斜角距離。
   * `vertical_distance` 是每個物件的垂直距離。
   * 調整結果可以參考 `example.png`。
6. 在 `config.py` 內可以設定功能
   * `auto_farm` 自動農場整理。
   * `auto_combine` 自動物件合成(建議搭配自動整理)。
   * `auto_train`  自動火車。
7. 完成所有調整後，運行主程式
   ```
   python FMV_main.py
   ```
## 疑難排解
1. 確保遊戲畫面顯示在最前方，否則程式可能無法捕捉畫面。
2. Windows 可能會有多餘的螢幕滑動，建議的 `config.py` 修正。
   * `drag_fix` 建議設定0.01以上。
   * `mouse_speed` 建議設定6以上。
   * 以上可以自行調整測試自己最適合的速度
3. 可能仍會遇到其他問題，可以跟我回報您遇到的問題。

請仔細按照這些步驟操作，以確保順利完成設定和使用。如果有任何疑問或需要進一步的幫助，請隨時與我聯繫！
