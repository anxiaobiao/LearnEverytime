import numpy as np
from scipy.io import savemat
import math
from scipy.spatial import Voronoi
from scipy.spatial import voronoi_plot_2d
import matplotlib.pyplot as plt

# 忽略警告
import warnings
warnings.filterwarnings("ignore")

barr_center = np.load('../data/Python/barr_center.npy')
data = np.load('../data/Python/data.npy')

# 计算Voronoi图
vor = Voronoi(barr_center)

x_min = data[0, 0, 0]
x_max = data[-1,-1,0]
y_min = data[0, 0, 1]
y_max = data[-1, -1, 1]
# bound = [data[0, 0, 0], data[0, 0, 1], data[-1,-1,0], data[-1, -1, 1]]

# 判断是否在框内,若在返回ture
def judge_frame(point):

    x, y = point[0], point[1]
    flag = (x >= x_min and x <= x_max and y >= y_min and y <= y_max)
    return flag

# 判断两线段相交
def judge_inter(A, B, C, D):

    def vector(piont_1, point_2):   # 输入numpy格式
        return point_2 - piont_1

    def vector_product(vec_1, vec_2):   # 计算向量
        return vec_1[0] * vec_2[1] - vec_2[0] * vec_1[1]

    AC = vector(A, C)
    AD = vector(A, D)
    BC = vector(B, C)
    BD = vector(B, D)
    CA = vector(C, A)
    CB = vector(C, B)
    DA = vector(D, A)
    DB = vector(D, B)

    # 相交返回true
    return (vector_product(AC, AD) * vector_product(BC, BD) <= 0 ) \
           and (vector_product(CA, CB) * vector_product(DA, DB) <= 0)


# 判断得出两线段的交点
def intersection(point_1, point_2):
    point_bound = [[[x_min, y_min], [x_max, y_min]], [[x_max, y_min], [x_max, y_max]],
                   [[x_min, y_max], [x_max, y_max]], [[x_min, y_max], [x_min, y_min]]]

    for line in point_bound:
        if judge_inter(point_1, point_2, line[0], line[1]):
            x1, x2, x3, x4 = point_1[0], point_2[0], line[0][0], line[1][0]
            y1, y2, y3, y4 = point_1[1], point_2[1], line[0][1], line[1][1]
            px = ((x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)) / ((x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4))
            py = ((x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)) / ((x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4))
            return [px, py]

# 求射线方程
def ray(barr, piont):

    # 计算障碍的中垂线
    def medLine(x1, y1, x2, y2):
        A = 2 * (x2 - x1)
        B = 2 * (y2 - y1)
        C = x1 ** 2 - x2 ** 2 + y1 ** 2 - y2 ** 2
        return A, B, C
    A, B, C = medLine(barr[0][0], barr[0][1], barr[1][0], barr[1][1])
    # angle = math.atan(-A/B)
    # theta = [np.cos(angle),np.sin(angle)]

    # return [theta[1], theta[0], np.linalg.det([piont, theta])]
    return [A, B, C]

# 射线与线段是否有交点
def ray_inter(point, barr, sPoint, ePoint, ray):
    sFlag = np.sum(np.array(ray) * np.array([sPoint[0], sPoint[1], 0]))
    eFlag = np.sum(np.array(ray) * np.array([ePoint[0], ePoint[1], 0]))
    num = 0
    num += sFlag == 0
    num += eFlag == 0
    num += sFlag * eFlag < 0
    return num == 1

