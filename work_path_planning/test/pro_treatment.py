import scipy.io as io
import numpy as np
from scipy.io import savemat

# 忽略警告
import warnings
warnings.filterwarnings("ignore")

data = io.loadmat('matlab.mat')['v']

standard_x = 594000
standard_y = 3370000

data[:, 0] = data[:, 0] - standard_x
data[:, 1] = data[:, 1] - standard_y

for i in range(len(data)):
    if data[i, 2] <= 0:
        data[i, 2] = 0

np.save('data_nopro.npy',data)
savemat("data_nopro.mat", {'v': data})