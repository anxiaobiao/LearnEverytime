import math
import heapq
import numpy as np
from scipy.io import savemat
import path_people.get_barr as get_barr
import sys
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# 忽略警告
import warnings
warnings.filterwarnings("ignore")

class AStar:
    """AStar set the cost + heuristics as the priority
    """
    def __init__(self, s_start, s_goal, func, heuristic_type, alpha=10, angle=math.pi / 4):
        self.s_start = s_start
        self.s_goal = s_goal
        self.heuristic_type = heuristic_type
        self.alpha = alpha
        self.angle = angle

        self.func = func    # 环境数据

        self.u_set =  [(-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1)]  # feasible input set
        self.obs = self.get_obs()  # position of obstacles

        self.OPEN = []  # priority queue / OPEN set
        self.CLOSED = []  # CLOSED set / VISITED order
        self.PARENT = dict()  # recorded parent
        self.g = dict()  # cost to come

    def get_obs(self):
        obs = set() # 无序不重复数据集

        for i in self.func[0]:
            obs.add(tuple(i.tolist()))
        for i in self.func[-1]:
            obs.add(tuple(i.tolist()))

        for i in self.func[:, 0]:
            obs.add(tuple(i.tolist()))
        for i in self.func[:, -1]:
            obs.add(tuple(i.tolist()))

        return obs

    def updata_obs(self, barr):
        for b in barr:
            self.obs.add(tuple(b.tolist()))

    def searching(self):
        """
        A_star Searching.
        :return: path, visited order
        """

        self.PARENT[self.s_start] = self.s_start
        self.g[self.s_start] = 0
        self.g[self.s_goal] = math.inf
        heapq.heappush(self.OPEN, (self.f_value(self.s_start), self.s_start))  # 最小堆，顺序是第一个比较，第一个相同第二个比较

        num = 0
        while self.OPEN:
            _, s = heapq.heappop(self.OPEN)
            self.CLOSED.append(s)

            if s == self.s_goal:  # stop condition
                break

            # dis_start_s = math.hypot(self.s_start[0] - s[0], self.s_start[1] - s[1], self.s_start[2] - s[2])
            for s_n in self.get_neighbor(s):
                new_cost = self.g[s] + self.cost(s, s_n) # 对于所有可行数据集求代价
                # new_cost = dis_start_s + self.cost(s, s_n)  # 对于所有可行数据集求代价

                if s_n not in self.g:
                    self.g[s_n] = math.inf

                if new_cost < self.g[s_n]:  # conditions for updating Cost
                    self.g[s_n] = new_cost
                    self.PARENT[s_n] = s
                    heapq.heappush(self.OPEN, (self.f_value(s_n), s_n)) # f表示总代价

            num = num + 1
            print('{} done...'.format(num))

        return self.extract_path(self.PARENT), self.CLOSED

    def get_neighbor(self, s):
        """
        find neighbors of state s that not in obstacles.
        :param s: state
        :return: neighbors
        """
        x, y = np.where(data[:, 0, 0] == s[0]), np.where(data[0, :, 1] == s[1])
        x, y = int(x[0]), int(y[0]) # 获得当前点的坐标索引

        neighbor = [(x + u[0], y + u[1]) for u in self.u_set]

        return [tuple(self.func[n].tolist()) for n in neighbor]

    def cost(self, s_start, s_goal):
        """
        Calculate Cost for this motion
        :param s_start: starting node
        :param s_goal: end node
        :return:  Cost for this motion
        :note: Cost function could be more complicate!
        """

        if self.is_collision(s_start, s_goal):
            # print('111111111111111111111111111111111111111111111111111111111111111111111111')
            return math.inf

        dis = math.hypot(s_goal[0] - s_start[0], s_goal[1] - s_start[1], s_goal[2] - s_start[2])
        solpe = self.get_solpe(s_start, s_goal)

        res = dis * solpe ** self.alpha

        # return math.hypot(s_goal[0] - s_start[0], s_goal[1] - s_start[1], s_goal[2] - s_start[2])
        return res

    def get_solpe(self, s_start, s_goal):

        h = s_goal[2] - s_start[2]
        side = math.hypot(s_goal[0] - s_start[0], s_goal[1] - s_start[1])
        res = abs(h / side) + 1

        # if res < math.sqrt(3) / 3:
        #     res = 1
        if res - 1 < math.tan(self.angle):
            res = 1

        return res

    def is_collision(self, s_start, s_end):
        """
        check if the line segment (s_start, s_end) is collision.
        :param s_start: start node
        :param s_end: end node
        :return: True: is collision / False: not collision
        """

        if s_start in self.obs or s_end in self.obs:
            # print('11111111111111111111111111')
            return True

        if s_start[0] != s_end[0] and s_start[1] != s_end[1]:
            if s_end[0] - s_start[0] == s_start[1] - s_end[1]:
                s1 = (min(s_start[0], s_end[0]), min(s_start[1], s_end[1]))
                s2 = (max(s_start[0], s_end[0]), max(s_start[1], s_end[1]))
            else:
                s1 = (min(s_start[0], s_end[0]), max(s_start[1], s_end[1]))
                s2 = (max(s_start[0], s_end[0]), min(s_start[1], s_end[1]))

            if s1 in self.obs or s2 in self.obs:
                return True

        return False

    def f_value(self, s):
        """
        f = g + h. (g: Cost to come, h: heuristic value)
        :param s: current state
        :return: f
        """

        return self.g[s] + self.heuristic(s)

    def extract_path(self, PARENT):
        """
        Extract the path based on the PARENT set.
        :return: The planning path
        """
        def searck_key(keys):
            val = np.inf
            res = keys[0]
            for k in keys:
                subtraction_val = np.array(k) - np.array(self.s_goal)
                dis = math.hypot(subtraction_val[0], subtraction_val[1], subtraction_val[2])
                if dis < val:
                    res = k
                    val = dis
            return res

        path = [self.s_goal]
        s = self.s_goal

        while True:
            # s = PARENT[s]
            try:
                s = PARENT[s]
            except (KeyError):
                keys = list(PARENT.keys())
                recent_key = searck_key(keys)
                path = [recent_key]
                s = PARENT[recent_key]
            path.append(s)

            if s == self.s_start or s in self.obs:
                break

        return list(path)

    def heuristic(self, s):
        """
        Calculate heuristic.
        :param s: current node (state)
        :return: heuristic function value
        """

        heuristic_type = self.heuristic_type  # heuristic type
        goal = self.s_goal  # goal node

        if heuristic_type == "manhattan":
            return abs(goal[0] - s[0]) + abs(goal[1] - s[1]) + abs(goal[2] - s[2])
        else:
            return math.hypot(goal[0] - s[0], goal[1] - s[1], goal[2] - s[2])

