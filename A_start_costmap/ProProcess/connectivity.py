import numpy as np
import cv2


data = cv2.imread(r'D:\code\path_planning\zzz_Graduate\pictrure\connectivity.jpg', 0)
cv2.imshow("imgs", data)
_, data = cv2.threshold(data, 110, 255, cv2.THRESH_BINARY)

num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(data, connectivity=8)

output = np.zeros((data.shape[0], data.shape[1], 3), np.uint8)
for i in range(1, num_labels):
    mask = labels == i
    output[:, :, 0][mask] = np.random.randint(0, 255)
    output[:, :, 1][mask] = np.random.randint(0, 255)
    output[:, :, 2][mask] = np.random.randint(0, 255)

cv2.imshow("img111", data)
cv2.imshow("data_erosion", output)
cv2.waitKey(0)