# -*- coding: utf-8 -*-
"""
Created on Wed Apr  6 14:16:04 2022

@author: Vada
"""
import Geometric_gradient as geo
import math
import numpy as np

import matplotlib
matplotlib.use("Qt5Agg")  # 声明使用QT5
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class Figure_Canvas(FigureCanvas):   # 通过继承FigureCanvas类，使得该类既是一个PyQt5的Qwidget，又是一个matplotlib的FigureCanvas，这是连接pyqt5与matplot lib的关键

    def __init__(self, model, parent=None, width=6, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=100)  # 创建一个Figure，注意：该Figure为matplotlib下的figure，不是matplotlib.pyplot下面的figure

        FigureCanvas.__init__(self, fig) # 初始化父类
        self.setParent(parent)
        self.axes = fig.add_subplot(111) # 调用figure下面的add_subplot方法，类似于matplotlib.pyplot下面的subplot方法
        
        self.plarform = model.attack_platform
        self.long_axis = model.attack_len
        self.obstacles = model.obstacle
        self.points = model.global_best
        self.launch = model.launch_platform
        self.attack = model.attack_platform

    def pol_tran_des(self, polar_diameter, polar_angle):
        
        x = polar_diameter * math.cos(polar_angle)
        y = polar_diameter * math.sin(polar_angle)
        
        return x, y
        
    def draw_oval(self):
        
        def_angle, foc_len = self.plarform[0], self.plarform[1]
        # 根据极坐标画椭圆
        oval_x, oval_y = [], []
        for polar_angle in np.arange(-math.pi, math.pi, 0.01):
            
            polar_diameter = geo.polar_coordinates(self.long_axis, foc_len, def_angle, polar_angle)
            x, y = self.pol_tran_des(polar_diameter, polar_angle)
            
            oval_x.append(x)
            oval_y.append(y)
            
        self.axes.plot(oval_x, oval_y, linewidth=1)
        
    def draw_circle(self, obstacle):
        
        cir_pol_angle, cir_pol_len, radius = obstacle[0], obstacle[1], obstacle[2]
        # 根据极坐标画圆
        center_x = cir_pol_len * math.cos(cir_pol_angle)
        center_y = cir_pol_len * math.sin(cir_pol_angle)
        
        circle_x, circle_y = [], []
        for polar_angle in np.arange(-math.pi, math.pi, 0.01):
            
            circle_x.append(center_x + radius * math.cos(polar_angle))
            circle_y.append(center_y + radius * math.sin(polar_angle))
        
        self.axes.plot(circle_x, circle_y, linewidth=2, color='red')
        
    def draw_point(self):
        
        point_x, point_y = [], []
        
        point_x.append(self.attack[1] * math.cos(self.attack[0]))
        point_y.append(self.attack[1] * math.sin(self.attack[0]))
        
        for i in range(int(len(self.points)/2)):
            point_pol_angle, point_pol_len = self.points[i], self.points[i + int(len(self.points)/2)]
            
            point_x.append(point_pol_len * math.cos(point_pol_angle))
            point_y.append(point_pol_len * math.sin(point_pol_angle))
        
        point_x.append(self.launch[1] * math.cos(self.launch[0]))
        point_y.append(self.launch[1] * math.sin(self.launch[0]))
        # 绘制端点及转向点
        
        self.axes.scatter(point_x, point_y, marker = '^')
        self.axes.plot(point_x, point_y, linewidth=2, color='black')
    
    def draw_path(self):
        # 绘制椭圆
        self.draw_oval()
        
        # 绘制圆形障碍
        for circle in self.obstacles:
            self.draw_circle(circle)
    
        # 绘制转向点
        self.draw_point()
    
    def draw_init(self):
        # 绘制椭圆
        self.draw_oval(self.long_axis, self.attack)
        
        # 绘制圆形障碍
        for circle in self.obstacles:
            self.draw_circle(circle)
    
    def test(self):
        x = [1,2,3,4,5,6,7,8,9]
        y = [23,21,32,13,3,132,13,3,1]
        self.axes.plot(x, y)
