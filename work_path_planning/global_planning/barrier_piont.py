import numpy as np
from scipy.io import savemat
import math


# 忽略警告
import warnings
warnings.filterwarnings("ignore")

data = np.load('../data/data.npy')

def normal_vectors(v_1, v_2):

    a = v_1[1] * v_2[2] - v_2[1] * v_1[2]
    b = v_1[2] * v_2[0] - v_2[2] * v_1[0]
    c = v_1[0] * v_2[1] - v_2[0] * v_1[1]

    return a/c, b/c

def judge(v_1, v_2):

    a, b = normal_vectors(v_1, v_2)
    fun = math.acos(1 / math.sqrt(a ** 2 + b ** 2 + 1))

    return fun > math.pi / 3

def barrier(point_1, point_2, point_3, point_4):

    v_1 = point_1 - point_2
    v_2 = point_2 - point_3
    v_3 = point_3 - point_4
    v_4 = point_4 - point_1

    num = 0
    num += judge(v_1, v_2)
    num += judge(v_2, v_3)
    num += judge(v_3, v_4)
    num += judge(v_4, v_1)

    return num >= 4

data_matrix = np.zeros([len(data), len(data[0]), 4])

for i in range(len(data)):
    for j in range(len(data[0])):
        data_matrix[i, j, 0] = data[i, j, 0]
        data_matrix[i, j, 1] = data[i, j, 1]
        data_matrix[i, j, 2] = data[i, j, 2]

    print(1, i)

for i in range(len(data) - 1):
    for j in range(len(data[0]) - 1):

        flag = barrier(data[i, j], data[i, j+1], data[i+1, j+1], data[i+1, j])

        if flag:
            data_matrix[i, j, 3] = 1
            data_matrix[i, j+1, 3] = 1
            data_matrix[i+1, j+1, 3] = 1
            data_matrix[i+1, j, 3] = 1

    print(2, i)

barrier_glo = []
for i in range(len(data_matrix)):
    for j in range(len(data_matrix[0])):
        if data_matrix[i, j, 3] == 1:
            barrier_glo.append(data[i, j].tolist())

    print(3, i)

barrier_glo = np.array(barrier_glo)

savemat("../data/barrier_point.mat", {'b': barrier_glo})
savemat("barrier_point.mat", {'b': barrier_glo})
# savemat("../pro_treatment/barrier.mat", {'b': barrier_glo})

