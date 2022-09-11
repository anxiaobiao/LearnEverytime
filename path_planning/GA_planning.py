import numpy as np
import math
import matplotlib.pyplot as plt
import copy
import time

import Geometric_gradient as geo
import draw

class GA_Planning:
    def __init__(self, popsize = 1000, indsize = 5, attack_len = 300, iterations = 50, attack_platform = np.array([0.0, 250.0]),\
                 launch_platform = np.array([0.0, 0.0]), perform_para = [0.6, 0.2, 0.2], penalty_para = [0.2, 0.2, 0.6],\
                     max_angle = math.pi / 2, min_length = 10, draw_flag = False, \
                         obstacle = [[math.pi/12, 30, 10], [math.pi/36, 200, 20], [0, 100, 30]]):

        self.popsize = popsize          # 种群数量，表示有几条可行路径
        self.indsize = indsize          # 个体数量，表示有几个转向点
        self.attack_len = attack_len    # 最长攻击长度
        self.iterations = iterations    # 迭代次数

        self.attack_platform = attack_platform  # 极坐标（极角，极径）
        self.launch_platform = launch_platform  # 极坐标

        self.ind_all = self.codeingGA()  # 全部个体的具体特征，默认为20个，每个个体5*2=10大小
        # self.velocity = self.init_velocity()
        self.curr_best = self.ind_all[:]  # 每个粒子当前最优位置

        self.global_best = self.ind_all[0][:]  # 最好的个体特征

        self.perform_para = perform_para  # 性能指标的权重系数
        self.penalty_para = penalty_para  # 惩罚函数的权重系数

        self.max_angle = max_angle  # 最大转弯半径
        self.min_length = min_length  # 最小直线飞行距离

        self.obstacle = obstacle  # [圆心极角，圆心极径，半径]，障碍为圆形

        # self.best_score = self.performance(self.global_best) - self.penalty_func(self.global_best)

        self.draw_flag = draw_flag  # 调试时使用

    def codeingGA(self):
        