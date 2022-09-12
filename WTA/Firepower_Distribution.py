# -*- coding: utf-8 -*-
"""
Created on Mon Oct 25 16:29:45 2021

@author: Tom Wade
"""

import numpy as np
import matplotlib.pyplot as plt
import math
from itertools import combinations

# 计算散布中心
def Scatt_center(CoorCluster):
    while(len(CoorCluster)):
        # 散布中心
        temp = (sum(CoorCluster) / len(CoorCluster)).reshape(1, 2)
        # 求距离
        dis = pow(((CoorCluster - temp) ** 2).sum(1), 0.5)
        # 临界值critical的选取
        leftover = dis < critical
        if leftover.all():
            return temp
        CoorCluster = CoorCluster[leftover]
        
# 求基线角
def Center_angle(platform_center, target_center):
    temp = math.atan((target_center[0, 1] - platform_center[0, 1]) / (target_center[0, 0] - platform_center[0, 0]))
    if platform_center[0, 0] < target_center[0, 0] and platform_center[0, 1] <= target_center[0, 1]:
        return temp
    elif platform_center[0, 0] == target_center[0, 0] and platform_center[0, 1] < target_center[0, 1]:
        return math.pi / 2
    elif platform_center[0, 0] > target_center[0, 0]:
        return math.pi + temp
    elif platform_center[0, 0] == target_center[0, 0] and platform_center[0, 1] > target_center[0, 1]:
        return math.pi * 3 / 2
    elif platform_center[0, 0] < target_center[0, 0] and platform_center[0, 1] > target_center[0, 1]:
        return math.pi * 2 + temp

# 将发射平台和目标的地理转换为相应的基线坐标和发现坐标
def trans(CoorCluster, center, angle):
    temp = center - CoorCluster
    ConEqu = np.array([[math.cos(angle), math.sin(angle)], [-math.sin(angle), math.cos(angle)]])
    return (ConEqu @ temp.T).T

def AreaFireDis(platform_trans, target_trans, λ, ε1, εn):
    area = []
    for i in range(1, len(platform_trans)):
        temp = λ * platform_trans[i-1, 1] + (1 - λ) * platform_trans[i, 1]
        area.append(temp) 
    area.insert(0, area[0] + ε1)
    area.append(area[-1] - εn)
    area = np.array(area)
    
    target_dict = {}
    j = 0
    for i in range(len(area)):
        if target_trans[j, 1] > area[i]:
            while(j < len(target_trans) and target_trans[j, 1] > area[i]):
                j = j + 1
                if i == 0:
                    temp = {j : [1]}
                elif i == 1:
                    temp = {j : [1, 2]}
                elif i == len(area) - 1:
                    temp = {j : [len(area) - 2, len(area) - 1]}
                else:
                    temp = {j : [i-1, i, i+1]}
                target_dict.update(temp)
    return target_dict

# 同区目标归为一个目标
def target_norm(target_dict, target_trans, target):
    temp = {}
    for key, value in target_dict.items():
        if str(value) in temp:
            temp[str(value)].append(key)
        else:
            temp[str(value)] = [key]
    
    target_return = np.zeros((len(temp), 2))
    i = 0
    
    for key, value in temp.items():
        value = list((np.array(value) - np.ones(len(value))).astype(int))
        if len(value) >= 2:
            target_return[i] = sum(target[value]) / len(value)
        else:
            target_return[i] = target[value]
        i = i + 1
    
    for key, value in temp.items():
        if len(value) >= 2:
            value.pop()
            for i in value:
                target_dict.pop(i)
    
    n = len(target_dict)
    key_list = list(target_dict.keys())
    for i in range(n):
        target_dict[i+1] = target_dict[key_list[i]]
        del target_dict[key_list[i]]
    
    return target_return

# 返回分配的全部解空间
def permutations(target_dict):
    t_dict = {}
    for i in range(len(target_dict)):
        temp = target_dict[i+1]
        t = []
        for j in range(1,len(temp)+1):
            for k in combinations(temp, j):
                t.append(list(k))
                # t.append(k)
        t = {i : t}
        t_dict.update(t)
    
    # print(t_dict)
    num = 1
    for i in range(len(t_dict)):
        num *= len(t_dict[i])
    
    distributed_num = np.zeros((num, len(target_dict))).astype(int)
    temp = np.zeros((1, len(target_dict))).astype(int)
    temp_end = np.zeros((1, len(target_dict))).astype(int)
    for i in range(len(target_dict)):
        temp_end[0,i] = len(t_dict[i])
    
    n = 0
    while((temp != temp_end).all()):
        distributed_num[n] = temp
        n += 1
        temp[0, -1] += 1
        for i in range(len(target_dict)-1, 0, -1):
            if temp[0, i] == temp_end[0, i]:
                temp[0, i] = 0
                temp[0, i-1] += 1

    distributed = []
    for i in range(len(distributed_num)):
        temp = []
        for j in range(len(distributed_num.T)):
            temp.append(t_dict[j][distributed_num[i, j]])
        distributed.append(temp)
    
    return distributed
    
