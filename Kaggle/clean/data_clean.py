# -*- coding: utf-8 -*-
"""
Created on Wed Apr 13 10:48:00 2022

@author: Vada
"""

import pandas as pd
import numpy as np
import copy
import warnings
import random

from sklearn.preprocessing import LabelEncoder
import scipy.stats as st
from scipy.special import boxcox

warnings.filterwarnings("ignore")

# 将特征数据分裂开，方便下一步运算
def data_seg(data):
    
    # 将船舱分割
    # data['deck'], data['num'], data['side'] = data['Cabin'].str.split('/', expand=True)
    new = data['Cabin'].str.split('/', expand=True)
    new.columns = ['deck', 'num', 'side']
    # print(new)
    data = pd.concat([data, new], axis=1)
    data = data.drop('Cabin', axis=1)
    
    # 将名字分割
    new = data['Name'].str.split(' ', expand=True)
    new.columns = ['first_name', 'last_name']
    data = pd.concat([data, new], axis=1)
    data = data.drop('Name', axis=1)
    # data = data.drop('first_name', axis=1)
    
    data = missing_value(data)
    # 再运行一次填充
    data = missing_value(data)
    
    """
    以下为概率填充
    """   
    data.VIP = data.VIP.fillna('False')
    data.Age = data.Age.fillna(random.randint(0,38)) # 75%处
    data.HomePlanet = data.HomePlanet.fillna(random.choice(['Europa', 'Earth', 'Mars']))
    data.Destination = data.Destination.fillna(random.choice(['TRAPPIST-1e', 'PSO J318.5-22', '55 Cancri e']))
    data.RoomService = data.RoomService.fillna(0)
    data.FoodCourt = data.FoodCourt.fillna(0)
    data.ShoppingMall = data.ShoppingMall.fillna(0)
    data.Spa = data.Spa.fillna(0)
    data.VRDeck = data.VRDeck.fillna(0)
    
    # data.side = data.side.fillna(random.choice(['P', 'S']))
    
    # 填充Cabin的数据
    data = missing_Cabin(data)
    # missing_Cabin(data)
    
    # 去除掉名字，及认为名字对是否前往异时空为多余特征
    data = data.drop('first_name', axis=1)
    data = data.drop('last_name', axis=1)
    
    # 编码
    data = coding(data)
    
    return data
    