# 判断射线与线段相交并求出交点
def ray_inter_point(ray, point, barr):
    point_bound = [[[x_min, y_min], [x_max, y_min]], [[x_max, y_min], [x_max, y_max]],
                   [[x_min, y_max], [x_max, y_max]], [[x_min, y_max], [x_min, y_min]]]

    list_inter = []
    for bound in point_bound:
        # if ray_inter(point, barr, line[0], line[1], ray):
        #     # abLine = [ray[0], ray[1]]
        #     # abDot = [line[0][1] - line[1][1], line[0][0] - line[1][0]]
        #     # c = [[ray[2]], [line[0][0] * line[1][1] - line[1][1] * line[0][0]]]
        #     # cross = np.linalg.solve([abLine, abDot], c)
        #     # return cross
        #
        #     sPoint, ePoint =  line[0], line[1]
        #     line = [sPoint[1] - ePoint[1], ePoint[0] - sPoint[0], sPoint[0] * ePoint[1] - ePoint[0] * sPoint[1]]
        #
        #     a0, b0, c0 = ray[0], ray[2], ray[2]
        #     a1, b1, c1 = line[0], line[1], line[2]
        #
        #     D = a0 * b1 - a1 * b0
        #     x = (b0 * c1 - b1 * c0) / D
        #     y = (a1 * c0 - a0 * c1) / D
        #
        #     return [x, y]

        sPoint, ePoint = bound[0], bound[1]
        line = [sPoint[1] - ePoint[1], ePoint[0] - sPoint[0], sPoint[0] * ePoint[1] - ePoint[0] * sPoint[1]]

        a0, b0, c0 = ray[0], ray[1], ray[2]
        a1, b1, c1 = line[0], line[1], line[2]

        D = a0 * b1 - a1 * b0
        x = (b0 * c1 - b1 * c0) / D
        y = (a1 * c0 - a0 * c1) / D

        list_inter.append([x, y])

    for i in list_inter:
        if judge_inter(point, np.array(i), barr[0].tolist(), barr[1].tolist()) and judge_frame(np.array(i)):
            return i


# 定义顶点和顶点连接的索引
vertices, ridge_vertices = [], []
# new_dict = {tuple(v):list(k) for k,v in vor.ridge_dict.items()}
new_dict = []
for k,v in vor.ridge_dict.items():
    if -1 in v:
        new_dict.append(list(k))

for ver_rela in vor.ridge_vertices:

    if -1 in ver_rela:
        temp = [0, 1]
        temp.pop(ver_rela.index(-1))
        if judge_frame(vor.vertices[ver_rela[temp[0]]]):
            # 与边界的交点
            # barr_ind = new_dict[tuple(ver_rela)]
            barr_ind = new_dict.pop(0)
            barr = [vor.points[barr_ind[0]], vor.points[barr_ind[1]]]       # np.array([], [])
            f_ray = ray(barr, vor.vertices[ver_rela[temp[0]]])  # 改为直线方程
            inter = ray_inter_point(f_ray, vor.vertices[ver_rela[temp[0]]], barr)

            if vor.vertices[ver_rela[temp[0]]].tolist() not in vertices:
                vertices.append(vor.vertices[ver_rela[temp[0]]].tolist())
            #     start = vertices.index(vor.vertices[ver_rela[temp[0]]].tolist())
            # else:
            #     start = vertices.index(vor.vertices[ver_rela[0]].tolist())

            start = vertices.index(vor.vertices[ver_rela[temp[0]]].tolist())
            vertices.append(inter)
            end = vertices.index(vertices[-1])
            ridge_vertices.append([start, end])


        else:
            new_dict.pop(0)
            continue

    else:
        # 两个都在
        if judge_frame(vor.vertices[ver_rela[0]]) and judge_frame(vor.vertices[ver_rela[1]]):
            if vor.vertices[ver_rela[0]].tolist() not in vertices:
                vertices.append(vor.vertices[ver_rela[0]].tolist())
            if vor.vertices[ver_rela[1]].tolist() not in vertices:
                vertices.append(vor.vertices[ver_rela[1]].tolist())

            start = vertices.index(vor.vertices[ver_rela[0]].tolist())
            end = vertices.index(vor.vertices[ver_rela[1]].tolist())
            ridge_vertices.append([start, end])

        # 一个都不在
        elif not(judge_frame(vor.vertices[ver_rela[0]]) or judge_frame(vor.vertices[ver_rela[1]])):
            continue

        # 有一个在
        else:
            # 与边界的交点，即判断两线段的交点
            inter = intersection(vor.vertices[ver_rela[0]], vor.vertices[ver_rela[1]])

            # 判断那一点在框内
            if judge_frame(vor.vertices[ver_rela[0]]):
                if vor.vertices[ver_rela[0]].tolist() not in vertices:
                    vertices.append(vor.vertices[ver_rela[0]].tolist())
                    start = vertices.index(vor.vertices[ver_rela[0]].tolist())
                else:
                    start = vertices.index(vor.vertices[ver_rela[0]].tolist())

            else:
                if vor.vertices[ver_rela[1]].tolist() not in vertices:
                    vertices.append(vor.vertices[ver_rela[1]].tolist())
                    start = vertices.index(vor.vertices[ver_rela[1]].tolist())
                else:
                    start = vertices.index(vor.vertices[ver_rela[1]].tolist())

            # start = vertices.index(vor.vertices[ver_rela[0]].tolist())

            vertices.append(inter)
            end = vertices.index(vertices[-1])
            ridge_vertices.append([start, end])