# 判断两线段是否相交，相交返回True
def jud_cross(target_1, plarform_1, target_2, plarform_2):
    if max(plarform_1[0], target_1[0]) < min(plarform_2[0], target_2[0]) or \
        max(plarform_2[0], target_2[0]) < min(plarform_1[0], target_1[0]) or \
        max(plarform_1[1], target_1[1]) < min(plarform_2[1], target_2[1]) or \
        max(plarform_2[1], target_2[1]) < min(plarform_1[1], target_1[1]):
        return False
    if(np.cross(plarform_1 - plarform_2, target_2 - plarform_2) * np.cross(target_1 - plarform_2, target_2 - plarform_2) >= 0 or \
       np.cross(plarform_2 - plarform_1, target_1 - plarform_1) * np.cross(target_2 - plarform_1, target_1 - plarform_1) >= 0):
        return False
    return True

# 求取各解空间的相交路线的数量
def cross_num(platform, target, distributed):
    NumberOfCross = np.zeros((len(distributed), 1))
    for i in range(len(distributed)):
        temp = distributed[i]
        num = 0
        for j in range(len(temp)):
            for k in temp[j]:
                for m in range(j+1, len(temp)):
                    for n in temp[m]:
                        num += jud_cross(target[j], platform[k-1], target[m], platform[n-1])
        NumberOfCross[i, 0] = num
    return NumberOfCross
    
# 计算攻击总数
def attack_num(distributed):
    # distributed = np.array(distributed)
    attack = np.zeros((len(distributed) ,1))
    for i in range(len(distributed)):
        num = 0
        for j in range(len(distributed[0])):
            num += len(distributed[i][j])
        attack[i] = num
    return attack

# 求均方差
def mean_square_error(attack_num, distributed):
    Nd = len(distributed[0])
    n_mean = attack_num / Nd
    
    temp = np.zeros((len(distributed) ,1))
    
    for i in range(len(distributed)):
        t = 0
        for j in range(Nd):
            t += len((distributed[i][j] - n_mean[i])**2)
        temp[i] = math.sqrt(t / Nd)
    return temp
    
# 汇总
def summary(cross_num, attack_num, σn):
    temp = np.zeros((len(cross_num), 3))
    temp[:,0] = attack_num[:,0]
    temp[:,1] = cross_num[:,0]
    temp[:,2] = σn[:,0]
    return temp
    
    
# 画图
def draw(platform, target_new):
    for i in range(len(platform)):
        plt.scatter(platform[i, 0], platform[i, 1])
    for i in range(len(target_new)):
        plt.scatter(target_new[i, 0], target_new[i, 1])

if __name__ == '__main__':
    # 初始化
    platform = np.array([[50,1000], [67,850], [59,660], [76, 590], [63, 200]])
    target = np.array([[2500, 900], [2980, 600], [2290, 350]])
    critical = 200
    λ = 0.5
    ε1 = 10  
    εn = 10
    
    # 预处理，方便后续运行
    platform = platform[np.argsort(platform[:, 1]), :]
    target = target[np.argsort(target[:, 1]), :]
    
    # 第一部分
    platform_center = Scatt_center(platform)
    target_center = Scatt_center(target)
    AngleOfCenter = Center_angle(platform_center, target_center)
    platform_trans = trans(platform, platform_center, AngleOfCenter)
    target_trans = trans(target, target_center, AngleOfCenter)
    
    # 第二部分，key是目标编号，value是发射平台编号
    target_dict = AreaFireDis(platform_trans, target_trans, λ, ε1, εn)
    
    # 将分在同一个区的目标化为一个目标
    target_new = target_norm(target_dict, target_trans, target)
    
    # 数组的自由组合，结果是发射平台编号，第几列就是第几个目标，本例是两个目标
    distributed = permutations(target_dict)
    
    # 相交数量,即nc
    cross_num = cross_num(platform, target_new, distributed)
    
    # 目标的被攻击平台总数，即sum(nj)
    attack_num = attack_num(distributed)
    
    # 均方差，即σn
    σn = mean_square_error(attack_num, distributed)
    
    # 将上述三个结果汇总到一个数组中，顺序是sum(nj)， nc， σn
    ans = summary(cross_num, attack_num, σn)
    
    # 画图
    # draw(platform, target_new)
    
    # return ans
    
    
    
    