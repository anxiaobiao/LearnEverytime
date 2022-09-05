import numpy as np
from scipy.io import savemat

def splic(data, barr, world):
    x_min, x_max, y_min, y_max = min(data[:, 0]), max(data[:, 0]), min(data[:, 1]), max(data[:, 1])
    x_side, y_side = x_max - x_min + 1, y_max - y_min + 1

    add_x, add_y = np.zeros((len(data), 3)), np.zeros((len(data), 3))
    add_x[:, [0]], add_y[:, [1]] = x_side, y_side

    data_1 = data
    data_2 = data + add_x
    data_3 = data + add_y
    data_4 = data + add_x + add_y

    data_splic = np.vstack((data_1, data_2))
    data_splic = np.vstack((data_splic, data_3))
    data_splic = np.vstack((data_splic, data_4))

    add_x, add_y = np.zeros((len(barr), 3)), np.zeros((len(barr), 3))
    add_x[:, [0]], add_y[:, [1]] = x_side, y_side
    barr_1 = barr
    barr_2 = barr + add_x
    barr_3 = barr + add_y
    barr_4 = barr + add_x + add_y

    barr_splic = np.vstack((barr_1, barr_2))
    barr_splic = np.vstack((barr_splic, barr_3))
    barr_splic = np.vstack((barr_splic, barr_4))

    add_x, add_y = np.zeros((len(world), 3)), np.zeros((len(world), 3))
    add_x[:, [0]], add_y[:, [1]] = x_side, y_side
    world_1 = world
    world_2 = world + add_x
    world_3 = world + add_y
    world_4 = world + add_x + add_y

    world_splic = np.vstack((world_1, world_2))
    world_splic = np.vstack((world_splic, world_3))
    world_splic = np.vstack((world_splic, world_4))

    world_splic = del_repeat(world_splic)

    return data_splic, barr_splic, world_splic

def del_repeat(world):
    start_x, end_x, start_y, end_y = min(world[:, 0]), max(world[:, 0]), min(world[:, 1]), max(world[:, 1])
    res_1 = list()

    # X轴
    for i in np.arange(start_x, end_x+1, 1.0):
        temp = world[:, 0] == i
        select = world[temp]
        if len(select) == 4:
            temp = repeat(select)
            res_1.extend(temp.tolist())
            # print('2')
        else:
            res_1.extend(select.tolist())

    res_1 = np.array(res_1)
    res = list()
    # Y轴
    for i in np.arange(start_y, end_y+1, 1.0):
        temp = res_1[:, 1] == i
        select = res_1[temp]
        if len(select) == 4:
            temp = repeat(select)
            res.extend(temp.tolist())
            # print('1')
        else:
            res.extend(select.tolist())

    res = np.array(res)
    return res

def repeat(arr):
    for i in range(len(arr)):
        for j in range(len(arr)):
            x, y = arr[i, 0] - arr[j, 0], arr[i, 1] - arr[j, 1]
            if abs(x + y) == 1:
                break
        if abs(x + y) == 1:
            break

    res = np.delete(arr, [i, j], 0)
    return res




if __name__ == '__main__':
    data = np.loadtxt(r'D:\code\path_planning\path_people\txt\data.txt')
    barr = np.loadtxt(r'D:\code\path_planning\path_people\txt\barrier.txt')
    world = np.loadtxt(r'D:\code\path_planning\path_people\txt\world.txt')


    data_splic, barr_splic, world_splic = splic(data, barr, world)

    savemat("../data/matlab/data_moon_2.mat", {'v': data_splic})
    savemat("../data/matlab/world_2.mat", {'w': world_splic})
    savemat("../data/matlab/barr_2.mat", {'b': barr_splic})

    np.savetxt('data.txt', data_splic, fmt='%.5f')
    np.savetxt('barr.txt', barr_splic, fmt='%.5f')
    np.savetxt('world.txt', world_splic, fmt='%.5f')