vertices = np.array(vertices)
ridge_vertices = np.array(ridge_vertices)

plt.scatter(barr_center[:, 0], barr_center[:, 1])
plt.scatter(vertices[:, 0], vertices[:, 1])
for point_ind in ridge_vertices:
    plt.plot([vertices[point_ind[0], 0], vertices[point_ind[1], 0]],
             [vertices[point_ind[0], 1], vertices[point_ind[1], 1]],
             color = 'k')

plt.show()

voronoi_plot_2d(vor)
plt.show()

savemat("../data/matlab/Voronoi.mat", {'vertices': vertices, 'ridge_vertices': ridge_vertices})
'''
下面为离散化，将得到的voronoi数据离散化为数据点的形式并存储
'''
def distance(point_1, point_2):

    x_1, y_1 = point_1[0], point_1[1]
    x_2, y_2 = point_2[0], point_2[1]

    return math.sqrt((x_1 - x_2) ** 2 + (y_1 - y_2) ** 2)

# 获得锚框
def anchor_frame(point_1, vec_2):
    x_frame, y_frame = interval_x+1, interval_y+1
    x_min, x_max, y_min, y_max = point_1[0]-x_frame, point_1[0]+x_frame, point_1[1]-y_frame, point_1[1]+y_frame
    ans = []
    for i in range(len(vec_2)):
        if vec_2[i, 0, 0] > x_min and vec_2[i, 0, 0] < x_max:
            for j in range(len(vec_2[0])):
                if vec_2[i, j, 1] > y_min and vec_2[i, j, 1] < y_max:
                    ans.append(vec_2[i, j, 0:2].tolist())
                else:
                    continue
        else:
            continue
    return ans

# vec_1在vec_2上做匹配问题
def corrected_results(vec_1, all_vec):
    res = []
    i = 0
    for point_1 in vec_1:
        # 获得锚框内的点
        vec_2 = anchor_frame(point_1, all_vec)
        min_dis = distance(point_1, vec_2[0])
        # min_point = vec_2[0, 0:2]
        min_point = vec_2[0]
        for point_2 in vec_2:
            temp = distance(point_1, point_2)
            if temp < min_dis:
                min_dis = temp
                # min_point = point_2[0:2]
                min_point = point_2
        # res.append(min_point.tolist())
        res.append(min_point)
        i += 1
        print(i)

    return res

# 返回直线的k和b
def make_line(point_1, point_2):
    x_1, y_1 = point_1[0], point_1[1]
    x_2, y_2 = point_2[0], point_2[1]

    k = (y_1 - y_2) / (x_1 - x_2)
    b = y_2 - k * x_2
    return [k, b]

# 采样的具体实现
def discretization(start, end, interval_SE, param):
    x_1, x_2 = start[0], end[0]
    if x_1 > x_2:
        x_1, x_2 = x_2, x_1

    res = []
    temp = x_1
    while temp < x_2:   # 间隔采样
        res.append([temp, param[0] * temp + param[1]])
        temp += interval_SE

    return res

# 计算间隔
def inter(sample):
    temp = []
    for i in range(len(sample) - 1):
        temp.append(sample[i + 1] - sample[i])
    # interval_x = int(min(np.unique(temp)))
    return int(min(np.unique(temp)))


data_2D = np.reshape(data, (len(data) * len(data[0]), 3))

# 计算X轴采样间隔
x_unique = np.unique(data_2D[:, 0])
interval_x = inter(x_unique)

# 计算Y轴采样间隔
y_unique = np.unique(data_2D[:, 1])
interval_y = inter(y_unique)

vertices_point = corrected_results(vertices, data)

# 进行离散化操作
vector_side = []
for point_ind in ridge_vertices:
    parameter = make_line(vertices[point_ind[0]], vertices[point_ind[1]])       # 计算所生成的直线
    res = discretization(vertices[point_ind[0]], vertices[point_ind[1]], interval_x, parameter)   # 直线采样
    vector_side.append(res)

ans = []
for vec in vector_side:
    temp = corrected_results(vec, data)
    temp = set([tuple(t) for t in temp])    # 去掉重复点(set数据为无序不重复数据)
    temp = list(list(t) for t in temp)
    ans.append(temp)

ans = np.array(ans)
np.save('../data/Python/voronoi_point.npy', ans)












