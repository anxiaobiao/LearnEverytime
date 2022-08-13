import numpy as np
from scipy.io import savemat
import math
from scipy.spatial import Voronoi
from scipy.spatial import voronoi_plot_2d
import matplotlib.pyplot as plt

# 忽略警告
import warnings
warnings.filterwarnings("ignore")

voronoi_point = np.load('../data/Python/voronoi_point.npy',allow_pickle=True)
voronoi_point = voronoi_point.tolist()
barrier = np.load('../data/Python/barrier.npy')


