# -*- coding: utf-8 -*-
"""
Created on Fri Apr  8 10:16:27 2022

@author: Vada
"""
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal
import math
import numpy as np

from PSO_Planning import PSO_Planning as PSO

class Runthread(QtCore.QThread):
    #  通过类成员对象定义信号对象
    _signal = pyqtSignal(int, PSO)
 
    def __init__(self, loop = 30, indsize = 5, attack_len = 300, max_angle = math.pi / 2, min_length = 10, \
                 obstacle = [[math.pi/12, 30, 10], [math.pi/36, 200, 20], [0, 100, 30]], attack_platform = np.array([0.0, 250.0]),\
                     launch_platform = np.array([0.0, 0.0])):
        super(Runthread, self).__init__()
        self.indsize = indsize
        self.attack_len = attack_len
        self.max_angle = max_angle
        self.min_length = min_length
        self.obstacle = obstacle
        self.attack_platform = attack_platform
        self.launch_platform = launch_platform
        self.loop = loop
        
    def __del__(self):
        self.wait()
 
    def run(self):
        for i in range(self.loop):
            oacrr_pso = PSO(iterations = 200, draw_flag = False, indsize = self.indsize, attack_len = self.attack_len,\
                max_angle = self.max_angle, min_length = self.min_length, obstacle = self.obstacle, \
                    attack_platform = self.attack_platform, launch_platform = self.launch_platform)
            oacrr_pso.OACRR_PSO()
            self._signal.emit(i, oacrr_pso) 
