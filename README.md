# FMV Farm Merge Valley auto arrange Guide
Currently still in testing. This is the test [video](https://www.youtube.com/watch?v=LEYuK1p1jNw).  
This guide provides instructions on how to set up and troubleshoot the FMV_arrange.py script. Follow the steps below to ensure proper functionality.
## Installation and Initial Setup
1. Use a computer to install Python and OpenCV.
2. Run the `FMV_arrange.py` directly.
If the script does not work as expected, proceed to the adjustment steps below.
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
2. Additional issues may still occur. Please report any problems you encounter.

Follow these steps carefully to ensure a smooth setup and operation. If you have any questions or need further assistance, don’t hesitate to reach out!

## 如何安裝
1. 你的電腦必須安裝 python 和 OpenCV.
2. 然後直接執行`FMV_arrange.py`
如果無法執行可以試試按照下面的調整步驟。
或可能是某些插件沒安裝，就debug看看吧,之後在上requirement。
## 調整步驟
1. 運行 `adjustment.py`。
2. 如果程式顯示「無法獲取視窗位置 (Failed to get window position.)」，請手動更新 `gift_button.png` 圖片：
   * 將更新後的圖片替換至 buttons 資料夾中覆蓋原文件。
   * 或者將自定義圖片放入 buttons 資料夾，並在 config.py 中將 scan_screen 設置為新圖片的名稱。
3. 如果成功截取遊戲畫面，請檢查 buttons 資料夾中是否有類似於 `example.png` 的圖片。
4. 調整 `config.py` 中的 `slant_distance` 和 `vertical_distance` 值，以確保物品位於顯示的矩形內例如`example.png`。
5. 完成所有調整後，重新運行 FMV_arrange.py 以驗證功能。
## 疑難排解
1. 確保遊戲畫面顯示在最前方，否則程式可能無法捕捉畫面。
2. 可能仍會遇到其他問題，可以跟我回報您遇到的問題。

請仔細按照這些步驟操作，以確保順利完成設定和使用。如果有任何疑問或需要進一步的幫助，請隨時與我聯繫！
