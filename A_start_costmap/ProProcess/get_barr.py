import math
import numpy as np
from scipy.io import savemat
from scipy.optimize import leastsq

# 忽略警告
import warnings
warnings.filterwarnings("ignore")

# 小二乘求平面
def fit_func(p, x, y):
    """ 数据拟合函数 """
    a, b, c = p
    return a * x + b * y + c


def residuals(p, x, y, z):
    """ 误差函数 """
    return z - fit_func(p, x, y)


def estimate_plane_with_leastsq(pts):
    """ 根据最小二乘拟合出平面参数 """
    p0 = np.array([1, 0, 1])
    np_pts = np.array(pts)
    plsq = leastsq(residuals, p0, args=(np_pts[:, 0], np_pts[:, 1], np_pts[:, 2]))
    return plsq[0]

def judge(arr, angle):

    vec = estimate_plane_with_leastsq(arr)
    fun = math.acos(1 / math.sqrt(vec[0] ** 2 + vec[1] ** 2 + 1))
    return abs(fun) > angle

def get_barr(data, angle):
    barrier, barr_center = [], []
    block = 3
    for i in range(int(len(data) / block)):
        for j in range(int(len(data[0]) / block)):

            if i == int(len(data) / block) - 1 and j == int(len(data) / block) - 1:
                arr = data[i * block:, j * block:, :]
                arr = np.reshape(arr, (len(arr) * len(arr[0]), 3))
                if judge(arr, angle):
                    barrier.append(arr.tolist())
                break

            if i == int(len(data) / block) - 1:
                arr = data[i * block:, j * block:(j + 1) * block, :]
                arr = np.reshape(arr, (len(arr) * len(arr[0]), 3))
                if judge(arr, angle):
                    barrier.append(arr.tolist())
                break

            if j == int(len(data) / block) - 1:
                arr = data[i * block:(i+1)*block, j * block:, :]
                arr = np.reshape(arr, (len(arr) * len(arr[0]), 3))
                if judge(arr, angle):
                    barrier.append(arr.tolist())
                break

            arr = data[i*block:(i+1)*block, j*block:(j+1)*block, :]
            arr = np.reshape(arr, (len(arr) * len(arr[0]), 3))

            ave = np.average(arr, axis=0)

            if judge(arr, angle):
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

    return barrier_save, barr_center

def get_barr_slide(data, angle):
    barrier = []
    block = 5
    for i in range(len(data) - block):
        for j in range(len(data[0]) - block):
            arr = data[i:i+block, j:j+block]
            arr = np.reshape(arr, (len(arr) * len(arr[0]), 3))
            if judge(arr, angle):
                barrier.append(arr.tolist())
        print(i)

    barrier = np.array(barrier)
    barrier = np.reshape(barrier, (len(barrier) * len(barrier[0]), 3))
    barrier = np.unique(barrier, axis=0)

    return barrier

if __name__ == '__main__':

    # data = np.load('./data/python/data.npy')
    data = np.load('./data/python/data_moon_1.npy')
    angle = math.pi / 3
    # barrier = np.reshape(barrier, (len(barrier) * len(barrier[0]), 3))

    # barrier_save, barr_center = get_barr(data, angle)
    barrier_save = get_barr_slide(data, angle)

    savemat("./data/matlab/barrier.mat", {'b': barrier_save})
    # np.save('./data/python/barrier.npy', barrier_save)