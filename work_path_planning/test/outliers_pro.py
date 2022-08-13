import numpy as np
import scipy.io as io
import copy
from scipy.io import savemat
import pandas as pd

# 忽略警告
import warnings

warnings.filterwarnings("ignore")

three_D = np.load('three_D.npy')


# 2σ原则检测异常值
def three_sigma(ser1):
    mean_value = np.nanmean(ser1)  # 求平均值

    rule = False
    if ser1[4] < mean_value - 10 or ser1[4] > mean_value + 10:
        rule = True
    if ser1[4] is np.nan and not(mean_value is np.nan):
        rule = True
    # std_value = np.nanstd(ser1)  # 求标准差
    # rule = ((mean_value - std_value > ser1[4]) or (ser1.mean() + ser1.std() < ser1[4]))
    # 位于（u-3std,u+3std）区间的数据是正常的，不在这个区间的数据为异常的
    # 一旦发现有异常值，就标注为True，否则标注为False
    # index = np.arange(ser1.shape[0])[rule]  # 返回异常值的位置索引
    # outrange = ser1.iloc[index]  # 获取异常数据
    return rule


for i in range(1, len(three_D) - 1):
    for j in range(1, len(three_D[0]) - 1):
        temp = []
        temp.append(three_D[i - 1, j - 1, 2])
        temp.append(three_D[i - 1, j, 2])
        temp.append(three_D[i - 1, j + 1, 2])
        temp.append(three_D[i, j - 1, 2])
        temp.append(three_D[i, j, 2])
        temp.append(three_D[i, j + 1, 2])
        temp.append(three_D[i + 1, j - 1, 2])
        temp.append(three_D[i + 1, j, 2])
        temp.append(three_D[i + 1, j + 1, 2])
        temp = np.array(temp)

        flag = three_sigma(temp)

        if flag:
            # print(flag)
            three_D[i, j, 2] = np.nanmean(temp)

    print(i)


data = np.reshape(three_D, (len(three_D) * len(three_D[0]), 3))

np.save('data.npy',data)
savemat("data.mat", {'v': data})
# np.save('three_D.npy',three_D)