# 对于缺失值的填补工作
def missing_value(data):
    
    # 获取星球全部的姓
    Europa_name = data[data.HomePlanet == 'Europa'].last_name.unique()
    Earth_name = data[data.HomePlanet == 'Earth'].last_name.unique()
    Mars_name = data[data.HomePlanet == 'Mars'].last_name.unique()
    
    Europa_first = data[data.HomePlanet == 'Europa'].first_name.unique()
    Earth_first = data[data.HomePlanet == 'Earth'].first_name.unique()
    Mars_first = data[data.HomePlanet == 'Mars'].first_name.unique()
    
    last_value = data.iloc[0]   # 上行数据
    last_index = data.index[0]
    for index, row in data.iterrows():
        this_value = row        # 本行数据
        
        # PassengerId 的前四位一样为一组，具有类似性质
        if index[:4] == last_index[:4]:
            if pd.isnull(this_value['HomePlanet']):
                this_value['HomePlanet'] = last_value['HomePlanet']
            if pd.isnull(this_value['Destination']):
                this_value['Destination'] = last_value['Destination']
            if pd.isnull(this_value['deck']) or pd.isnull(this_value['num']) or pd.isnull(this_value['side']):
                this_value['deck'] = last_value['deck']
                this_value['num'] = last_value['num']
                this_value['side'] = last_value['side']
            if pd.isnull(this_value['last_name']):
                this_value['last_name'] = last_value['last_name']
            if pd.isnull(this_value['first_name']):
                this_value['first_name'] = last_value['first_name']
                
        if index[:4] == last_index[:4]:
            if pd.isnull(last_value['HomePlanet']):
                last_value['HomePlanet'] = this_value['HomePlanet']
            if pd.isnull(last_value['Destination']):
                last_value['Destination'] = this_value['Destination']
            if pd.isnull(last_value['deck']) or pd.isnull(this_value['num']) or pd.isnull(this_value['side']):
                last_value['deck'] = this_value['deck']
                last_value['num'] = this_value['num']
                last_value['side'] = this_value['side']
            if pd.isnull(last_value['last_name']):
                last_value['last_name'] = this_value['last_name']
            if pd.isnull(last_value['first_name']):
                last_value['first_name'] = this_value['first_name']
        
        # 某个姓氏可能是在独特的星球上
        if pd.isnull(this_value['HomePlanet']) and (this_value['last_name'] in Europa_name) and (this_value['last_name'] not in Earth_name) and (this_value['last_name'] not in Mars_name):
              this_value['HomePlanet'] = 'Europa'
        if pd.isnull(this_value['HomePlanet']) and this_value['last_name'] not in Europa_name and this_value['last_name'] in Earth_name and this_value['last_name'] not in Mars_name:
              this_value['HomePlanet'] = 'Earth'
        if pd.isnull(this_value['HomePlanet']) and this_value['last_name'] not in Europa_name and this_value['last_name'] not in Earth_name and this_value['last_name'] in Mars_name:
              this_value['HomePlanet'] = 'Mars'
              
        # 名字也可能在某个特殊的星球上
        if pd.isnull(this_value['HomePlanet']) and this_value['first_name'] in Europa_first and (this_value['first_name'] not in Earth_first) and (this_value['first_name'] not in Mars_first):
              this_value['HomePlanet'] = 'Europa'
        if pd.isnull(this_value['HomePlanet']) and this_value['first_name'] not in Europa_first and this_value['first_name'] in Earth_first and this_value['first_name'] not in Mars_first:
              this_value['HomePlanet'] = 'Earth'
        if pd.isnull(this_value['HomePlanet']) and this_value['first_name'] not in Europa_first and this_value['first_name'] not in Earth_first and this_value['first_name'] in Mars_first:
              this_value['HomePlanet'] = 'Mars'
        
        # CryoSleep==True或Age<=12的人必定没有账单
        if row['CryoSleep'] or row['Age'] <= 12:
            this_value['RoomService'] = 0
            this_value['FoodCourt'] = 0
            this_value['ShoppingMall'] = 0
            this_value['Spa'] = 0
            this_value['VRDeck'] = 0
        
        # last_name与cabin的强关联情况
        if (pd.isnull(this_value['last_name']) and (this_value['deck'] == last_value['deck'] and this_value['num'] == last_value['num'] and this_value['side'] == last_value['side'])):
            this_value['last_name'] = last_value['last_name']
        if (pd.isnull(last_value['last_name']) and (this_value['deck'] == last_value['deck'] and this_value['num'] == last_value['num'] and this_value['side'] == last_value['side'])):
            last_value['last_name'] = this_value['last_name']
            data.loc[last_index] = last_value
        
        if (pd.isnull(this_value['deck']) and (this_value['last_name'] == last_value['last_name'])):
            this_value['deck'] = last_value['deck']
            this_value['num'] = last_value['num']
            this_value['side'] = last_value['side']
        if (pd.isnull(last_value['deck']) and (this_value['last_name'] == last_value['last_name'])):
            last_value['deck'] = this_value['deck']
            last_value['num'] = this_value['num']
            last_value['side'] = this_value['side']
            data.loc[last_index] = last_value
            
        # HomePlanet与cabin或last_name具有强相关
        if (pd.isnull(this_value['HomePlanet']) and ((this_value['deck'] == last_value['deck'] and this_value['num'] == last_value['num'] and this_value['side'] == last_value['side']) or this_value['last_name'] == last_value['last_name'])):
            this_value['HomePlanet'] = last_value['HomePlanet']
        if (pd.isnull(last_value['HomePlanet']) and ((this_value['deck'] == last_value['deck'] and this_value['num'] == last_value['num'] and this_value['side'] == last_value['side']) or this_value['last_name'] == last_value['last_name'])):
            last_value['HomePlanet'] = this_value['HomePlanet']
            data.loc[last_index] = last_value
            
        # Destination与cabin或last_name具有强相关
        if (pd.isnull(this_value['Destination']) and ((this_value['deck'] == last_value['deck'] and this_value['num'] == last_value['num'] and this_value['side'] == last_value['side']) or this_value['last_name'] == last_value['last_name'])):
            this_value['Destination'] = last_value['Destination']
        if (pd.isnull(last_value['Destination']) and ((this_value['deck'] == last_value['deck'] and this_value['num'] == last_value['num'] and this_value['side'] == last_value['side']) or this_value['last_name'] == last_value['last_name'])):
            last_value['Destination'] = this_value['Destination']
            data.loc[last_index] = last_value
            
        # 如果星球为Earth, VIP必为false
        if pd.isnull(this_value['VIP']) and this_value['HomePlanet'] == 'Earth':
            this_value['VIP'] = False
        # Mars的vip是>18岁, 没有假睡，没有去PSO星球的
        if pd.isnull(this_value['VIP']) and this_value['HomePlanet'] == 'Mars' and this_value['Age'] >= 18 and this_value['CryoSleep'] == False and this_value['Destination'] == 'PSO J318.5-22':
            this_value['VIP'] = True
        # Europa的vip是>=25岁
        if pd.isnull(this_value['VIP']) and this_value['HomePlanet'] == 'Europa' and this_value['Age'] >= 25:
            this_value['VIP'] = True

        # 如果是同组 
        this_bill = this_value['RoomService'] + this_value['FoodCourt'] + this_value['ShoppingMall'] + this_value['Spa'] + this_value['VRDeck']
        last_bill = last_value['RoomService'] + last_value['FoodCourt'] + last_value['ShoppingMall'] + last_value['Spa'] + last_value['VRDeck']        
        if this_value['last_name'] == last_value['last_name']:
            
            # 没有账单的 Earth on G   Europa on B   Mars on E or F
            if pd.isnull(this_value['deck']) and this_bill == 0:
                if this_value['HomePlanet'] == 'Earth':
                    this_value["deck"] = 'G'
                if this_value['HomePlanet'] == 'Europa':
                    this_value["deck"] = 'B'
                if this_value['HomePlanet'] == 'Mars':
                    this_value["deck"] = random.choice(['E', 'F'])
            if pd.isnull(last_value['deck']) and last_bill == 0:
                if last_value['HomePlanet'] == 'Earth':
                    last_value["deck"] = 'G'
                if last_value['HomePlanet'] == 'Europa':
                    last_value["deck"] = 'B'
                if last_value['HomePlanet'] == 'Mars':
                    last_value["deck"] = random.choice(['E', 'F'])
                data.loc[last_index] = last_value
            
            # side在同侧
            if pd.isnull(this_value['side']):
                this_value["side"] = last_value["side"]
            if pd.isnull(last_value['side']):
                last_value["side"] = this_value["side"]
                data.loc[last_index] = last_value
                
        # 如果在Europa并且没有账单 deck = B
        if pd.isnull(this_value['deck']) and this_bill == 0 and this_value['HomePlanet'] == 'Europa':
              this_value['deck'] = 'B'
                
        # # Earth on E, F, G    Mars on D, E, F    Europa on A, B, C, D, E, T
        # if pd.isnull(this_value['deck']) and this_value['HomePlanet'] == 'Earth':
        #       this_value['deck'] = random.choice(['E', 'F', 'G'])
        # if pd.isnull(this_value['deck']) and this_value['HomePlanet'] == 'Mars':
        #       this_value['deck'] = random.choice(['D', 'E', 'F'])
        # if pd.isnull(this_value['deck']) and this_value['HomePlanet'] == 'Europa':
        #       this_value['deck'] = random.choice(['A', 'B', 'C', 'D', 'E', 'T'])
        
        # 如果age>12并且账单为0假死
        if pd.isnull(this_value['CryoSleep']) and this_bill == 0:
            this_value['CryoSleep'] = True
            
        # age>12 and 不是假睡 and 没有账单 都是取得TRAPPIST-1e
        if pd.isnull(this_value['Destination']) and this_value['Age'] > 12 and this_value['CryoSleep'] == False and this_bill == 0:
            this_value['Destination'] = 'TRAPPIST-1e'
        
        # Europa年龄<25的不去PSO J318.5-22 (多了一个， 用处不大)
        if pd.isnull(this_value['Destination']) and this_value['HomePlanet'] == 'Europa' and this_value['Age'] < 25:
            this_value['Destination'] = random.choice(['TRAPPIST-1e', '55 Cancri e'])
        
        # 五个金钱的方面，若一个为空，采用其余四个的均值作为空的值
        if pd.isnull(this_value['RoomService']) and not(pd.isnull(this_value['FoodCourt']) or pd.isnull(this_value['ShoppingMall']) or pd.isnull(this_value['Spa']) or pd.isnull(this_value['VRDeck'])):
            this_value['RoomService'] = int((this_value['FoodCourt'] + this_value['ShoppingMall'] + this_value['Spa'] + this_value['VRDeck']) / 4)
        if pd.isnull(this_value['FoodCourt']) and not(pd.isnull(this_value['RoomService']) or pd.isnull(this_value['ShoppingMall']) or pd.isnull(this_value['Spa']) or pd.isnull(this_value['VRDeck'])):
            this_value['FoodCourt'] = int((this_value['RoomService'] + this_value['ShoppingMall'] + this_value['Spa'] + this_value['VRDeck']) / 4)
        if pd.isnull(this_value['ShoppingMall']) and not(pd.isnull(this_value['FoodCourt']) or pd.isnull(this_value['RoomService']) or pd.isnull(this_value['Spa']) or pd.isnull(this_value['VRDeck'])):
            this_value['ShoppingMall'] = int((this_value['FoodCourt'] + this_value['RoomService'] + this_value['Spa'] + this_value['VRDeck']) / 4)
        if pd.isnull(this_value['Spa']) and not(pd.isnull(this_value['FoodCourt']) or pd.isnull(this_value['ShoppingMall']) or pd.isnull(this_value['RoomService']) or pd.isnull(this_value['VRDeck'])):
            this_value['Spa'] = int((this_value['FoodCourt'] + this_value['ShoppingMall'] + this_value['RoomService'] + this_value['VRDeck']) / 4)
        if pd.isnull(this_value['VRDeck']) and not(pd.isnull(this_value['FoodCourt']) or pd.isnull(this_value['ShoppingMall']) or pd.isnull(this_value['Spa']) or pd.isnull(this_value['RoomService'])):
            this_value['VRDeck'] = int((this_value['FoodCourt'] + this_value['ShoppingMall'] + this_value['Spa'] + this_value['RoomService']) / 4)

        data.loc[index] = this_value
        last_value = data.loc[index]   # 上行数据
        last_index = index

    return data
    
