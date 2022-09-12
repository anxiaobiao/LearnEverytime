# -*- coding: utf-8 -*-
"""
Created on Tue Jan 11 17:48:46 2022

@author: Tom Wade
"""

from WithGA import GA
import numpy as np
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

if __name__ == '__main__':
    # 初始化
    platform = np.array([[2,6], [3,8], [2,8], [2, 1]])
    target = np.array([[10, 2], [11, 5], [11, 2]])
    critical = 3
    λ = 0.5
    ε1 = 3  
    εn = 2
    
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
    
    # 使用遗传算法求解
    # 参数：platform, target, target_dict, pop_size, n_generations
    use_ga = GA(platform, target_new, target_dict, 10, 10)
    use_ga.run()
    print("最佳DNA为：{}".format(use_ga.best_DNA))
    






























