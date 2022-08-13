import psycopg2
import numpy as np
from scipy.io import savemat


def read_date(database, user, password, host, sql, port = "5432"):
    con = psycopg2.connect(database = database, user = user, password = password, host = host, port = port)
    print("Database connect successgully!")

    cur = con.cursor()
    cur.execute(sql) # 从数据中选取点云数据
    rows = cur.fetchall()

    con.commit()

    cur.close()
    con.close()

    print("Database close")

    return rows

def extract_coordinates(date):
    process = list()
    for a in date:
        temp = eval(a[0])['pt']
        temp = [temp[-3], temp[-2], temp[-1]]
        process.append(temp)

    process = np.array(process)
    print("corrdinates done!")
    return process

def get_grid(data, side_len):

    x_min, x_max, y_min, y_max = min(data[:, 0]), max(data[:, 0]), min(data[:, 1]), max(data[:, 1])
    # x_min, x_max, y_min, y_max = int(x_min - 1), int(x_max + 1), int(y_min - 1), int(y_max + 1)
    x_min, x_max, y_min, y_max = int(x_min), int(x_max), int(y_min), int(y_max)

    data_grid = list()
    for i in np.arange(x_min, x_max, side_len):
        # if i + side_len < min(data[:, 0]) or i - side_len > max(data[:, 0]):
        #     continue
        data_grid_x = list()
        for j in np.arange(y_min, y_max, side_len):
            # if j + side_len < min(data[:, 1]) or j - side_len > max(data[:, 1]):
            #     continue
            temp = data[:, 0] >= i
            a = data[temp]
            temp *= data[:, 0] < i + side_len
            a = data[temp]
            temp *= data[:, 1] >= j
            a = data[temp]
            temp *= data[:, 1] < j + side_len
            a = data[temp]
            temp = data[temp]
            data_grid_x.append([i + side_len / 2, j + side_len / 2, np.mean(temp[:, 2])])
            print(i, j)
        data_grid.append(data_grid_x)

    return data_grid

def insert_val(database, user, password, host, data, port = "5432"):
    con = psycopg2.connect(database=database, user=user, password=password, host=host, port=port)
    print("Database connect successgully!")

    cur = con.cursor()
    # cur.execute("select count(*) from pg_class where relname = 'test';")    # 查看表是否存在
    # rows = cur.fetchall()
    cur.execute("create table if not exists test(id int, pointpatch pcpatch);")  # 如果不存在表，创建
    cur.execute("INSERT INTO test (id)VALUES (1);")
    cur.execute("update test set pointpatch=Pc_makepatch(1, array{})where id=1;".format(data)) # 将数据插入

    con.commit()
    print("Database insert successgully!")
    cur.close()
    con.close()

def treat(data):
    data = np.reshape(data, (len(data) * len(data[0]), len(data_get[0][0])))
    temp = np.ones(len(data) * (15-len(data_get[0][0]))).reshape(len(data), (15-len(data_get[0][0]))).tolist()
    data = np.c_[temp, data]
    data = list(data.flatten())
    return data

if __name__ == '__main__':
    sql = "SELECT PC_AsText(PC_Explode(pa)) FROM out000003 WHERE id = 4;"
    data_ore = read_date(database = "path_people", user = "postgres", password = "123456", host = "localhost", sql=sql)  # 从数据库中提取数据
    data = extract_coordinates(data_ore)    # 将提取的数据处理成可用的三维数据

    data_get = get_grid(data, 1)
    data_get = np.array(data_get)

    data_treat = treat(data_get)
    insert_val(database = "path_people", user = "postgres", password = "123456", host = "localhost", data = data_treat)

    # data_moon = np.reshape(data_get, (len(data_get) * len(data_get[0]), 3))
    # savemat("../data/matlab/data_moon.mat", {'v': data})