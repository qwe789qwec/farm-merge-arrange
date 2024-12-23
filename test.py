import numpy as np

# 設定一維陣列
one_d_array = np.arange(9, 54)  # 示例一維陣列
print("Original 1D array:", one_d_array)

# 設定行數
rows = 9

farm_shape1 = [9, 10, 11, 12, 13, 14, 15, 16, 17]

# 動態生成矩陣
matrix = []
current_index = 0
for row_size in farm_shape1:
    if row_size % 2 == 0:
        row = np.arange(current_index, current_index + row_size)
    else:
        row = np.arange(current_index + row_size - 1, current_index - 1, -1)
    matrix.append(row)
    current_index += row_size

# 打印結果
print("\nReshaped matrix:")
for row in matrix:
    print(row)

print(matrix[1][8])
