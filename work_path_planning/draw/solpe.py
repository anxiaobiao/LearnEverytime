import numpy as np
import math

class CalcSolpe:
    def __init__(self, data, block_x, block_y):
        self.data = data
        self.block_x = block_x
        self.block_y = block_y

    def solpe(self, f_x, f_y):
        return math.atan(math.sqrt(f_x ** 2 + f_y ** 2))

    def first(self, i, j):
        f_x = (self.data[i - 1, j] - self.data[i + 1, j]) / 2 * self.block_x
        f_y = (self.data[i, j + 1] - self.data[i, j - 1]) / 2 * self.block_y
        S = self.solpe(f_x, f_y)
        return  S

    def second(self, i, j):
        f_x = (self.data[i - 1, j - 1] - self.data[i - 1, j + 1] + self.data[i, j - 1] - self.data[i, j + 1] +
               self.data[i + 1, j - 1] - self.data[i + 1, j + 1]) / 6 * self.block_x
        f_y = (self.data[i + 1, j + 1] - self.data[i - 1, j + 1] + self.data[i + 1, j] - self.data[i - 1, j] +
               self.data[i + 1, j - 1] - self.data[i - 1, j - 1]) / 6 * self.block_x
        S = self.solpe(f_x, f_y)
        return S

    def third(self, i, j):
        f_x = (self.data[i-1, j-1] - self.data[i-1, j+1] + 2 * (self.data[i, j-1] - self.data[i, j+1]) +
               self.data[i+1, j-1] - self.data[i+1, j+1]) / 8 * self.block_x
        f_y = (self.data[i+1, j+1] - self.data[i-1, j+1] + 2 * (self.data[i+1, j] - self.data[i-1, j]) +
               self.data[i+1, j-1] - self.data[i-1, j-1]) / 8 * self.block_x
        S = self.solpe(f_x, f_y)
        return S

    def fourth(self, i, j):
        f_x = (self.data[i-1, j-1] - self.data[i-1, j+1] + math.sqrt(2) * (self.data[i, j-1] - self.data[i, j+1]) +
               self.data[i+1, j-1] - self.data[i+1, j+1]) / (4 + 2 * math.sqrt(2) * self.block_x)
        f_y = (self.data[i+1, j+1] - self.data[i-1, j+1] + math.sqrt(2) * (self.data[i+1, j] - self.data[i-1, j]) +
               self.data[i+1, j-1] - self.data[i-1, j-1]) / (4 + 2 * math.sqrt(2) * self.block_x)
        S = self.solpe(f_x, f_y)
        return S

    def fifth(self, i, j):
        f_x = (self.data[i - 1, j - 1] - self.data[i - 1, j + 1] + self.data[i + 1, j - 1] - self.data[i + 1, j + 1]) / 4 * self.block_x
        f_y = (self.data[i + 1, j + 1] - self.data[i - 1, j + 1] + self.data[i + 1, j - 1] - self.data[i - 1, j - 1]) / 4 * self.block_x
        S = self.solpe(f_x, f_y)
        return  S

    def sixth(self, i, j):
        f_x = (self.data[i, j] - self.data[i, j + 1]) / self.block_x
        f_y = (self.data[i, j] - self.data[i - 1, j]) / self.block_y
        S = self.solpe(f_x, f_y)
        return  S


def get_slide(data, type_solpe):
    data_teans = data[:, :, 2]
    calcsolpe = CalcSolpe(data_teans, 1, 1)
    barr = np.full((len(data), len(data[0])), np.nan)
    for i in range(1, len(data)-1):
        for j in range(1, len(data[0])-1):
            S = getattr(calcsolpe, type_solpe)(i, j)   # 获得的为角度值
            if S > 1:
                barr[i, j] = 200
            else:
                barr[i, j] = int(S * 100)
            # barr[i, j] = int(S * 100)

    return barr

def get_barr(data, barr):
    res = np.zeros((len(data), len(data[0]), 4))

    res[:, :, 0] = data[:, :, 0]
    res[:, :, 1] = data[:, :, 1]
    res[:, :, 2] = data[:, :, 2]
    res[:, :, 3] = barr

    # res = get_barr_slide(res)

    return res

def get_barr_slide(data):
    block = 3
    for i in range(len(data) - block):
        for j in range(len(data[0]) - block):
            arr = data[i:i + block, j:j + block]
            temp = sum(arr[:, :, 3].flatten() == 200)
            # temp += sum(arr[:, :, 3].flatten() == 255)
            if temp == 8:
                data[i:i + block, j:j + block, 3] = 200

    return data

def flip90_left(arr):
    new_arr = np.transpose(arr)
    new_arr = new_arr[::-1]
    return new_arr


if __name__ == '__main__':
    data = np.load('../data/python/data_moon_1.npy')

    # barr = list()
    list_solpe = ['first', 'second', 'third', 'fourth', 'fifth', 'sixth']
    for i in list_solpe:
        temp = get_slide(data, i)
        temp[np.isnan(temp)] = 255
        temp = temp.astype(np.int16)
        globals()[i] = temp

        barr = get_barr(data, globals()[i])
        barr = np.reshape(barr, (len(barr) * len(barr[0]), 4))

        np.savetxt(r'D:\code\path_planning\path_people\optimize\solpe\{}.txt'.format(i), barr, fmt='%.5f')
        # np.savetxt(r'D:\code\path_planning\path_people\optimize\solpe\{}_barr.txt'.format(i), barr[(barr[:, 3] == 200) + (barr[:, 3] == 255)], fmt='%.5f')
        barr = barr[(barr[:, 3] == 200) + (barr[:, 3] == 255)]
        barr[:, 2] = barr[:, 3]
        barr = np.delete(barr, -1, axis=1)
        barr[:, 0], barr[:, 1] = barr[:, 0] + 200, barr[:, 1] + 200

        np.savetxt(r'D:\code\path_planning\path_people\optimize\solpe\{}_barr.txt'.format(i),barr , fmt='%3d')

    globals()[list_solpe[1]] = flip90_left(globals()[list_solpe[1]])
    np.savetxt(r'D:\code\path_planning\path_people\data\second.txt', globals()[list_solpe[1]], fmt='%3d')

    # del i, list_solpe, temp




    # barr = np.array(barr)