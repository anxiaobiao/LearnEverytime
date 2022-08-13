import scipy.io as io
import numpy as np
from scipy.io import savemat
import copy

# 忽略警告
import warnings
warnings.filterwarnings("ignore")

data_prim = io.loadmat('matlab.mat')
# print(data)

data = data_prim['v']
data_prim = data_prim['v']

standard_x = 594000
standard_y = 3370000

# 将横纵坐标降低为顺眼值
data[:, 0] = data[:, 0] - standard_x
data[:, 1] = data[:, 1] - standard_y

# data = data[data[:, 2] > 2000]
# 将低于0高度的值作为0（地面）
for i in range(len(data)):
    if data[i, 2] <= 0:
        data[i, 2] = 0

# 提取出x轴和y轴坐标的所有取值
x_unique = np.unique(data[:, 0])
y_unique = np.unique(data[:, 1])

# 生成采样间隔的全nan数据方阵
data_matrix = np.full((len(x_unique), len(y_unique), 3), np.nan)
k, flag = 0, 0
# 去重，将重复数据使用均值代替
for i in range(len(x_unique)):
    # if flag == 1:
    #     break
    for j in range(len(y_unique)):
        temp = []
        if data_matrix[i, j, 0] != data[k, 0] or data_matrix[i, j, 1] != data[k, 1]:
            data_matrix[i, j, 0] = x_unique[i]
            data_matrix[i, j, 1] = y_unique[j]

        while k < len(data) and data_matrix[i, j, 0] == data[k, 0] and data_matrix[i, j, 1] == data[k, 1]:
            temp.append(data[k, 2])
            k += 1

        data_matrix[i, j, 2] = np.nanmean(np.array(temp))

        # if i == 100 and j == 245:
        #     flag = 1
        #     break

    print(i)

# 将为采样数据使用0（地面）代替，因为nan数据只出现在后63为上，后63大部分为地面
np.nan_to_num(data_matrix)

# 保存数据文件
np.save('../data/Python/data.npy', data_matrix)
res = np.reshape(data_matrix, (len(data_matrix) * len(data_matrix[0]), 3))
savemat("../data/matlab/data.mat", {'v': res})