# 填充Cabin数据
def missing_Cabin(data):
    
    col = data.columns
    
    Europa_data = pd.DataFrame(columns = col)
    Earth_data = pd.DataFrame(columns = col)
    Mars_data = pd.DataFrame(columns = col)
    Miss_data = pd.DataFrame(columns = col)
    
    Europa_data.index.name = 'PassengerId'
    Earth_data.index.name = 'PassengerId'
    Mars_data.index.name = 'PassengerId'
    Miss_data.index.name = 'PassengerId'
    
    # 将数据分类
    for index, row in data.iterrows():
        
        this_value = row
        if pd.isnull(this_value['deck']) and pd.isnull(this_value['num']) and pd.isnull(this_value['side']):
            Miss_data.loc[index] = this_value
        elif this_value['HomePlanet'] == 'Europa':
            Europa_data.loc[index] = this_value
        elif this_value['HomePlanet'] == 'Earth':
            Earth_data.loc[index] = this_value
        elif this_value['HomePlanet'] == 'Mars':
            Mars_data.loc[index] = this_value
    
    # 排序
    Miss_data = Miss_data.sort_values(by=['deck', 'side', 'PassengerId'])
    Europa_data = Europa_data.sort_values(by=['deck', 'side', 'PassengerId'])
    Earth_data = Earth_data.sort_values(by=['deck', 'side', 'PassengerId'])
    Mars_data = Mars_data.sort_values(by=['deck', 'side', 'PassengerId'])
    
    # 首先将非全空的数据填补上
    last = Europa_data.iloc[0]
    for index, row in Europa_data.iterrows():
        if pd.isnull(row['side']):
            row['side'] = last['side']
        if pd.isnull(row['num']):
            row['num'] = int(last['num']) + 1
        Europa_data.loc[index] = row
    
    last = Earth_data.iloc[0]
    for index, row in Earth_data.iterrows():
        if pd.isnull(row['side']):
            row['side'] = last['side']
        if pd.isnull(row['num']):
            row['num'] = int(last['num']) + 1
        Earth_data.loc[index] = row
    
    last = Mars_data.iloc[0]
    for index, row in Mars_data.iterrows():
        if pd.isnull(row['side']):
            row['side'] = last['side']
        if pd.isnull(row['num']):
            row['num'] = int(last['num']) + 1
        Mars_data.loc[index] = row
        
    
    
    for miss_index, miss_row in Miss_data.iterrows():
        # and int(last_data['num']) < int(miss_row['num']) and int(Europa_row['num']) > int(miss_row['num'])
        # 判断Europa
        if miss_row['HomePlanet'] == 'Europa':
            last_data = Europa_data.iloc[0]
            last_index = Europa_data.index[0]
            for Europa_index, Europa_row in Europa_data.iterrows():
                if int(last_index[:4]) < int(miss_index[:4]) and int(Europa_index[:4]) > int(miss_index[:4]):
                    miss_row['deck'] = last_data['deck']
                    miss_row['side'] = last_data['side']
                    miss_row['num'] = int(last_data['num']) + 1
                    
                    Europa_data.loc[miss_index] = miss_row
                    Europa_data = Europa_data.sort_values(by=['deck', 'side', 'PassengerId'])
                    break
                last_data = Europa_row
                last_index = Europa_index
        
        # 判断Earth
        if miss_row['HomePlanet'] == 'Earth':
            last_data = Earth_data.iloc[0]
            last_index = Earth_data.index[0]
            for Earth_index, Earth_row in Earth_data.iterrows():
                if int(last_index[:4]) < int(miss_index[:4]) and int(Earth_index[:4]) > int(miss_index[:4]):
                    miss_row['deck'] = last_data['deck']
                    miss_row['side'] = last_data['side']
                    miss_row['num'] = int(last_data['num']) + 1
                    
                    Earth_data.loc[miss_index] = miss_row
                    Earth_data = Earth_data.sort_values(by=['deck', 'side', 'PassengerId'])
                    break
                last_data = Earth_row
                last_index = Earth_index
                
        # 判断Mars
        if miss_row['HomePlanet'] == 'Mars':
            last_data = Mars_data.iloc[0]
            last_index = Mars_data.index[0]
            
            last_bill = last_data['RoomService'] + last_data['FoodCourt'] + last_data['ShoppingMall'] + last_data['Spa'] + last_data['VRDeck']        

            for Mars_index, Mars_row in Mars_data.iterrows():
                # this_bill = Mars_row['RoomService'] + Mars_row['FoodCourt'] + Mars_row['ShoppingMall'] + Mars_row['Spa'] + Mars_row['VRDeck']
                if int(last_index[:4]) < int(miss_index[:4]) and int(Mars_index[:4]) > int(miss_index[:4]):
                    if last_bill == 0 and last_data['deck'] == 'D':
                        last_bill = Mars_row['RoomService'] + Mars_row['FoodCourt'] + Mars_row['ShoppingMall'] + Mars_row['Spa'] + Mars_row['VRDeck']
                        continue
                    miss_row['deck'] = last_data['deck']
                    miss_row['side'] = last_data['side']
                    miss_row['num'] = int(last_data['num']) + 1
                    
                    Mars_data.loc[miss_index] = miss_row
                    Mars_data = Mars_data.sort_values(by=['deck', 'side', 'PassengerId'])
                    break
                last_data = Mars_row
                last_index = Mars_index
             
    data = pd.concat([Earth_data, Europa_data, Mars_data])
    data = data.sort_values(by=['PassengerId'])
    # return Europa_data, Earth_data, Mars_data, Miss_data
    return data
    
