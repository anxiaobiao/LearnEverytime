''''
Real Time Face Recogition
	==> Each face stored on dataset/ dir, should have a unique numeric integer ID as 1, 2, 3, etc                       
	==> LBPH computed model (trained faces) should be on trainer/ dir
Based on original code by Anirban Kar: https://github.com/thecodacus/Face-Recognition    

Developed by Marcelo Rovai - MJRoBot.org @ 21Feb18  

'''

import cv2
import numpy as np
import os
import temperature
import Ctrl_MySQL as SQL
import time

recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read('trainer/trainer.yml')
cascadePath = "haarcascade_frontalface_default.xml"
faceCascade = cv2.CascadeClassifier(cascadePath);

font = cv2.FONT_HERSHEY_SIMPLEX

#iniciate id counter
id = 0

# names related to ids: example ==> Marcelo: id=1,  etc
# names = ['None', 'Marcelo', 'Paula', 'Ilza', 'Z', 'W']
sql = "select name from temp"
names = SQL.mysql_return(sql)
n = []
for i in range(len(names)):
    n.append(str(names[i][0]))
names = n
del n
# print(n)

sql = "select id from temp"
num_id = SQL.mysql_return(sql)
t_id = []
# print((num_id[1][0]))
for i in range(len(num_id)):
    t_id.append(int(num_id[i][0]))
num_id = t_id
# print(num_id)
# num_id = list(num_id)
# print(num_id)

sql = "select temp_table from temp"
temp_table = SQL.mysql_return(sql)
t_table = []
# print((num_id[1][0]))
for i in range(len(temp_table)):
    t_table.append(str(temp_table[i][0]))
temp_table = t_table

width, height = 640, 480

# Initialize and start realtime video capture
cam = cv2.VideoCapture(0)
cam.set(3, width) # set video widht
cam.set(4, height) # set video height

# Define min window size to be recognized as a face
minW = 0.1*cam.get(3)
minH = 0.1*cam.get(4)

while True:

    ret, img =cam.read()
    img = cv2.flip(img, 1) # Flip vertically

    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

    faces = faceCascade.detectMultiScale( 
        gray,
        scaleFactor = 1.2,
        minNeighbors = 5,
        minSize = (int(minW), int(minH)),
       )

    for(x,y,w,h) in faces:
        print(x, y, w, h)

        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

        id, confidence = recognizer.predict(gray[y:y + h, x:x + w])
        temp_id = id
        t_id = num_id.index(id)

        if (confidence < 100):
            id = names[t_id]
            confidence = "  {0}%".format(round(100 - confidence))
        else:
            id = "unknown"
            confidence = "  {0}%".format(round(100 - confidence))

        temp = temperature.main(x, y, w, h, width, height)
        t_id = num_id[t_id]
        print(id, temp)

        temp_data = (time.strftime('%Y-%m-%d',time.localtime(time.time())))
        temp_data = "'{}'".format(temp_data)

        sql = " select time from t_{} order by time desc limit 0,1".format(t_id)
        c = SQL.mysql_return(sql)
        if len(c):
            c = "'{}'".format(c[0][0])
        if c != temp_data:
            sql = "insert into t_{} (time) VALUES ({})".format(t_id, temp_data)
            SQL.mysql_no_return(sql)

        # Check if confidence is less them 100 ==> "0" is perfect match 


        temp_hour = int((time.strftime('%H',time.localtime(time.time()))))
        if temp_hour <12 and temp_hour >= 8:
            noon = '上午'
        if temp_hour >= 12 and temp_hour < 18:
            noon = '下午'
        if temp_hour >= 18 and temp_hour < 23:
            noon = '晚上'
        if temp_hour >= 23 or temp_hour < 8:
            noon = '凌晨'
        # temp_data = "'{}'".format(temp_data)
        # print(temp_data)
        # temp = "'{}'".format(temp)
        if temp > 30:
            sql = "update t_{} set {}={} where time = {}".format(t_id, noon, temp, temp_data)
            # print(sql)
            SQL.mysql_no_return(sql)

        # if temp > 30:
        #     sql = "update t set 8点={} where id = {}".format(temp, t_id)
        #     SQL.mysql_no_return(sql)

        cv2.putText(img, str(id), (x+5,y-5), font, 1, (255,255,255), 2)
        cv2.putText(img, str(temp), (x+5,y+h-5), font, 1, (255,255,0), 1)
        # cv2.putText(img, str(temp), (x+5,y+h-5), font, 1, (255,255,0), 1)

    
    cv2.imshow('camera',img) 

    k = cv2.waitKey(10) & 0xff # Press 'ESC' for exiting video
    if k == 27:
        break

# Do a bit of cleanup
print("\n [INFO] Exiting Program and cleanup stuff")
cam.release()
cv2.destroyAllWindows()
