import numpy as np
from scipy import spatial
import math
from scipy.io import savemat

# 忽略警告
import warnings
warnings.filterwarnings("ignore")

class ACA_TSP:
    def __init__(self, func, n_dim, start, end, start_layer, end_layer, size_pop=10, max_iter=20, distance_matrix=None, alpha=10, beta=1, gamma=3.5, nu=6, rho=0.4):
        self.func = func
        self.n_dim = n_dim  # 城市数量，每一次表示选取一个城市，所以是层数的数量。是一个2D-array，具有每一层的点数
        self.size_pop = size_pop  # 蚂蚁数量
        self.max_iter = max_iter  # 迭代次数
        self.alpha = alpha # 信息素重要程度
        self.beta = beta   # 适应度的重要程度
        self.gamma = gamma   # 坡度因子
        self.nu = nu   # 偏差因子
        self.rho = rho  # 信息素挥发速度

        self.start = start
        self.end = end
        self.start_layer = start_layer
        self.end_layer = end_layer

        # self.prob_matrix_distance = 1 / (distance_matrix + 1e-10 * np.eye(n_dim, n_dim))  # 避免除零错误
        self.prob_matrix_distance = self.get_distance()  # 避免除零错误
        self.prob_matrix_slope = self.get_slope()   # 获得坡度矩阵

        # self.Tau = np.ones((n_dim, n_dim))  # 信息素矩阵，每次迭代都会更新
        self.Tau = self.get_Tau()  # 信息素矩阵，每次迭代都会更新
        self.Table = np.zeros((size_pop, len(n_dim)-1)).astype(int)  # 某一代每个蚂蚁的爬行路径，原内容为x坐标，现在为坐标索引
        self.y = None  # 某一代每个蚂蚁的爬行总距离
        self.generation_best_X, self.generation_best_Y = [], []  # 记录各代的最佳情况
        self.x_best_history, self.y_best_history = self.generation_best_X, self.generation_best_Y  # 历史原因，为了保持统一
        self.best_x, self.best_y = None, None

    def get_distance(self):
        res = []
        for n in range(1, len(self.n_dim)):
            distance_matrix = spatial.distance.cdist(self.func[n-1], self.func[n], metric='euclidean')
            res.append((1 / (distance_matrix + 1e-10 * np.eye(self.n_dim[n-1], self.n_dim[n]))).tolist())

        return np.array(res)

    def calc_slope(self, arr1, arr2):
        arr1, arr2 = np.array(arr1), np.array(arr2)
        res = []
        for a in arr1:
            temp = arr2 - a
            res.append((temp[:, 2] / (np.sqrt(temp[:, 0] ** 2 + temp[:, 1] ** 2))).tolist())

        return np.array(res)

    def get_slope(self):
        res = []
        for n in range(1, len(self.n_dim)):
            slope_matrix = self.calc_slope(self.func[n-1], self.func[n])
            res.append((1 / (slope_matrix + 1e-10 * np.eye(self.n_dim[n-1], self.n_dim[n]))).tolist())

        return np.array(res)

    def get_Tau(self):
        res = []
        for n in range(1, len(self.n_dim)):
            res.append(np.ones((self.n_dim[n - 1], self.n_dim[n])).tolist())

        return np.array(res)

    def get_delta_tau(self):
        res = []
        for n in range(1, len(self.n_dim)):
            res.append(np.zeros((self.n_dim[n-1], self.n_dim[n])).tolist())

        return np.array(res)

    def run(self, max_iter=None):
        self.max_iter = max_iter or self.max_iter
        for i in range(self.max_iter):  # 对每次迭代
            # prob_matrix = (self.Tau ** self.alpha) * (self.prob_matrix_distance) ** self.beta  # 转移概率，无须归一化。
            y = []
            for j in range(self.size_pop):  # 对每个蚂蚁
                self.Table[j, self.start_layer] = self.func[self.start_layer].index(self.start)  # start point，其实可以随机，但没什么区别
                temp = 0
                # for k in range(self.n_dim - 1):  # 蚂蚁到达的每个节点
                for k in range(self.start_layer, self.end_layer-1):  # 蚂蚁到达的每个节点
                    prob_matrix = (np.array(self.Tau[k]) ** self.alpha) * (np.array(self.prob_matrix_distance[k])) ** self.beta * \
                                  (np.array(self.prob_matrix_slope[k])) ** self.gamma  # 转移概率，无须归一化。
                    # taboo_set = set(self.Table[j, :k + 1])  # 已经经过的点和当前点，不能再次经过
                    # allow_list = list(set(range(self.n_dim)) - taboo_set)  # 在这些点中做选择
                    prob = prob_matrix[self.Table[j, k]]
                    prob = prob / prob.sum()  # 概率归一化
                    # next_point = np.random.choice(self.func[k+1], size=1, p=prob)
                    # self.Table[j, k + 1] = self.func[k].index(next_point)
                    self.Table[j, k + 1] = int(np.random.choice(np.arange(len(self.func[k+1])), size=1, p=prob))

                    # 计算长度
                    pro_point = np.array(self.func[k][self.Table[j, k]])
                    next_point = np.array(self.func[k+1][self.Table[j, k+1]])
                    arr = next_point - pro_point
                    temp += math.hypot(arr[0],arr[1], arr[2])
                y.append(temp)

                print(i, j)

            y = np.array(y)

            # 计算距离
            # y = np.array([self.func(i) for i in self.Table])

            # 顺便记录历史最好情况
            index_best = y.argmin()
            x_best, y_best = self.Table[index_best, :].copy(), y[index_best].copy()
            self.generation_best_X.append(x_best)
            self.generation_best_Y.append(y_best)

            # 计算需要新涂抹的信息素
            # delta_tau = np.zeros((self.n_dim, self.n_dim))
            delta_tau = self.get_delta_tau()
            for j in range(self.size_pop):  # 每个蚂蚁
                # for k in range(self.n_dim - 1):  # 每个节点
                for k in range(self.start_layer, self.end_layer-1):  # 每个节点
                    n1, n2 = self.Table[j, k], self.Table[j, k + 1]  # 蚂蚁从n1节点爬到n2节点
                    delta_tau[k][n1][n2] += 1 / ((y[j] - 7) ** 6)  # 涂抹的信息素
                # n1, n2 = self.Table[j, self.n_dim - 1], self.Table[j, 0]  # 蚂蚁从最后一个节点爬回到第一个节点
                # delta_tau[n1, n2] += 1 / y[j]  # 涂抹信息素

            # 信息素飘散+信息素涂抹
            for k in range(self.start_layer, self.end_layer - 1):  # 每个节点
                self.Tau[k] = ((1 - self.rho) * np.array(self.Tau[k]) + np.array(delta_tau[k])).tolist()

        best_generation = np.array(self.generation_best_Y).argmin()
        self.best_x = self.generation_best_X[best_generation]
        self.best_y = self.generation_best_Y[best_generation]
        return self.best_x, self.best_y

    fit = run



if __name__ == '__main__':

    data = np.load('./data/python/data_ant.npy', allow_pickle=True).tolist()
    dict_layer = dict(zip(list(range(len(data))), data))
    dict_poxy = dict()
    for k, v in dict_layer.items():
        for i in v:
            dict_poxy[tuple(i)] = k

    start, end = 2, len(data)-3
    start_point = dict_layer[start][5]
    end_point = dict_layer[end][28]

    start_layer = dict_poxy[tuple(start_point)]
    end_layer = dict_poxy[tuple(end_point)]

    dim = [len(i) for i in data]

    aca = ACA_TSP(data, dim, start_point, end_point, start_layer, end_layer)
    best_x, best_y = aca.run()

    best_x = best_x.tolist()
    best_x.append(0)

    res = []
    for i in range(len(best_x)):
        res.append(data[i][best_x[i]])

    res = res[start_layer:end_layer]

    savemat("./data/matlab/path_ant.mat", {'b': res})