# 编码操作
def coding(data):
    
    data['num'] = data['num'].astype(int)
    
    # 对非数值型数据编码
    need_coding = ('HomePlanet', 'CryoSleep', 'Destination', 'VIP', 'deck', 'side')
    for coding in need_coding:
        lbl = LabelEncoder()  # 转化为0到n-1的值(n为个数)
        lbl.fit(list(data[coding].values))
        data[coding] = lbl.transform(list(data[coding].values))
        
    # 计算偏差，多余偏差大于 1 的最正态化处理
    skew_num = st.skew(data)
    index = data.columns
    need_trans = index[abs(skew_num) > 1]
    for trans in need_trans:
           data[trans] = boxcox(data[trans], 0.05)
          # data[trans] = st.boxcox1p(data[trans])
        
    data = data[index[abs(st.skew(data)) < 1]]       # 删去了 VIP 和Destination，因为处理后的偏差依然很大
    
    # 使用ont-hot编码
    data = pd.get_dummies(data)
    
    return data
    

if __name__ == '__main__':
    
    # train数据清洗
    train_read = pd.read_csv('../data/train.csv', index_col=0)
    
    train_y = pd.DataFrame(train_read['Transported'])
    train_x = train_read.drop('Transported', axis=1)
    train_x = data_seg(train_x)
    
    
    # test数据清洗
    test_read = pd.read_csv('../data/test.csv', index_col=0)
    
    # test_y = pd.DataFrame(test_read['Transported'])
    # test_x = test_read.drop('Transported', axis=1)
    test_x = data_seg(test_read)
    
    
    
    # 数据汇总保存
    train = pd.concat([train_x, train_y], axis=1)
    # test = pd.concat([test_x, test_y], axis=1)
    test = test_x   

    train.to_csv("train.csv")
    test.to_csv("test.csv")
    
    
    
    