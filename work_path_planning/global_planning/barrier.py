import numpy as np
from scipy.io import savemat
import math


# 忽略警告
import warnings
warnings.filterwarnings("ignore")

data = np.load('../data/Python/data.npy')

# 求解超定方程
def super_fun(arr):

    A = np.ones(arr.shape)

    A[:, 0] = arr[:, 0]
    A[:, 1] = arr[:, 1]

    b = arr[:, 2]

    res = np.linalg.inv(A.T @ A) @ A.T @ b

    return res / res[2]

# 小二乘求平面
def leastsq(arr):

    A = np.zeros([3,3])
    b = np.zeros([3,1])

    for i in range(len(arr)):
        temp = np.array([
            [arr[i, 0] ** 2, arr[i, 0] * arr[i, 1], arr[i, 0]],
            [arr[i, 0] * arr[i, 1], arr[i, 1] ** 2, arr[i, 1]],
            [arr[i, 0], arr[i, 1], 1]
        ])

        A += temp

        b += np.array([
            [arr[i, 2] * arr[i, 0]],
            [arr[i, 2] * arr[i, 1]],
            [arr[i, 2]]
        ])

    res = np.linalg.pinv(A) @ b

    return res / res[2]

def judge(arr):

    # vec = super_fun(arr)
    vec = leastsq(arr)
    fun = math.acos(1 / math.sqrt(vec[0] ** 2 + vec[1] ** 2 + 1))
    return abs(fun) > math.pi / 6

barrier, barr_center = [], []
block = 4
for i in range(int(len(data) / block)):
    for j in range(int(len(data[0]) / block)):

        if i == int(len(data) / block) - 1 and j == int(len(data) / block) - 1:
            arr = data[i * block:, j * block:, :]
            arr = np.reshape(arr, (len(arr) * len(arr[0]), 3))
            if judge(arr):
                barrier.append(arr.tolist())
            break

        if i == int(len(data) / block) - 1:
            arr = data[i * block:, j * block:(j + 1) * block, :]
            arr = np.reshape(arr, (len(arr) * len(arr[0]), 3))
            if judge(arr):
                barrier.append(arr.tolist())
            break

        if j == int(len(data) / block) - 1:
            arr = data[i * block:(i+1)*block, j * block:, :]
            arr = np.reshape(arr, (len(arr) * len(arr[0]), 3))
            if judge(arr):
                barrier.append(arr.tolist())
            break

        arr = data[i*block:(i+1)*block, j*block:(j+1)*block, :]
        arr = np.reshape(arr, (len(arr) * len(arr[0]), 3))

        ave = np.average(arr, axis=0)

        if judge(arr):
            barrier.append(arr.tolist())
            barr_center.append([ave[0], ave[1]])
        # for m in range(i * 8, (i + 1) * 8):
        #     for n in range(j * 8, (j + 1) * 8):
        #         temp = [data[m, n, 0], ]

    print(i)

barrier_save = []
for i in range(len(barrier)):
    barrier_save += barrier[i]
barrier_save = np.array(barrier_save)

barr_center = np.array(barr_center)

# barrier = np.reshape(barrier, (len(barrier) * len(barrier[0]), 3))
savemat("../data/matlab/barrier.mat", {'b': barrier_save})
np.save('../data/Python/barrier.npy', barrier_save)
np.save('../data/Python/barr_center.npy', barr_center)
