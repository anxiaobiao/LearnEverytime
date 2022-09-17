# -*- coding: utf-8 -*-
"""
Created on Sun Mar 13 10:28:50 2022

@author: Vada
"""
from PSO_Planning import PSO_Planning as PSO
# import numpy as np
import draw
from UI_draw import Figure_Canvas
from path_Thread import Runthread

import matplotlib.pyplot as plt
import copy
import numpy as np
import time
import threading
import math
from random import randint

import matplotlib
matplotlib.use("Qt5Agg")  # 声明使用QT5
import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QVBoxLayout, QWidget, QPushButton, QApplication
from PyQt5 import uic



class UI(QWidget):
    
    def __init__(self):
        super().__init__()
        # 加载主界面文件
        self.ui_main = uic.loadUi("UI/main.ui")
        self.ui_main.show()
        self.ui_main.closeEvent = self.closeEvent
        
        # 加载设置界面
        self.ui_set = uic.loadUi("UI/setting.ui")
        
        # 获得set中的初始数据
        self.get_set()
        
        # 绑定主界面按钮事件
        self.ui_main.start.clicked.connect(self.main_start)
        self.ui_main.set.clicked.connect(self.main_setting)
        self.ui_main.exit.clicked.connect(self.main_exit)
        
        # 绑定设置界面按钮事件
        self.ui_set.ok.clicked.connect(self.set_ok)
        self.ui_set.exit.clicked.connect(self.set_exit)
        self.ui_set.add.clicked.connect(self.set_add)
        self.ui_set.sub.clicked.connect(self.set_sub)
        
        # 设置全局变量
        self.model_list = []
        self.button_list = []
        self.button_layout = QVBoxLayout()
        self.flag = 0
        
        # 初始化进程
        self.thread = None
        
      
    # 获得障碍点
    def set_obstacle(self):
        all_obstacle = []
        for i in range(self.ui_set.tablet.rowCount()):
            temp = []
            for j in range(self.ui_set.tablet.columnCount()):
                temp.append(copy.deepcopy(float(self.ui_set.tablet.item(i, j).text())))
            temp[0], temp[1] = self.des_tran_pol(temp[0], temp[1])
            all_obstacle.append(copy.deepcopy(temp))
            
        return all_obstacle
    
    # 获得数据
    def get_set(self):
        self.loop = int(self.ui_set.loop.text())
        
        self.indsize = int(self.ui_set.indsize.text())
        self.attack_len = int(self.ui_set.attack_len.text())
        self.max_angle = math.pi * 2 * (int(self.ui_set.max_angle.text()) / 360)
        self.min_length = int(self.ui_set.min_length.text())
        
        
        # self.attack_platform = np.array([float(self.ui_set.attack_x.text()), float(self.ui_set.attack_y.text())])
        self.attack_platform = list(self.des_tran_pol(float(self.ui_set.attack_x.text()), float(self.ui_set.attack_y.text())))
        self.launch_platform = np.array([float(self.ui_set.launch_x.text()), float(self.ui_set.launch_y.text())])
        self.obstacle = self.set_obstacle()
        # print(self.ui_set.tablet.item(1,1).text())
        # print(self.attack_platform)
        
        
    # 主界面开始按钮事件
    def main_start(self):
        self.ui_main.start.setEnabled(False)
        self.ui_main.set.setEnabled(False)
        # self.ui_main.exit.setEnabled(False)
        print("main program strating...")
        
        # t = threading.Thread(target=self.start_on, name='t', daemon=True)
        # t.start()
        
        self.button_list = []
        self.model_list = []
        self.button_layout = QVBoxLayout()
        self.Widget = QWidget()
        
        # 创建线程
        self.thread = Runthread(loop = self.loop, indsize = self.indsize, attack_len = self.attack_len,\
                                    max_angle = self.max_angle, min_length = self.min_length, obstacle = self.obstacle, \
                                        attack_platform = self.attack_platform, launch_platform = self.launch_platform)
        # 连接信号
        self.thread._signal.connect(self.main_run)  # 进程连接回传到GUI的事件
        self.thread.daemon=True
        # 开始线程
        self.thread.start()
        
        # self.ui_main.start.setEnabled(True)
        # self.ui_main.set.setEnabled(True)

    def main_run(self, i, oacrr_pso):     
        
        # button_layout.addSpacing(300)
                
        self.Widget.setLayout(self.button_layout)
        
        # print("**************{}*************".format(i))
        
        self.button_list.append(QPushButton(str(i), self))
        self.button_layout.addWidget(self.button_list[i])
        # button_layout.addWidget(QPushButton(str(i), self))
        self.button_list[i].clicked.connect(lambda: self.show_button(self.sender().text()))
        
        self.ui_main.progressBar.setValue((i+1) / self.loop * 100)

        self.model_list.append(copy.deepcopy(oacrr_pso))
            
        # self.ui_main.progressBar.setValue((i+1) / self.loop * 100)
        # if i == 0:
        #     self.thread.terminate()
            
        if i+1 == self.loop:
            self.ui_main.scrollArea.setWidget(self.Widget)
            self.ui_main.start.setEnabled(True)
            self.ui_main.set.setEnabled(True)

        # self.ui_main.exit.setEnabled(True)
    
    # def start_on(self):
        
    #     self.button_list = []
    #     button_layout = QVBoxLayout()
    #     # button_layout.addSpacing(300)
    #     Widget = QWidget()
    #     Widget.setLayout(button_layout)
        
    #     self.model_list = [] 
    #     for i in range(self.loop):
    #     # for i in range(5):
            
            
            
    #         # 设置按钮
    #         # temp.setMinimumHeight(30)
    #         # temp.setMinimumWidth(50)
    #         self.button_list.append(QPushButton(str(i), self))
    #         button_layout.addWidget(self.button_list[i])
    #         # button_layout.addWidget(QPushButton(str(i), self))
    #         self.button_list[i].clicked.connect(lambda: self.show_button(self.sender().text()))
            
    #         self.ui_main.progressBar.setValue(int((i) / self.loop * 100))
    #         # Bar = threading.Thread(target = self.muti_Bar, args=(i))
    #         # Bar.start()
            
    #         # 运行程序
    #         oacrr_pso = PSO(iterations = 200, draw_flag = False, indsize = self.indsize, attack_len = self.attack_len,\
    #                         max_angle = self.max_angle, min_length = self.min_length, obstacle = self.obstacle, \
    #                             attack_platform = self.attack_platform, launch_platform = self.launch_platform)
    #         oacrr_pso.OACRR_PSO()
    #         self.model_list.append(copy.deepcopy(oacrr_pso))
            
    #     self.ui_main.progressBar.setValue(int((i+1) / self.loop * 100))
    #     self.ui_main.scrollArea.setWidget(Widget)
        
    #     self.ui_main.start.setEnabled(True)
    #     self.ui_main.set.setEnabled(True)
    #     # self.ui_main.exit.setEnabled(True)
        
    # 将进度条多线程
    # def muti_Bar(self, i):
    #     self.ui_main.progressBar.setValue((i+1) / self.loop * 100)
    
    # 在graphics绘制图
    def draw_sample(self, pic):
        
        graphicscene = QtWidgets.QGraphicsScene()
        graphicscene.addWidget(pic)
        
        self.ui_main.graphics.setScene(graphicscene)
        self.ui_main.graphics.show()
        
    # 按钮显示的设置
    def show_button(self, number):
        
        print(number)
        
        num = int(number)
        model = self.model_list[num]
        
        pic = Figure_Canvas(model)
        #实例化一个FigureCanvas
        pic.draw_path()    
        # 调用程序
        self.draw_sample(pic)
        
        global_best = []
        for i in range(self.indsize):
            temp = [self.pol_tran_des(model.global_best[i + self.indsize], model.global_best[i])]
            global_best.append(copy.deepcopy(temp))
        global_best.reverse()
        self.ui_main.text.setText("路径为：\n{} \n分数为：{}".format(global_best, model.best_score))
        
        
    # 主界面设置按钮事件
    def main_setting(self):
        print("main_setting...")
        # time.sleep(10)
        self.get_set()
        self.ui_set.show()
        
        
    # 主界面退出按钮事件
    def main_exit(self):
        self.flag = 1
        print("main_exit...")

    # 设置界面确定按钮
    def set_ok(self):
        self.get_set()
        print("set_ok...")
                
    # 设置界面取消按钮
    def set_exit(self):
        self.thread.terminate()
        print("set_exit...")  
        
        
    # 设置界面+号按钮
    def set_add(self):
        row = self.ui_set.tablet.rowCount()
        self.ui_set.tablet.insertRow(row)
    
    # 设置界面-号按钮
    def set_sub(self):
        selected_items = self.ui_set.tablet.selectedItems()
        print(selected_items)
        if len(selected_items) == 0:  # 说明没有选中任何行
            return
        selected_items = [selected_items[i] for i in range(len(selected_items)-1, -1, -7)]
        # 将选定行的行号降序排序，只有从索引大的行开始删除，才不会出现错误
        for items in selected_items:
            self.ui_set.tablet.removeRow(self.ui_set.tablet.indexFromItem(items).row())

    # 极坐标转直角坐标
    def pol_tran_des(self, polar_diameter, polar_angle):
    
        x = round(polar_diameter * math.cos(polar_angle), 2)
        y = round(polar_diameter * math.sin(polar_angle), 2)
        
        return x, y
    
    # 直角坐标转极坐标
    def des_tran_pol(self, x, y):
        
        polar_diameter = math.sqrt(x ** 2 + y ** 2)
        polar_angle = math.atan2(y, x)
        if x == 0:
            polar_angle = math.atan2(x, y)
        
       
        return polar_angle, polar_diameter
    
    def closeEvent(self,event):#函数名固定不可变
        reply=QtWidgets.QMessageBox.question(self,u'警告',u'确认退出?',QtWidgets.QMessageBox.Yes,QtWidgets.QMessageBox.No)
        #QtWidgets.QMessageBox.question(self,u'弹窗名',u'弹窗内容',选项1,选项2)
        if reply==QtWidgets.QMessageBox.Yes:
            self.thread.terminate()
            event.accept()#关闭窗口
        else:
            event.ignore()#忽视点击X事件  
        
        
        
        
        
        
if __name__ == '__main__':
    
    
    app = QApplication(sys.argv)
    ui = UI()
    sys.exit(app.exec_())
    
    