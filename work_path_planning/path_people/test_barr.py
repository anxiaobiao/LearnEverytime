import os
from plyfile import PlyData, PlyElement
import numpy as np
import pandas as pd
from scipy.io import savemat

# 忽略警告
import warnings
warnings.filterwarnings("ignore")

### 定义文件名获取函数
def data_needed(filePath):
    file_name = list()        #新建列表
    for i in os.listdir(filePath):        #获取filePath路径下所有文件名
        data_collect = ''.join(i)        #文件名字符串格式
        file_name.append(data_collect)        #将文件名作为列表元素填入
    print("获取filePath中文件名列表成功")        #打印获取成功提示
    return(file_name)        #返回列表

def read_ply(file_dir):

    # file_dir = 'D:\code\data\some_old\Production_Ply\Data\Tile_+001_+002.ply'  #文件的路径
    plydata = PlyData.read(file_dir)  # 读取文件
    data = plydata.elements[0].data  # 读取数据
    data_pd = pd.DataFrame(data)  # 转换成DataFrame, 因为DataFrame可以解析结构化的数据
    data_np = np.zeros(data_pd.shape, dtype=np.float)  # 初始化储存数据的array
    property_names = data[0].dtype.names  # 读取property的名字
    for i, name in enumerate(property_names):  # 按property读取数据，这样可以保证读出的数据是同样的数据类型。
        data_np[:, i] = data_pd[name]
    data_np = data_np[:, 0:3]
    # data_np = data_np.reshape(len(data_np[0]), 3)
    return data_np.tolist()

def read_all_ply(filePath):
    # file_name = data_needed(filePath)
    file_name = os.listdir(filePath)
    data = []
    for n in file_name:
        temp = read_ply(filePath + '\\' + n)
        data.extend(temp)
    return np.array(data)

def get_grid(data, side_len):

    x_min, x_max, y_min, y_max = min(data[:, 0]), max(data[:, 0]), min(data[:, 1]), max(data[:, 1])
    # x_min, x_max, y_min, y_max = int(x_min - 1), int(x_max + 1), int(y_min - 1), int(y_max + 1)
    x_min, x_max, y_min, y_max = int(x_min), int(x_max), int(y_min), int(y_max)

    data_grid = list()
    for i in np.arange(x_min, x_max, side_len):
        # if i + side_len < min(data[:, 0]) or i - side_len > max(data[:, 0]):
        #     continue
        data_grid_x = list()
        for j in np.arange(y_min, y_max, side_len):
            # if j + side_len < min(data[:, 1]) or j - side_len > max(data[:, 1]):
            #     continue
            temp = data[:, 0] > i
            temp *= data[:, 0] < i + side_len
            temp *= data[:, 1] > j
            temp *= data[:, 1] < j + side_len
            temp = data[temp]
            data_grid_x.append([i + side_len / 2, j + side_len / 2, np.mean(temp[:, 2])])
            print(i, j)
        data_grid.append(data_grid_x)

    return data_grid

def drop_nan(data):
    temp = list()
    for i in range(len(data)):
        if not np.isnan(data[i, 2]):
            a = data[i, 2]
        if np.isnan(data[i, 2]):
            temp.append(i)
        elif len(temp) != 0:
            data[temp] = np.nan_to_num(data[temp], nan=data[i, 2])
            temp = list()
    data[temp] = np.nan_to_num(data[temp], nan=a)   # 如果最后几个为nan，进行这个操作


if __name__ == '__main__':
    # 读取文件
    # filePath = r"D:\code\data\some_old\Production_Ply\Data"        #想要获取文件名的路径
    # data = read_all_ply(filePath)
    data = np.load('./data/python/data_moon.npy')

    # data = get_grid(data, 1)
    # data = np.array(data)

    row, loc = len(data[0]), len(data)
    data = np.reshape(data, (len(data) * len(data[0]), 3))
    drop_nan(data)
    data = np.reshape(data, (loc, row, 3))

    np.save('./data/python/data_moon_1.npy', data)
    data_moon = np.reshape(data, (len(data) * len(data[0]), 3))
    savemat("./data/matlab/data_moon_1.mat", {'v': data_moon})
"""
    np.save('./data/python/data_moon.npy', data)
    data_moon = np.reshape(data, (len(data) * len(data[0]), 3))
    savemat("./data/matlab/data_moon.mat", {'v': data_moon})
"""

