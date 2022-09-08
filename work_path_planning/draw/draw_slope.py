import tifffile as tiff
import numpy as np
import cv2
from PIL import Image
import math
import gdal

from path_people.optimize import test_barr as TB


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

def make_solpe(data, angle):
    calcsolpe = TB.CalcSolpe(data, 1, 1)
    solpe = np.full((len(data), len(data[0])), np.nan)
    for i in range(1, len(solpe)-1):
        for j in range(1, len(solpe[0])-1):
            S = getattr(calcsolpe, 'second')(i, j)  # 获得的为角度值
            if S > math.tan(angle):
                solpe[i, j] = 200
            else:
                solpe[i, j] = int(S * 100)
        print(i)

    solpe[np.isnan(solpe)] = 255
    solpe = solpe.astype(np.uint8)
    return solpe

def get_barr(data):
    for i in range(len(data)):
        for j in range(len(data[0])):
            if data[i, j, 0] == 200 and data[i, j, 1] == 200 and data[i, j, 2] == 200:
                data[i, j, 0] = 255
                data[i, j, 1] = 0
                data[i, j, 2] = 0

def judge_a(a):
    for i in range(len(a)):
        for j in range(len(a[0])):
            if a[i, j] != 255:
                a[i, j] = 0
            else:
                a[i, j] = 255


if __name__ == '__main__':
    imgpath = r'D:\data\中南大学\dsm\tile_380000_3048000.tif'
    # imgpath = 'D:\code\path_planning\draw\Slope.tif'
    data = tiff.imread(imgpath)

    angle = math.pi * 5 / 18     # 角度 > angle 为障碍
    solpe = make_solpe(data, angle)
    pic_RGB = cv2.cvtColor(solpe, cv2.COLOR_GRAY2BGR)
    get_barr(pic_RGB)
    # # pic_RGB = Image.fromarray(pic_RGB)
    # # pic_RGB.save("pic_RGB.png")
    # # # pic_RGB.show()

    reference_path = r'D:\code\path_planning\draw\reference.tif'
    run = GRID()
    # proj, geotrans, data1, row1, column1 = run.read_img(reference_path)
    proj, geotrans, data1, row1, column1 = run.read_img(imgpath)

    # data2 = cv2.imread("pic_RGB.png", -1).transpose(2,0,1)
    # data2 = np.array((data2), dtype=data1.dtype)
    data2 = np.array((pic_RGB), dtype=data1.dtype).transpose(2,0,1)
    r, g, b, a = data2[2, :, :], data2[1, :, :], data2[0, :, :], data2[2, :, :]
    judge_a(a)
    data2 = np.vstack((r, g, b, a)).reshape(4, len(r), len(r[0]))
    run.write_img('pic_2_tif.tif', proj, geotrans, data2)

    # 显示灰度图
    # im = Image.fromarray(solpe)
    # im.show()