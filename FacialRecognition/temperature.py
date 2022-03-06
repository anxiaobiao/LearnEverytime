import numpy as np
import serial

# temperature = np.random.uniform(35, high=38, size=(32,32))

def ReadTemperature():
    temperature = np.array([0.0] * 1024).reshape(32, 32)
    Temp_Byte = [0 for j in range(0, 2055)]
   # print(Temp_Byte)
    if serial.isOpen():
        CMD_Data = [0xEE, 0xE1, 0x01, 0x55, 0xFF, 0xFC, 0xFD, 0xFF]  # 发送读取温度数据命令
        serial.write(CMD_Data)  # 串口写数据
        for i in range(0, 2055, 1):
            Temp_Byte[i] = serial.read(1)
        # 计算温度数据
        for i in range(0, 32, 1):
            for j in range(0, 32, 1):
                temperature[i][j] = int.from_bytes(
                    Temp_Byte[64 * i + 2 * (j + 1) - 1] + Temp_Byte[64 * i + 2 * (j + 1)], byteorder='big')
                temperature[i][j] = round(((temperature[i][j] - 2731)/10.0) ,1)  # 计算摄氏温度
        return temperature

def AxisTempTran(x, y, w, h, width, height):
    LeftTop_x = int(x * 32 / width)
    LeftTop_y = int(y * 32 / height)
    
    RightDown_x = int((x + w) * 32 / width)
    RightDown_y = int((y + h) * 32 / height) 
    
    return LeftTop_x, LeftTop_y, RightDown_x, RightDown_y

def SquTemp(LeftTop_x, LeftTop_y, RightDown_x, RightDown_y, temperature):
    
    TempList = []
    for i in range(LeftTop_y, RightDown_y, 1):
        for j in range(LeftTop_x, RightDown_x, 1):
            TempList.append(temperature[j, i])
    maxTemp = max(TempList)
    del TempList
    return maxTemp

serial = serial.Serial('COM3', 115200, timeout=2)
temperature = np.array([[0 for j in range(0, 32)] for i in range(0, 32)])
def main(x, y, w, h, width, height):
    # faces = np.array([193, 228, 223, 223]).reshape(1, 4)
    # width = 640
    # height = 480
    # x, y, w, h = faces[0, 0], faces[0, 1], faces[0, 2], faces[0, 3]
    
    LeftTop_x, LeftTop_y, RightDown_x, RightDown_y = AxisTempTran(x, y, w, h, width, height)
    temperature = ReadTemperature()
    Temp = SquTemp(LeftTop_x, LeftTop_y, RightDown_x, RightDown_y, temperature)
    # print(Temp)
    return Temp

# if __name__ == '__main__':
#     faces = np.array([190, 3, 69, 69]).reshape(1, 4)
#     width = 640
#     height = 480
#     x, y, w, h = faces[0, 0], faces[0, 1], faces[0, 2], faces[0, 3]
#     while(1):
#         a = main(x, y, w, h, width, height)
#         print(a)