def calc_len(arr):
    dis = 0
    for i in range(1, len(arr)):
        dis += abs(math.hypot(arr[i-1][0] - arr[i][0], arr[i-1][1] - arr[i][1], arr[i-1][2] - arr[i][2]))

    return int(dis)

def draw(data, path, barr):
    fig = plt.figure()
    ax = Axes3D(fig)

    ax.scatter(data[:, 0], data[:, 1], data[:,2], s=1, c='r')
    ax.scatter(barr[:, 0], barr[:, 1], barr[:, 2], s=5, c='k')
    ax.scatter(path[:, 0], path[:, 1], path[:, 2], s=15, c='b')

    # ax.savefig("a.png")
    # ax.show()

def matching(point, data):
    ans = data[0]
    for d in data:
        x_1, y_1, z_1 = d[0] - point[0], d[1] - point[1], d[2] - point[2]
        x_2, y_2, z_2 = ans[0] - point[0], ans[1] - point[1], ans[2] - point[2]
        res_1 = math.sqrt(x_1 ** 2 + y_1 ** 2 + z_1 ** 2)
        res_2 = math.sqrt(x_2 ** 2 + y_2 ** 2 + z_2 ** 2)
        if res_1 < res_2:
            ans = d
    return ans.tolist()

if __name__ == '__main__':
    angle = math.pi / 18   # pi/4与pi/3

    # data = np.load('./data/python/data.npy')
    data = np.load('./data/python/data_moon_1.npy')
    draw_data = np.reshape(data, (len(data) * len(data[0]), 3))

    # s_start = tuple(data[170, 100].tolist())
    # s_goal = tuple(data[160, 200].tolist())

    give = [(-93.3827136397538,182.482189169476,3.34697756390315), (31.3021007271463,-70.8673974811307,2.75040293291228)]
    # num = 2

    # s_start = (-50.9570036884844,-110.697099290399,2.37690739972538)
    # s_goal = (-22.3223460808182,59.9547553041359,21.0320825339638)

    s_start = give[0]
    s_goal = give[1]

    # 点匹配
    s_start = tuple(matching(s_start, draw_data))
    s_goal = tuple(matching(s_goal, draw_data))
    print('匹配完成')

    # s_start = tuple(data[170, 120].tolist())
    # s_goal = tuple(data[160, 220].tolist())

    barrier, _ = get_barr.get_barr(data, angle)
    barrier = get_barr.get_barr_slide(data, math.pi / 3)
    if list(s_goal) in barrier.tolist() or list(s_start) in barrier.tolist():
        print("\n起点或终点在障碍中")
        sys.exit()

    astar = AStar(s_start, s_goal, data, "euclidean", alpha=10, angle = angle)     # alpha >= 10
    astar.updata_obs(barrier)
    path, visited = astar.searching()
    path = np.array(path)

    # np.savetxt(r'D:\code\path_planning\path_people\answer\{}.txt'.format(num), path, fmt='%.5f', delimiter=',', footer=';')

    velocity = 2.8
    dis = calc_len(path)
    time = int(dis / velocity)
    print('总长度：{}米\t'.format(dis), '时间：{}小时 {}分钟 {}秒'.format(int(time/3600), int((time%3600)/60), (time%60)))

    draw(draw_data, path, barrier)

    savemat("./data/matlab/path.mat", {'p': path})
    savemat("./data/matlab/barrier.mat", {'b': barrier})

    # path[:, 0] += 594000
    # path[:, 1] += 3370000
    # np.save('./data/python/path.npy', path)