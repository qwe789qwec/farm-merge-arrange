import numpy as np

# 建立一個測試矩陣
matrix = np.array([
    [1,  2,  3,  4],
    [5,  6,  7,  8],
    [9, 10, 11, 12],
    [13, 14, 15, 16]
])

# 蛇行遍歷
rows, cols = matrix.shape  # 取得矩陣大小
result = []

rows, cols = matrix.shape
for i in range(rows):
    # 確定當前行的遍歷方向
    range_cols = range(cols) if i % 2 == 0 else range(cols - 1, -1, -1)
    for j in range_cols:
        item = matrix[i, j]
        print(f"({i}, {j}): {item}")
