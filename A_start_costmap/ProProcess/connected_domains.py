import numpy as np
import cv2

def get_del_threshold(fused_map, threshold):
    fused_map_index = np.array(fused_map != 0, dtype=int)
    total_area = fused_map_index.sum()
    area_threshold = np.ceil(total_area*threshold)
    return area_threshold

def del_index_withthreshold(area_threshold, labels, states):
    cla = np.arange(0, states.shape[0])
    all_area = states[:,-1]
    satisfied_area_index = all_area > area_threshold
    keep_area_index = cla[satisfied_area_index]
    mask = np.zeros_like(labels)
    for i in keep_area_index:
        mask += labels == i
    mask = np.array(1- mask, dtype=bool)
    return mask

def del_area(fused_map, threshold):
    num_labels, labels, states, centroids = cv2.connectedComponentsWithStats(np.array(255-fused_map, np.uint8), connectivity=8)
    area_threshold = get_del_threshold(fused_map, threshold)    # 障碍的个数？
    del_mask = del_index_withthreshold(area_threshold, labels, states)
    enhanced_fused_map = fused_map.copy()
    enhanced_fused_map[del_mask] = 255
    return enhanced_fused_map

fused_map = cv2.imread("D:\code\path_planning\zzz_Graduate\data\slope.tif",0)
threshold = 0.001

del_fuse = del_area(fused_map, threshold) ## 用于显示的二值图

# cv2.imshow("imgs", fused_map)
cv2.imwrite("D:\code\path_planning\zzz_Graduate\pictrure/slope.jpg", fused_map)
cv2.imwrite("D:\code\path_planning\zzz_Graduate\pictrure/ans.jpg", del_fuse)
cv2.waitKey(0)