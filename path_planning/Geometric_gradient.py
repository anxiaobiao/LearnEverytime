# -*- coding: utf-8 -*-
"""
Created on Thu Mar 10 08:49:09 2022

@author: Vada
"""

import numpy as np
import math
import matplotlib as mpl
import matplotlib.pyplot as plt

# mpl.rcParams["font.sans-serif"] = ["SimHei"]

def cosine_law(focal_length, polar_diameter, polar_angle):
    """
    本函数是正弦函数
    
    Parameters
    ----------
    focal_length : float
        当前椭圆的焦距（发射点与攻击点的距离）
    polar_diameter : float
        极径（发射点到转向点的长度）
    polar_angle : float
        极角（发射点到转向点与当前椭圆极轴的角度）

    Returns
    -------
    float
        目标点到转向点的距离

    """
    l_i = math.sqrt(focal_length ** 2 + polar_diameter ** 2 - 2 * focal_length * polar_diameter * math.cos(polar_angle))
    return l_i

def polar_coordinates(remaining_path, d_i, sum_angle, independent_variable):
    """
    本函数是返回根据参数形成椭圆的极径范围，确保规划途中不会出现超出椭圆路径的点
    
    Parameters
    ----------
    remaining_path : float
        剩余路径（本椭圆的长轴）
    d_i : float
        本椭圆的焦点距
    sum_angle : float
        之前的旋转角度（以极轴为基准，向上为正，向下为负）
    independent_variable : float
        自变量，即椭圆内所选点的极角

    Returns
    -------
    float
        因变量，即椭圆内所选点的极径的最大值
        后续使用是需要其与智能算法的制定极径作比较，要有其大于所选的极径

    """
    up = (remaining_path) ** 2 - d_i ** 2
    down = 2 * (remaining_path) - 2 * d_i * np.cos(independent_variable - sum_angle)
    
    return up / down

def draw(theta, remaining_path, d_i, sum_angle):
    
    ax4= plt.subplot(polar =True)#使用极坐标
    
    ax4.plot(theta, polar_coordinates(remaining_path, d_i, sum_angle, theta),'m-') #椭圆

if __name__ == '__main__':
    """
    假设发射平台为极点
    公式3.12，P61
    s: 最大发射距离
    polar_diameter: 焦点距
    l_i: 已使用的飞行路径
    """
    s = 100
    launch_platform = np.array([0, 0])
    attack_platform = np.array([70, 0])
    
    d = attack_platform[0] - launch_platform[0]
    remaining_focal = d    # 自减20
    remaining_angle = 0     # 自加pi/18,循环4次
    
    ans_all = []
    
    for i in range(4):
        ans = [s, remaining_focal, remaining_angle]
        ans_all.append(ans)
        
        theta=np.arange(0,2*math.pi,0.02)   #极角，弧度制
        
        l_i = cosine_law(d, remaining_focal, remaining_angle)

        # draw(theta, s-l_i, remaining_focal, remaining_angle)
        
        s -= l_i
        remaining_focal -= 20
        remaining_angle += math.pi/9
        
    ax4= plt.subplot(polar =True)#使用极坐标
    
    ax4.plot(theta, polar_coordinates(ans_all[0][0], ans_all[0][1], ans_all[0][2], theta),'m-') #椭圆
    ax4.plot(theta, polar_coordinates(ans_all[1][0], ans_all[1][1], ans_all[1][2], theta),'r-') #椭圆
    ax4.plot(theta, polar_coordinates(ans_all[2][0], ans_all[2][1], ans_all[2][2], theta),'b-') #椭圆





