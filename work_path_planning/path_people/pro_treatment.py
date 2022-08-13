import numpy as np
from scipy.io import savemat
import math


# 忽略警告
import warnings
warnings.filterwarnings("ignore")

data = np.load('../data/Python/data.npy')
# place = data[600:950, 600:950]
place = data[350:650, 400:700]

# 化为2维向量
res = np.reshape(place, (len(place) * len(place[0]), 3))

h_max, h_min = max(res[:, 2]), min(res[:, 2])

zoning = []

while(h_min < h_max):
    temp = res[(res[:, 2] > h_min) * (res[:, 2] < h_min + 10)]
    zoning.append(temp.tolist())
    h_min += 100


# 保存数据
np.save('./data/python/data_ant.npy', zoning)
np.save('./data/python/data.npy', place)
savemat("./data/matlab/data.mat", {'v': res})
