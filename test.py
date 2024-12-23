def diagonal_snake_traverse(matrix):
    rows, cols = len(matrix), len(matrix[0])
    result = []

    for d in range(rows + cols - 1):
        if d % 2 == 0:
            # 偶數對角線：從下到上
            i = min(d, rows - 1)
            j = d - i
            while i >= 0 and j < cols:
                result.append(matrix[i][j])
                i -= 1
                j += 1
        else:
            # 奇數對角線：從上到下
            j = min(d, cols - 1)
            i = d - j
            while j >= 0 and i < rows:
                result.append(matrix[i][j])
                i += 1
                j -= 1

    return result

# 示例矩陣
matrix = [
    [1, 2, 3, 4],
    [5, 6, 7, 8],
    [9, 10, 11, 12],
    [13, 14, 15, 16]
]

traversal_result = diagonal_snake_traverse(matrix)

print("斜著蛇行的遍歷結果:")
print(traversal_result)

import numpy as np

# 設定起始值和行數
start_value = 9
rows = 9

# 動態生成矩陣
matrix = []
current_value = start_value
for i in range(rows):
    row_length = i + 9
    row = np.arange(current_value, current_value + row_length)
    matrix.append(row)
    current_value += row_length

# 打印矩陣
for row in matrix:
    print(row)

print(matrix[1][11])
