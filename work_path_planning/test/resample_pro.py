import scipy.io as io
import numpy as np
from scipy.io import savemat

# 忽略警告
import warnings
warnings.filterwarnings("ignore")

data_prim = io.loadmat('matlab.mat')
# print(data)

data = data_prim['v']
data_prim = data_prim['v']

standard_x = 594000
standard_y = 3370000

data[:, 0] = data[:, 0] - standard_x
data[:, 1] = data[:, 1] - standard_y

# data = data[data[:, 2] > 2000]

for i in range(len(data)):
    if data[i, 2] <= 0:
        data[i, 2] = np.nan

data_matrix = data[0, :].reshape(1, 3)
for i in range(1, len(data)):
    if data_matrix[len(data_matrix)-1, 0] == data[i, 0] and data_matrix[len(data_matrix)-1, 1] == data[i, 1]:
        for j in range(i-1, len(data)-1):
            if data[j, 1] != data[j+1, 1]:
                break
        data_matrix[len(data_matrix)-1, 2] = np.nanmean(data[i-1:j-1, 2])
        i = j
    else:
        data_matrix = np.row_stack((data_matrix, data[i]))

    if i % 10000 == 0:
        print(i)

x_unique = np.unique(data_matrix[:, 0])
y_unique = np.unique(data_matrix[:, 1])






np.save('data_pro.npy',data_matrix)
savemat("data_pro.mat", {'v': data_matrix})

# data = np.nan_to_num(data_matrix)
# savemat("temp.mat", {'v': data})

