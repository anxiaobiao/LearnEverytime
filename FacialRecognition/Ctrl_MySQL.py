# -*- coding: utf-8 -*-
"""
Created on Mon Oct 25 15:21:58 2021

@author: Tom Wade
"""

import pymysql
import time

connection = pymysql.connect(host='127.0.0.1', user='root', password='123456',
                             database='temp', port=3306)

def mysql_no_return(sql):
    cursor = connection.cursor()
    cursor.execute(sql)
    connection.commit()
    # print(cursor.rowcount)
    # sql = "insert into temp (id, 1点) VALUES (%s, %s)" %('4', '2.30')

# face_id = input('\n enter user id end press <return> ==>  ')
# name = input('\n enter user name end press <return> ==>  ')
# name = "'{}'".format(name)
# face_id, name = 1, "'as'"
# temp_table = "'t_{}'".format(face_id)
#
# sql = "insert into temp (id, name, temp_table) VALUES ({}, {}, {})".format(face_id, name, temp_table)
# mysql_no_return(sql)

# t = int(time.strftime('%H',time.localtime(time.time()))) 
 
# def update(sql):
#     cursor = connection.cursor()
#     cursor.execute(sql)
#     connection.commit()
    # print(cursor.rowcount)
    
    # sql = "update temp set 1点='37' where id = 1"
    # update(sql)

def mysql_return(sql):
    cursor = connection.cursor()
    cursor.execute(sql)
    results = cursor.fetchall()
    return results

# sql = "select 1点 from temp where id=2"
# a = get(sql)

# 查看是否表存在
# sql = "select * from information_schema.tables where table_name ='temp';"
# a = get(sql)  # 0不存在 1存在

# sql = "CREATE TABLE if not exists t_{} (time varchar(11), 8点 varchar(11), 10点 varchar(11), 14点 varchar(11), 16点 varchar(11), 19点 varchar(11), 21点 varchar(11));".format(1)
# mysql_no_return(sql)

# a = 3
# b = '输出{}'.format(a)
# print(b)


# time的更新
# sql = "CREATE TABLE if not exists t (time varchar(20), 1点 varchar(11), 10点 varchar(11));"
# mysql_no_return(sql)

# a = (time.strftime('%Y-%m-%d',time.localtime(time.time())))
# a = "'{}'".format(a)

# sql = " select time from t order by time desc limit 0,1"
# c = mysql_return(sql)
# c = "'{}'".format(c[0][0])
# if c != a:
#     sql = "insert into t (time) VALUES ({})".format(a)
#     mysql_no_return(sql)

# a = (time.strftime('%Y-%m-%d',time.localtime(time.time())))
# a = "'{}'".format(a)
# # b = int((time.strftime('%H',time.localtime(time.time()))))
# b = 15
# if b <12 and b >= 8:
#     temp = '上午'
# if b >= 12 and b < 18:
#     temp = '下午'
# if b >= 18 and b < 23:
#     temp = '晚上'
# if b >= 23 or b < 8:
#     temp = '凌晨'
#
# sql = "update {} set {}='37' where time = {}".format('t_2', temp, a)
# mysql_no_return(sql)
























