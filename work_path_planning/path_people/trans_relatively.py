import numpy as np
from PIL import Image
import cv2

def matrix_res(A12, B1, Apianchazhi):
    # A12 = np.array(A12)

    A12 = A12 -Apianchazhi
    A12 = np.c_[A12, np.ones(len(A12))]

    # B1 = np.array(B1)

    B1 = np.c_[B1, np.ones(len(B1))]

    AA1 = A12.T @ A12
    invAA1 = np.linalg.inv(AA1)

    AB1 = B1.T @ A12 @ invAA1
    AB1inv = np.linalg.inv(AB1)

    return AB1, AB1inv

def the_data():
    A12 = np.load('./data/A12.npy')
    B1 = np.load('./data/B1.npy')

    Apianchazhi = np.array([-2193500, 5187698, 2982792])

    C1 = [[-2193452.7532769926,5187834.814012843,2982584.9942662106],
          [-2193697.2976713697,5187735.141402754,2982578.551225891],
          [-2193691.9610962938,5187719.064330411,2982610.2261918243],
          [-2193651.864670318,5187716.143288889,2982644.565603988],
          [-2193639.9895838643,5187711.043667241,2982662.051250831],
          [-2193634.1926531214,5187701.204899227,2982683.283948096],
          [-2193634.4655785966,5187697.766466958,2982689.024897793],
          [-2193642.6695555914,5187682.036296777,2982710.2073450605],
          [-2193644.2390644923,5187670.730197069,2982728.5932014445],
          [-2193643.520684175,5187661.052859991,2982745.8364355345],
          [-2193634.7893217346,5187651.513416305,2982768.69491839],
          [-2193620.703506216,5187646.2937209485,2982788.0020394577],
          [-2193586.71324918,5187644.012574753,2982816.7724906127],
          [-2193577.295407305,5187639.956111942,2982830.6597056277],
          [-2193571.0815107557,5187625.664544637,2982859.887665009],
          [-2193567.4432948735,5187618.717527006,2982874.546212323],
          [-2193562.389687332,5187614.414493135,2982885.671118308],
          [-2193401.619153271,5187680.90630878,2982888.2389460905]]
    C1 = np.array(C1)

    return A12, B1, C1, Apianchazhi

def cal_res():
    A12, B1, C1, Apianchazhi = the_data()

    AB1, AB1inv = matrix_res(A12, B1, Apianchazhi)
    C1 = C1 - Apianchazhi
    C1 = np.c_[C1, np.ones(len(C1))]

    res = (AB1 @ C1.T).T

    res = np.delete(res, [2, 3], axis=1)

    return res

def isRayIntersectsSegment(poi,s_poi,e_poi): #[x,y] [lng,lat]
    #输入：判断点，边起点，边终点，都是[lng,lat]格式数组
    if s_poi[1]==e_poi[1]: #排除与射线平行、重合，线段首尾端点重合的情况
        return False
    if s_poi[1]>poi[1] and e_poi[1]>poi[1]: #线段在射线上边
        return False
    if s_poi[1]<poi[1] and e_poi[1]<poi[1]: #线段在射线下边
        return False
    if s_poi[1]==poi[1] and e_poi[1]>poi[1]: #交点为下端点，对应spoint
        return False
    if e_poi[1]==poi[1] and s_poi[1]>poi[1]: #交点为下端点，对应epoint
        return False
    if s_poi[0]<poi[0] and e_poi[1]<poi[1]: #线段在射线左边
        return False

    xseg=e_poi[0]-(e_poi[0]-s_poi[0])*(e_poi[1]-poi[1])/(e_poi[1]-s_poi[1]) #求交
    if xseg<poi[0]: #交点在射线起点的左侧
        return False
    return True  #排除上述情况之后

def isPoiWithinPoly(poi,poly):
    #输入：点，多边形三维数组
    #poly=[[[x1,y1],[x2,y2],……,[xn,yn],[x1,y1]],[[w1,t1],……[wk,tk]]] 三维数组

    #可以先判断点是否在外包矩形内
    #if not isPoiWithinBox(poi,mbr=[[0,0],[180,90]]): return False
    #但算最小外包矩形本身需要循环边，会造成开销，本处略去
    sinsc=0 #交点个数
    for epoly in poly: #循环每条边的曲线->each polygon 是二维数组[[x1,y1],…[xn,yn]]
        for i in range(len(epoly)-1): #[0,len-1]
            s_poi=epoly[i]
            e_poi=epoly[i+1]
            if isRayIntersectsSegment(poi,s_poi,e_poi):
                sinsc+=1 #有交点就加1

    return True if sinsc%2==1 else  False

def frame(data, bound):
    bound = bound.astype(int).astype(float) + 0.5 * np.ones((len(bound), len(bound[0])))
    bx_min, bx_max, by_min, by_max = min(bound[:, 0]), max(bound[:, 0]), min(bound[:, 1]), max(bound[:, 1])

    bound_x, bound_y = int(bx_max - bx_min), int(by_max - by_min)
    pic = np.full((bound_x, bound_y), np.nan)

    x_min, x_max, y_min, y_max = max(min(data[:, 0]), min(bound[:, 0])), min(max(data[:, 0]), max(bound[:, 0])), \
                                max(min(data[:, 1]), min(bound[:, 1])), min(max(data[:, 1]), max(bound[:, 1]))

    # bound_points = make_bound(bound)  # 表示所有边的表示，两个点表示一个边
    bound_points = [bound.tolist()]
    data_map = make_map(data)

    for i in np.arange(x_min, x_max, 1):
        for j in np.arange(y_min, y_max, 1):
            # print(i, j)
            if isPoiWithinPoly([i, j], bound_points):
                y = int(abs(j - by_max))
                x = int(abs(i - bx_min))
                print(i, j, x, y)
                pic[x, y] = data_map[tuple([i, j])]

    pic = np.fliplr(pic)



    return pic

def make_map(data):
    data_map = dict()
    for i in range(len(data)):
        data_map[tuple(data[i, 0:2].tolist())] = data[i, 2]
    return data_map

def make_bound(bound_points):
    res = list()
    for i in range(len(bound_points) - 1):
        temp = []
        temp.append(bound_points[i])
        temp.append(bound_points[i+1])
        res.append(temp)

    temp = []
    temp.append(bound_points[i+1])
    temp.append(bound_points[1])
    res.append(temp)

    return res

if __name__ == '__main__':
    res = cal_res()
    data = np.loadtxt(r'D:\code\path_planning\path_people\optimize\solpe\second.txt')
    data = np.delete(data, [2], axis=1)

    pic = frame(data, res)
    pic = np.nan_to_num(pic, nan=255)
    pic = pic.astype(np.uint8)
    pic_RGB = cv2.cvtColor(pic, cv2.COLOR_GRAY2BGR)
    mask = (255 == pic_RGB[:, :, 0]) & (255 == pic_RGB[:, :, 1]) & (255 == pic_RGB[:, :, 2])
    alpha = (1 - mask.astype(np.uint8)) * 255
    img_rgba = np.concatenate((pic_RGB, alpha[:, :, np.newaxis]), 2)
    img_rgba = Image.fromarray(img_rgba)
    img_rgba = img_rgba.transpose(Image.ROTATE_90)
    img_rgba.save("123.png")

    # im = Image.fromarray(pic)
    # im = im.convert('L')  # 这样才能转为灰度图，如果是彩色图则改L为‘RGB’
    # im.show()
    # im.save('1.png')

    # a = data[0][0:2].tolist()
    #
    # c = isPoiWithinPoly(a,bound_points)