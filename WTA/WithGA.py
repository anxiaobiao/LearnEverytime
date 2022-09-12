# -*- coding: utf-8 -*-
"""
Created on Mon Oct 25 16:31:28 2021

@author: Tom Wade
"""
import numpy as np
import math

class GA():
    def __init__(self, platform, target, target_dict, pop_size, n_generations):
        self.platform = platform        # 发射平台坐标
        self.target_dict = target_dict  # 攻击平台的分配方式：key是目标编号，value是可以分配的发射平台编号
        self.target = target            # 攻击目标
        self.DNA_size = 0
        for i in range(len(target_dict)):
            self.DNA_size += len(self.target_dict[i+1])
        self.pop_size = pop_size
        self.crossover_rate = 0.8
        self.mutation_rate = 0.1
        self.pop = self.codingDNA()
        
        self.n_generations = n_generations
        
        # 目标函数的三个参数
        self.α = 1
        self.β = 1
        self.γ = 0.8    
        
        self.best_DNA = 0               # 最好的基因
        self.best_score = float('-inf') # 最好记忆的分数
        
    # 判断两线段是否相交，相交返回True
    def jud_cross(self, target_1, plarform_1, target_2, plarform_2):
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
    def cross_num(self, temp):
        num = 0
        for j in range(len(temp)):
            for k in temp[j]:
                for m in range(j+1, len(temp)):
                    for n in temp[m]:
                        num += self.jud_cross(self.target[j], self.platform[k-1], self.target[m], self.platform[n-1])
        return num
    
    def attack_sum(self, temp):
        num = 0
        for j in range(len(temp)):
            num += len(temp[j])
        return num
    
    def mean_square_error(self, attack_num, temp):
        Nd = len(temp)
        n_mean = attack_num / Nd
        
        t = 0
        for j in range(Nd):
            t += (len(temp[j]) - n_mean)**2
        ans = math.sqrt(t / Nd)
        return ans
    
    # 目标函数
    def F(self, this_decoded): # list型输入
        nc = self.cross_num(this_decoded)    # nc即航路交叉点个数
        sum_nj = self.attack_sum(this_decoded)      # 攻击目标之和，即sum(nj)
        σn = self.mean_square_error(sum_nj, this_decoded) # 均方差，即σn
        
        bd = self.α * (sum_nj - 2 * nc)
        cm = self.β * sum_nj
        
        if cm == 0:
            return 0
        else:
            return self.γ * (math.exp(bd) / cm) - (1 - self.γ) * σn
        
        
    # 编码操作
    def codingDNA(self):    # 行代表个体基因，列代表基因特征
        pop = np.random.randint(0, 2, (self.pop_size, self.DNA_size))   #随机生成初始种群
        return pop
        
    # 解码操作
    def decoding(self, every_pop):  # every_pop是numpy类型
        begin, end = 0, 0
        answer = []
        for i in range(len(self.target_dict)):
            this_target = np.array(self.target_dict[i+1])
            begin = end
            end += len(this_target)
            this_pop = every_pop[begin:end]
            ans = this_target[this_pop == 1].tolist()
            answer.append(ans)
        return answer
        
    # 交叉操作
    def crossover_and_mutation(self):
        pop_pool = self.pop
        for father in self.pop:
            child = father
            if np.random.rand() > self.crossover_rate:
                mother = self.pop[np.random.randint(0, len(self.pop))]
                crossover_point = np.random.randint(0, self.DNA_size)
                child[crossover_point:] = mother[crossover_point:]
            child = self.mutation(child)
            pop_pool = np.row_stack((pop_pool, child))
        self.select(pop_pool)
        
    # 变异操作
    def mutation(self, child):
        if np.random.rand() > self.mutation_rate:
            mutation_point = np.random.randint(0, self.DNA_size)
            child[mutation_point] ^= 1
        return child
        
    # 选择操作
    def select(self, pop_pool):
        fitness_value = []
        for every_pop in pop_pool:
            fitness_value.append(self.F(self.decoding(every_pop)))
        fitness_value = np.array(fitness_value)
        print(fitness_value)
        self.pop = pop_pool[fitness_value.argsort() > self.pop_size]
        this_best_value = fitness_value[fitness_value.argsort() == 0]
        if this_best_value > self.best_score:
            self.best_score = this_best_value
            self.best_DNA = pop_pool[fitness_value.argsort() == 0]
        print("最佳分数为：{}".format(self.best_score))
        
    # 运行遗传算法
    def run(self):
        # 初始化时以编码完成
        for i in range(self.n_generations):
            print("---------第{}轮遗传算法开始了！！！-----------".format(i+1))
            self.crossover_and_mutation()
        
        
        
if __name__ == '__main__':
    ga = GA()
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    