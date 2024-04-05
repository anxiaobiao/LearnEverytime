import numpy as np
import cv2
import argparse
import gdal

class GRID:

    # 读图像文件
    def read_img(self, filename):
        dataset = gdal.Open(filename)  # 打开文件

        im_width = dataset.RasterXSize  # 栅格矩阵的列数
        im_height = dataset.RasterYSize  # 栅格矩阵的行数

        im_geotrans = dataset.GetGeoTransform()  # 仿射矩阵
        im_proj = dataset.GetProjection()  # 地图投影信息
        im_data = dataset.ReadAsArray(0, 0, im_width, im_height)  # 将数据写成数组，对应栅格矩阵

        del dataset  # 关闭对象，文件dataset
        return im_proj, im_geotrans, im_data, im_width, im_height

    # 写文件，以写成tif为例
    def write_img(self, filename, im_proj, im_geotrans, im_data):

        # 判断栅格数据的数据类型
        if 'int8' in im_data.dtype.name:
            datatype = gdal.GDT_Byte
        elif 'int16' in im_data.dtype.name:
            datatype = gdal.GDT_UInt16
        else:
            datatype = gdal.GDT_Float32

        # 判读数组维数
        if len(im_data.shape) == 3:
        # if len(im_data.shape) == 4:
            im_bands, im_height, im_width = im_data.shape
        else:
            im_bands, (im_height, im_width) = 1, im_data.shape

        # 创建文件
        driver = gdal.GetDriverByName("GTiff")  # 数据类型必须有，因为要计算需要多大内存空间
        dataset = driver.Create(filename, im_width, im_height, im_bands, datatype)

        dataset.SetGeoTransform(im_geotrans)  # 写入仿射变换参数
        dataset.SetProjection(im_proj)  # 写入投影

        if im_bands == 1:
            dataset.GetRasterBand(1).WriteArray(im_data)  # 写入数组数据
        else:
            for i in range(im_bands):
                # dataset.GetRasterBand(i + 1).WriteArray(im_data[i])
                dataset.GetRasterBand(i + 1).WriteArray(im_data[i])
        del dataset

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

def generate_kernels(args):
    object_pwidth = int(np.ceil(args.object_width / args.pixel_meter))
    object_plength = int(np.ceil(args.object_length / args.pixel_meter))
    kernel1 = np.ones([object_pwidth, object_plength], np.uint8)
    kernel2 = np.ones([object_plength, object_pwidth], np.uint8)
    kernel3 = generate_diagonal_kernels(object_pwidth,object_plength)
    kernel4 = generate_diagonal_kernels(object_plength,object_pwidth)
    return kernel1,kernel2,kernel3,kernel4

def generate_diagonal_kernels(object_pwidth,object_plength): ##
    kernel_width = int(np.ceil(np.sqrt(2)/2*object_pwidth)+np.ceil(np.sqrt(2)/2*object_plength))
    # if kernel_width % 2 == 0:
    #     a = 1
    # else:
    #     a = 0
    diagonal_kernels = np.ones([kernel_width, kernel_width], np.uint8)
    ##
    width_square = int(np.ceil(np.sqrt(2) / 2 * object_pwidth))
    length_square = int(np.ceil(np.sqrt(2) / 2 * object_plength))
    lu_tri = 1-np.rot90(np.tri(width_square,width_square,k=-1),-1)## 左上三角
    ru_tri = 1-np.rot90(np.tri(length_square,length_square,k=-1),2)## 右上三角
    rd_tri = 1-np.rot90(np.tri(width_square,width_square,k=-1),1)## 右下三角
    ##
    diagonal_kernels[:width_square,:width_square] = lu_tri
    diagonal_kernels[:length_square,width_square:] = ru_tri
    diagonal_kernels[length_square:,length_square:] = rd_tri
    ##
    triu_kernel = np.triu(diagonal_kernels,k=0)
    trid_kernel = np.rot90(triu_kernel,2)
    diagonal_kernels = trid_kernel | triu_kernel
    return diagonal_kernels

def dilated_trafficable_map(binary_traffic_map,kernel1,kernel2,kernel3,kernel4):
    map1 = np.array(cv2.dilate(binary_traffic_map, kernel1), np.uint32)
    map2 = np.array(cv2.dilate(binary_traffic_map, kernel2), np.uint32)
    map3 = np.array(cv2.dilate(binary_traffic_map, kernel3), np.uint32)
    map4 = np.array(cv2.dilate(binary_traffic_map, kernel4), np.uint32)
    return map1,map2,map3,map4

def fuse_dilated_trafficable_map(map1,map2,map3,map4):
    fused_map = map1 & map2 & map3 & map4
    return fused_map

def post_processing(enhanced_fused_map, init_trafficable_map):
    index = enhanced_fused_map == 255
    ##
    final_map = init_trafficable_map.copy()
    final_map[index] = 255
    return final_map


"""
111
"""
parser = argparse.ArgumentParser(description='Hyper-parameter')
## 输入参数
parser.add_argument('--vehicle_or_person', type=bool, default=False,
                    help='False->person, True->car')
parser.add_argument('--object_width', type=float, default=4,
                    help='real width of the object(meter)')
parser.add_argument('--object_length', type=float, default=7.5,
                    help='real length of the object(meter)')
parser.add_argument('--max_slope', type=float, default=20,
                    help='maximum accessable slope')
parser.add_argument('--semantic_map', type=str, default='./input/caijian_final_class_zhuanhuan(1).tif',  ## 地物分类图
                    help='path of trafficable map generated from fuse_map.py')
parser.add_argument('--slope_map', type=str, default='./input/Slope_tif181_9_21_1_ProjectR1.tif',  ## 坡度图
                    help='path of trafficable map generated from fuse_map.py')
parser.add_argument('--save_pth', type=str, default='./output/',
                    help='area percentage threshold to delete')
## 超参数
parser.add_argument('--threshold', type=float, default=0.05,
                    help='area percentage threshold to delete')
parser.add_argument('--pixel_meter', type=float, default=0.5,
                    help='real distance reflected by one pixel')
## 输出路径
parser.add_argument('--save_dir', type=str, default='./output',
                    help='dir path for saving tif and png format picture')
args = parser.parse_args()


"""
222
"""

run = GRID()
proj, geotrans, prep_trafficable_map, row, column = run.read_img('data\slope_2.tif')  # 语义分割图
# prep_trafficable_map = cv2.imread("data\slope_2.tif",0)
threshold = 0.001

_, binary_traffic_map = cv2.threshold(prep_trafficable_map, 249, 255, cv2.THRESH_BINARY)
kernel1, kernel2, kernel3, kernel4 = generate_kernels(args)
map1, map2, map3, map4 = dilated_trafficable_map(binary_traffic_map, kernel1, kernel2, kernel3, kernel4)
fused_map = fuse_dilated_trafficable_map(map1, map2, map3, map4)
post_processing_img = post_processing(fused_map, prep_trafficable_map) ## 连通性前
cv2.imwrite(r"pictrure/accessibility_pro_2.jpg", post_processing_img)

del_fuse = del_area(fused_map, threshold) ## 用于显示的二值图
post_processing_img = post_processing(del_fuse, prep_trafficable_map) ## 连通性后

# cv2.imshow("imgs", post_processing_img)
# cv2.waitKey(0)
# cv2.imwrite("D:\code\path_planning\zzz_Graduate\pictrure/slope.jpg", fused_map)
run.write_img('data\people_2.tif', proj, geotrans, post_processing_img)
cv2.imwrite(r"pictrure/accessibility_ex_2.jpg", post_processing_img)


