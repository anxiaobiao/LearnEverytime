import numpy as np
import cv2


data = cv2.imread(r'D:\code\path_planning\zzz_Graduate\pictrure\swelling_and_corrosion.png', 0)
_, data = cv2.threshold(data, 110, 255, cv2.THRESH_BINARY)

kernel = np.ones((5, 5), np.uint8)
data_dilate = cv2.dilate(data, kernel)
data_erosion = cv2.erode(data, kernel)

imgs = np.hstack([data, data_dilate, data_erosion])



cv2.imshow("imgs", imgs)
# cv2.imwrite(r"D:\code\path_planning\zzz_Graduate\pictrure/data.jpg", data)
cv2.imwrite(r"D:\code\path_planning\zzz_Graduate\pictrure/data_dilate.jpg", data_dilate)
cv2.imwrite(r"D:\code\path_planning\zzz_Graduate\pictrure/data_erosion.jpg", data_erosion)
cv2.waitKey(0)