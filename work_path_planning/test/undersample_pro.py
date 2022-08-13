import numpy as np
import scipy.io as io
import copy
from scipy.io import savemat

# 忽略警告
import warnings
warnings.filterwarnings("ignore")

data = np.load('data_pro.npy')
data_prim = io.loadmat('matlab.mat')['v']

standard_x = 594000
standard_y = 3370000

data_prim[:, 0] = data_prim[:, 0] - standard_x
data_prim[:, 1] = data_prim[:, 1] - standard_y

x_unique = np.unique(data_prim[:, 0])
y_unique = np.unique(data_prim[:, 1])

# padding = np.array([1.0,2.0,3.0]).reshape(1,3)

three_D = []
temp = data[0, 0]
j = 0
for i in range(len(data)):
    if data[i, 0] != temp:
        three_D.append(data[j:i, :].tolist())
        j = i
        temp = data[i, 0]
three_D.append(data[j:i, :].tolist())

miss = []
for i in range(len(three_D)):
    if len(three_D[i]) < 1009:
        miss.append(i)

miss_all = []
for num in miss:
    this_one = three_D[num]
    temp = []
    y_num = 0
    for i in range(len(this_one)):
        # lock = 0
        while this_one[i][1] != y_unique[y_num]:
            temp.append([x_unique[num], y_unique[y_num], np.nanmean(np.array([this_one[i][2], this_one[i-1][2]]))])
            # lock = 1
            y_num += 1
        # if lock == 0:
        y_num += 1
    while y_num != len(three_D[0]):
        temp.append([x_unique[num], y_unique[y_num], np.nanmean(np.array([this_one[i][2], this_one[i-1][2]]))])
        y_num += 1

    this_one.extend(copy.deepcopy(temp))
    this_one.sort()
    miss_all.append(copy.deepcopy(this_one))


for i in reversed(miss):
    del three_D[i]
three_D.extend(copy.deepcopy(miss_all))

three_D = np.array(three_D)
data = np.reshape(three_D, (len(three_D) * len(three_D[0]), 3))
data = np.nan_to_num(data)

np.save('data_under.npy',data)
savemat("data_under.mat", {'v': data})
np.save('three_D.npy',three_D)



