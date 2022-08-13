import scipy.io as io
import numpy as np
import geopandas as gpd
import math
import shapely.geometry as geo
import pandas as pd

# 忽略警告
import warnings
warnings.filterwarnings("ignore")


data = io.loadmat('../data/matlab/Voronoi.mat')
vertices = data['vertices'].tolist()
ridge_vertices = data['ridge_vertices'].tolist()

# 构建DataFrame
def creat_datafream(order, fclass='service', name = None, oneway='B', maxspeed=30, bridge='F', cost=1, reverse_cost=1):
    temp = []
    for i in order:
        temp.append(tuple(vertices[i]))

    geometry = geo.LineString(temp)

    dictionary = {
        'fclass': [fclass],
        'name': [name],
        'oneway': [oneway],
        'maxspeed': [maxspeed],
        'bridge': [bridge],
        'geometry': [geometry],
        'cost': [take_cost(order)],
        'reverse_cost': [take_cost(order)]
    }
    return pd.DataFrame(dictionary)

# 获得代价：以长度作为代价
def take_cost(order):
    lenth = 0
    for i in range(len(order)-1):
        p1 = np.array(vertices[order[i]])
        p2 = np.array(vertices[order[i+1]])
        p3 = p2 - p1
        lenth += math.hypot(p3[0], p3[1])

    return lenth

pgrouting = pd.DataFrame()
for order in ridge_vertices:
    temp = creat_datafream(order)
    pgrouting = pgrouting.append(temp)

pgrouting.index = np.arange(len(pgrouting)).tolist()
# a = geo.LineString([(1,2),(2,3)])

pgrouting= gpd.GeoDataFrame(pgrouting)
pgrouting.to_file(r'../data/shapefile/voronoi.shp', driver='ESRI Shapefile',encoding='utf-8')
