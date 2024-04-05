from skimage import morphology
import numpy as np
import cv2


data = cv2.imread(r'pictrure\skeleton.jpg', 0)
_, data = cv2.threshold(data, 110, 255, cv2.THRESH_BINARY_INV)
# cv2.imwrite("binary.png", binary)
data_skeleton = data.copy()
data_skeleton[data_skeleton==255] = 1
skeleton0 = morphology.skeletonize(data_skeleton)     # 图片细化（骨架提取）
skeleton = skeleton0.astype(np.uint8)*255

cv2.imshow("imgs", data)
cv2.imshow("data_erosion", skeleton)
cv2.waitKey(0)