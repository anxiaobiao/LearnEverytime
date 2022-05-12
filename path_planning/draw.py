# -*- coding: utf-8 -*-
"""
Created on Sun Mar 13 11:20:02 2022

@author: Vada
"""

import matplotlib.pyplot as plt
import Geometric_gradient as geo
import math
import numpy as np


def pol_tran_des(polar_diameter, polar_angle):
    
    x = polar_diameter * math.cos(polar_angle)
    y = polar_diameter * math.sin(polar_angle)
    
    return x, y
    
def draw_oval(long_axis, plarform):
    
    
    def_angle, foc_len = plarform[0], plarform[1]
    # 根据极坐标画椭圆
    oval_x, oval_y = [], []
    for polar_angle in np.arange(-math.pi, math.pi, 0.01):
        
        polar_diameter = geo.polar_coordinates(long_axis, foc_len, def_angle, polar_angle)
        x, y = pol_tran_des(polar_diameter, polar_angle)
        
        oval_x.append(x)
        oval_y.append(y)
        
    ax = plt.plot(oval_x, oval_y, linewidth=1)
    
def draw_circle(obstacle):
    
    cir_pol_angle, cir_pol_len, radius = obstacle[0], obstacle[1], obstacle[2]
    # 根据极坐标画圆
    center_x = cir_pol_len * math.cos(cir_pol_angle)
    center_y = cir_pol_len * math.sin(cir_pol_angle)
    
    circle_x, circle_y = [], []
    for polar_angle in np.arange(-math.pi, math.pi, 0.01):
        
        circle_x.append(center_x + radius * math.cos(polar_angle))
        circle_y.append(center_y + radius * math.sin(polar_angle))
    
    ax = plt.plot(circle_x, circle_y, linewidth=2, color='red')
    
def draw_point(points, launch, attack):
    
    point_x, point_y = [], []
    
    point_x.append(attack[1] * math.cos(attack[0]))
    point_y.append(attack[1] * math.sin(attack[0]))
    
    for i in range(int(len(points)/2)):
        point_pol_angle, point_pol_len = points[i], points[i + int(len(points)/2)]
        
        point_x.append(point_pol_len * math.cos(point_pol_angle))
        point_y.append(point_pol_len * math.sin(point_pol_angle))
    
    point_x.append(launch[1] * math.cos(launch[0]))
    point_y.append(launch[1] * math.sin(launch[0]))
    # 绘制端点及转向点
    
    ax = plt.scatter(point_x, point_y, marker = '^')
    ax = plt.plot(point_x, point_y, linewidth=2, color='black')
    
    
    
    
    
    
    
    
    
    
    
    
if __name__ == '__main__':
    
    # 定义画布
    ax = plt.figure() 
    
    # 绘制椭圆
    draw_oval(300, [0, 260])
        
    # oval_x, oval_y = draw_oval(200, 100, 0.3, ax)
    
    # 绘制圆
    draw_circle([math.pi/12, 30, 10])
    
    # 绘制端点
    draw_point([0.2, 0.3, 30, 50], [0, 0], [0, 260])
    
    
    
    
    
    
    