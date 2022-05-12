# -*- coding: utf-8 -*-
"""
Created on Fri Mar 11 08:41:50 2022

@author: Vada
"""

import numpy as np
import math
import matplotlib.pyplot as plt
import copy
import time

import Geometric_gradient as geo
import draw


class PSO_Planning():
    
    def __init__(self, popsize = 1000, indsize = 5, attack_len = 300, iterations = 50, attack_platform = np.array([0.0, 250.0]),\
                 launch_platform = np.array([0.0, 0.0]), perform_para = [0.6, 0.2, 0.2], penalty_para = [0.2, 0.2, 0.6],\
                     max_angle = math.pi / 2, min_length = 10, draw_flag = False, \
                         obstacle = [[math.pi/12, 30, 10], [math.pi/36, 200, 20], [0, 100, 30]]):
        """
        

        Parameters
        ----------
        popsize : int, optional
            表示种群数量，即存在多少粒子. The default is 1000.
            
        indsize : int, optional
            某种群的个体数，表示多少个转向点. The default is 5.
            
        attack_len : int, optional
            最大攻击长度，表示椭圆的长轴. The default is 300.
            
        iterations : int, optional
            迭代数，表示迭代多少次. The default is 50.
            
        attack_platform : np.array, optional
            目标点位置，极坐标形式. The default is np.array([0.0, 250.0]).
            
        launch_platform : np.array, optional
            发射点位置，默认原点为发射点，极坐标形式. The default is np.array([0.0, 0.0]).
            
        perform_para : list, optional
            目标函数的权重系数，[总路径，转向角绝对值和，转向角绝对值均方差]. The default is [0.6, 0.2, 0.2].
            
        penalty_para : list, optional
            惩罚函数的权重系数，[大于最大转弯半径，小于最小飞行路径，经过障碍]. The default is [0.2, 0.2, 0.6].
            
        max_angle : float, optional
            最大转弯半径. The default is math.pi / 2.
            
        min_length : int, optional
            最小飞行长度. The default is 10.
            
        draw_flag : bool, optional
            是否将每一步的图绘制出来，调试时使用. The default is False.
            
        obstacle : list, optional
            圆形障碍，本算法仅支持圆形障碍,[圆心极角，圆心极径，圆的半径]. The default is [[math.pi/12, 30, 10], [math.pi/36, 200, 20], [0, 100, 30]].

        Returns
        -------
        None.

        """
        self.popsize = popsize          # 种群数量，表示有几条可行路径
        self.indsize = indsize          # 个体数量，表示有几个转向点
        self.attack_len = attack_len    # 最长攻击长度
        self.iterations = iterations    # 迭代次数
        
        self.attack_platform = attack_platform  # 极坐标（极角，极径）
        self.launch_platform = launch_platform # 极坐标
        
        self.ind_all = self.codeingPSO()    # 全部个体的具体特征，默认为20个，每个个体5*2=10大小
        self.velocity = self.init_velocity()
        self.curr_best = self.ind_all[:]    # 每个粒子当前最优位置
        
        self.global_best = self.ind_all[0][:]  # 最好的个体特征
        
        self.perform_para = perform_para # 性能指标的权重系数
        self.penalty_para = penalty_para # 惩罚函数的权重系数
        
        self.max_angle = max_angle    # 最大转弯半径
        self.min_length = min_length        # 最小直线飞行距离
        
        self.obstacle = obstacle  # [圆心极角，圆心极径，半径]，障碍为圆形
        
        self.best_score = self.performance(self.global_best) - self.penalty_func(self.global_best)
        
        self.draw_flag = draw_flag  # 调试时使用
        
    # 初始化速度
    def init_velocity(self):
        all_v = []
        
        for i in range(self.popsize):
            v = [0] * self.indsize * 2
            for j in range(self.indsize):
                v[j] = np.random.uniform(-math.pi/2, math.pi/2)   # 角度范围是-π/2~π/2
                v[j+self.indsize] = np.random.uniform(0, 3)
            # ind_all.append(copy.deepcopy(ind))
            all_v.append(v)
            
        return all_v
        
        # all_v.append([[np.random.uniform(-math.pi,math.pi)for i in range(self.indsize)]for j in range(self.popsize)])
        # all_v.append([[np.random.uniform(0, 3)for i in range(self.indsize)]for j in range(self.popsize)])

    # 编码操作
    def codeingPSO(self):   
        
        # 返回值是多维的list，每一维表示一个PSO个体
        ind_all = []
        
        for i in range(self.popsize):
            ind = [0] * self.indsize * 2
            for j in range(self.indsize):
                ind[j] = np.random.uniform(-math.pi/2, math.pi/2)   # 角度范围是-π/2~π/2
                max_len = geo.polar_coordinates(self.attack_len, self.attack_platform[1], self.attack_platform[0], ind[j])    # 根据角度变化
                ind[j+self.indsize] = np.random.uniform(0, max_len)
            # ind_all.append(copy.deepcopy(ind))
            ind_all.append(ind)
            
        return ind_all
    
    # 返回飞行路径和旋转角度
    def perfor(self, ind):
            
        # 求当前椭圆极轴与发射平台到转向点的夹角
        pro_angle = self.attack_platform[0]
        all_angle = []
        for i in range(self.indsize):
            all_angle.append(ind[i] - pro_angle)
            pro_angle = ind[i]
        # all_angle = list(map(abs,all_angle))    # 使结果成为正值
            
        # 求目标点到转向点的距离，即飞行距离
        pro_length = self.attack_platform[1]
        all_length = []
        for i in range(self.indsize):
            all_length.append(geo.cosine_law(pro_length, ind[i+self.indsize], all_angle[i]))
            pro_length = ind[i+self.indsize]
        all_length.append(ind[i+self.indsize])
        
        # 求飞行路径与极径夹角
        pro_length = self.attack_platform[1]
        all_turn_angle = []
        for i in range(self.indsize):
            sin_angle = math.sin(all_angle[i]) / (all_length[i] + 0.000001) * pro_length
            while sin_angle > 1 or sin_angle < -1:
                if sin_angle > 1:
                    sin_angle -= 1
                if sin_angle < -1:
                    sin_angle += 1
            all_turn_angle.append(math.asin(sin_angle))
            pro_length = ind[i+self.indsize]
        
        # 两个路径的夹角
        for i in range(1, self.indsize):
            temp = math.pi - abs(all_angle[i]) - abs(all_turn_angle[i])
            if(all_angle[i] > 0):
                all_turn_angle[i-1] += temp
            else:
                all_turn_angle[i-1] -= temp
        all_turn_angle = list(map(abs,all_turn_angle))
        
        # 转向角的绝对值
        for i in range(self.indsize):
            all_turn_angle[i] = math.pi - all_turn_angle[i]
        
        return all_turn_angle, all_length
    
    # 某一条航路的性能指标函数,ind代表某一条航路
    def performance(self, ind):
        
        def satidfaction(f_max, f_min, f):
            if f <= f_min:
                return 1
            elif f >= f_max:
                return 0
            else:
                return (f_max - f) / (f_max - f_min)
        
        all_turn_angle, all_length = self.perfor(ind)
        
        # 路径长度的满意度函数
        μ_s = satidfaction(self.attack_len, self.attack_platform[1] * math.cos(self.attack_platform[0]), sum(all_length))
        # μ_s = (self.attack_len - sum(all_length)) / (self.attack_len - self.attack_platform[1] * math.cos(self.attack_platform[0]))
        # 转向角的满意度函数
        μ_α = satidfaction(self.max_angle * self.indsize, 0, sum(all_turn_angle))
        # μ_α = (self.max_angle * self.indsize - sum(all_turn_angle)) / (self.max_angle * self.indsize)
        # 转向角均方差的满意度函数
        μ_δ = satidfaction(45, 0, math.sqrt(np.var(all_turn_angle)))
        # μ_δ = (45 - math.sqrt(np.var(all_turn_angle))) / 45
        # μ_δ = (math.pi / 8 - math.sqrt(np.var(all_turn_angle))) / math.pi / 8
        
        return self.perform_para[0] * μ_s + self.perform_para[1] * μ_α + self.perform_para[2] * μ_δ     # 返回值表示适应度函数
        
    # 确定三个边所对应的角度是否为钝角
    def deter_edge(self, ang_1, dia_1, ang_2, dia_2, ang_3, dia_3):
        
        # 确定边对应的cos值
        def cos_angle(a, b, c):
            return (a ** 2 + b ** 2 - c ** 2) / 2 * a * b
        
        a = geo.cosine_law(dia_1, dia_2, abs(ang_1 - ang_2))
        b = geo.cosine_law(dia_2, dia_3, abs(ang_2 - ang_3))
        c = geo.cosine_law(dia_3, dia_1, abs(ang_3 - ang_1))
        
        cos_a = cos_angle(c, b, a)
        cos_b = cos_angle(c, a, b)
        cos_c = cos_angle(a, b, c)
        
        return cos_a > 0 and cos_b > 0 and cos_c > 0    # 全部角度都为锐角

    def distance(self, pro_piont, ind, ever_obstacle, i):
        
        # 利用海伦公式求面积
        a = geo.cosine_law(pro_piont[1], ind[i+self.indsize], abs(pro_piont[0] - ind[i]))   # 圆心所对边的长度
        b = geo.cosine_law(ever_obstacle[1], ind[i+self.indsize], abs(ever_obstacle[0] - ind[i]))
        c = geo.cosine_law(pro_piont[1], ever_obstacle[1], abs(pro_piont[0] - ever_obstacle[0]))
        p = (a + b + c) / 2
        S = math.sqrt(p * (p - a) * (p - b) * (p - c))
        
        return (2 * S / a) < ever_obstacle[2]
                
    # 每一条航路的惩罚函数
    def penalty_func(self, ind):
        
        # 导出角度集合和长度集合
        all_turn_angle, all_length = self.perfor(ind)
        
        # 判断圆形障碍是否与航路相交
        def jud_intersect(self, ind):
            
            # 对于每一个圆形障碍，障碍表示（极角，极径，半径）
            # 假设目标点不在障碍内
            for ever_obstacle in self.obstacle:
                pro_piont = self.attack_platform
                
                # 转向点与障碍圆心距离小于半径，必定相撞
                for i in range(self.indsize):
                    
                    if geo.cosine_law(ind[i], ever_obstacle[1], abs(ind[i] - ever_obstacle[0])) < ever_obstacle[2]:
                        return True
                    
                # 判断圆心到线段距离，若小于，相交（由于点之间比成线段，所以大于则路径必不相撞）    
                for i in range(self.indsize):
                    # if self.distance(pro_piont, ind, ever_obstacle, i) and self.deter_edge(pro_piont[0], pro_piont[1], ind[i], ind[i+self.indsize], ever_obstacle[0], ever_obstacle[1]):
                    #     return True
                    if self.distance(pro_piont, ind, ever_obstacle, i):
                        return True
                    pro_piont = np.array([ind[i], ind[i+self.indsize]])
                if self.distance(self.launch_platform, ind, ever_obstacle, i):
                    return True
        
            return False
        
        f_a, f_b, f_c = 0, 0, 0 # 最大转弯角度、最小直线飞行距离、是否与障碍物相撞的惩罚标志初始化为0(即不超标)
        
        if jud_intersect(self, ind):    # 相撞则返回1
            f_c = 1 # 是否与障碍相交
            
        if all_length[len(all_length) - 1] < self.min_length:   #确定最后一个距离与最小飞行路径的关系
              f_b = 1   # 飞行距离与最小距离的关系
        for i in range(self.indsize):
            if all_turn_angle[i] > self.max_angle:
                f_a = 1 # 旋转角度与最大角度的关系
            if all_length[i] < self.min_length:
                f_b = 1

         
        return self.penalty_para[0] * f_a + self.penalty_para[1] * f_b + self.penalty_para[2] * f_c
    
    def objective_func(self):
        
        # 目标函数值
        objective_value = []
        for ind in self.ind_all:
            temp = self.performance(ind) - self.penalty_func(ind)
            objective_value.append(temp)
            
        old_value = []
        for ind in self.curr_best:
            temp = self.performance(ind) - self.penalty_func(ind)
            old_value.append(temp)
        
        # 将当前优秀的位置分配给当前最优
        best_value = []
        for i in range(self.popsize):
            if objective_value[i] > old_value[i]:
                self.curr_best[i] = copy.deepcopy(self.ind_all[i])
                # self.curr_best[i] = self.ind_all[i]
                best_value.append(objective_value[i])
            else:
                best_value.append(old_value[i])
                
        # 筛选出全局最优位置
        # best_value = self.performance(self.global_best) - self.penalty_func(self.global_best)
        for i in range(self.popsize):
            if best_value[i] > self.best_score:
                self.global_best = copy.deepcopy(self.curr_best[i])
                self.best_score = copy.deepcopy(best_value[i])
                # self.global_best = self.curr_best[i]
                # self.best_score = best_value[i]
                
        # temp = np.array(self.ind_all)
        # temp_old = np.array(self.curr_best)
        # temp_v = np.array(self.velocity)
        
        # objective_value = np.array(objective_value)
        # objective_value = np.argsort(-objective_value)
        
        # temp = temp[objective_value]
        # temp_old = temp_old[objective_value]
        # temp_v = temp_v[objective_value]
        
        # self.ind_all = temp.tolist()
        # self.curr_best = temp_old.tolist()
        # self.velocity = temp_v.tolist()
        
        
    # 经典PSO算法
    def PSO(self):
        
        # 初始化参数
        c_1, c_2 = 2, 2
        # r_1, r_2 = np.random.rand(), np.random.rand()   
        
        for k in range(self.iterations):
            
            if self.draw_flag:
                self.draw()
            print("PSO第{}次迭代,分数{}".format(k, self.best_score))
            
            w = 0.9 - 0.5 / self.iterations * k
            r_1, r_2 = np.random.rand(), np.random.rand() 
            
            self.objective_func()
            for i in range(self.popsize):
                for j in range(self.indsize):
                    self.velocity[i][j] = w * self.velocity[i][j] + c_1 * r_1 * \
                        (self.curr_best[i][j] - self.ind_all[i][j]) + c_2 * r_2 * \
                            (self.global_best[j] - self.ind_all[i][j])
                    self.ind_all[i][j] = self.ind_all[i][j] + self.velocity[i][j]
                    
                    self.velocity[i][j + self.indsize] = w * self.velocity[i][j + self.indsize] + c_1 * r_1 * \
                        (self.curr_best[i][j + self.indsize] - self.ind_all[i][j + self.indsize]) + c_2 * r_2 * \
                            (self.global_best[j + self.indsize] - self.ind_all[i][j + self.indsize])
                    self.ind_all[i][j + self.indsize] = self.ind_all[i][j + self.indsize] + self.velocity[i][j + self.indsize]
            
        self.objective_func()
     
        
    # OACRR-PSO算法
    def OACRR_PSO(self):
        
        # 获得黄金分割位置
        def get_pg(ind, j):
            
            if j == 0:
                return 0.382 * ind[j]
            elif j < self.indsize:
                return 0.382 * ind[j] + 0.618 * ind[j-1]
            elif j == self.indsize:
                return 0.382 * ind[j] + 0.618 * self.attack_platform[1]
            else:
                return 0.382 * ind[j] + 0.309 * ind[j-1]
            
        # 初始化参数
        c_1, c_2, c_3 = 2, 2, 2
        # r_1, r_2, r_3 = np.random.rand(), np.random.rand(), np.random.rand()
                
        for k in range(self.iterations):
            
            if self.draw_flag:
                self.draw()
            print("OACRR-PSO第{}次迭代,分数{}".format(k, self.best_score))
            
            w = 0.9 - 0.5 / self.iterations * k
            r_1, r_2, r_3 = np.random.rand(), np.random.rand(), np.random.rand()
            
            self.objective_func()
            for i in range(self.popsize):
                remain_len = self.attack_len
                pro_angle = self.attack_platform[0]
                pol_len = self.attack_platform[1]
                for j in range(self.indsize):
                    
                    # 记录上一代的位置和速度
                    # v = self.velocity[i][j]
                    angle = self.ind_all[i][j]
                    pol = self.ind_all[i][j + self.indsize]
                    # v_ang , v_pol = self.velocity[i][j], self.velocity[i][j + self.indsize]
                    
                    # 更新速度位置
                    self.velocity[i][j] = w * self.velocity[i][j] + c_1 * r_1 * \
                        (self.curr_best[i][j] - self.ind_all[i][j]) + c_2 * r_2 * \
                            (self.global_best[j] - self.ind_all[i][j])
                    self.ind_all[i][j] = self.ind_all[i][j] + self.velocity[i][j]
                                        
                    # 更新极径位置
                    self.velocity[i][j + self.indsize] = w * self.velocity[i][j + self.indsize] + c_1 * r_1 * \
                        (self.curr_best[i][j + self.indsize] - self.ind_all[i][j + self.indsize]) + c_2 * r_2 * \
                            (self.global_best[j + self.indsize] - self.ind_all[i][j + self.indsize])
                    self.ind_all[i][j + self.indsize] = self.ind_all[i][j + self.indsize] + self.velocity[i][j + self.indsize]
                    
                    num = 0
                    # 如果当前节点位置大于区域簇，执行下面的语句
                    while geo.polar_coordinates(remain_len, pol_len, pro_angle, self.ind_all[i][j]) < self.ind_all[i][j + self.indsize]:
                        
                        # 调试用
                        # time.sleep(1)
                        # print(k, i, j)
                        # print(geo.polar_coordinates(remain_len, pol_len, pro_angle, self.ind_all[i][j]), self.ind_all[i][j + self.indsize])
                        # print(remain_len, pol_len, pro_angle, self.ind_all[i][j])
                        
                        pg_angle = get_pg(self.ind_all[i], j)
                        pg_pol = get_pg(self.ind_all[i], j + self.indsize)
                        # print(pg_angle, pg_pol)
                        # print(angle, pol)
                        
                        # 更新角度
                        self.velocity[i][j] = c_3 * r_3 * (pg_angle - angle)
                        self.ind_all[i][j] = angle + self.velocity[i][j]
                        # self.velocity[i][j] = c_3 * r_3 * (pg_angle - self.ind_all[i][j])
                        # self.ind_all[i][j] = self.ind_all[i][j] + self.velocity[i][j]
                        
                        # 更新速度
                        self.velocity[i][j + self.indsize] = c_3 * r_3 * (pg_pol - pol)
                        self.ind_all[i][j + self.indsize] = pol + self.velocity[i][j + self.indsize]
                        # self.velocity[i][j + self.indsize] = c_3 * r_3 * (pg_pol - self.ind_all[i][j + self.indsize])
                        # self.ind_all[i][j + self.indsize] = self.ind_all[i][j + self.indsize] + self.velocity[i][j + self.indsize]
                        
                        if num >10:
                            self.ind_all[i][j + self.indsize] %= geo.polar_coordinates(remain_len, pol_len, pro_angle, self.ind_all[i][j])
                            break
                        num += 1
                    
                    pro_angle += self.ind_all[i][j]
                    remain_len -= geo.cosine_law(pol_len, self.ind_all[i][j+self.indsize], self.ind_all[i][j])
                    pol_len = self.ind_all[i][j+self.indsize]
                    
        self.objective_func()
            
            
    
    # 画图
    def draw(self):
    
        # 定义画布
        fig = plt.figure() 
                
        # 绘制椭圆
        draw.draw_oval(self.attack_len, self.attack_platform)
        
        # 绘制圆形障碍
        for circle in self.obstacle:
            draw.draw_circle(circle)
        
        # 绘制转向点
        draw.draw_point(self.global_best, self.launch_platform, self.attack_platform)
            
        
if __name__ == '__main__':
    
    # pso = PSO_Planning(draw_flag = True)
    # pso.PSO()
    # print("PSO:", pso.global_best)
    
    oacrr_pso = PSO_Planning(draw_flag = True)
    oacrr_pso.OACRR_PSO()
    print("OACRR-PSO:", oacrr_pso.global_best)
    
    
    
    
    
    
























