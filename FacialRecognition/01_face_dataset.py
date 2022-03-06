''''
Capture multiple Faces from multiple users to be stored on a DataBase (dataset directory)
	==> Faces will be stored on a directory: dataset/ (if does not exist, pls create one)
	==> Each face will have a unique numeric integer ID as 1, 2, 3, etc                       

Based on original code by Anirban Kar: https://github.com/thecodacus/Face-Recognition    

Developed by Marcelo Rovai - MJRoBot.org @ 21Feb18    

'''

import cv2
import os
import Ctrl_MySQL as SQL

cam = cv2.VideoCapture(0)
cam.set(3, 640) # set video width
cam.set(4, 480) # set video height

face_detector = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

# For each person, enter one numeric face id
face_id = input('\n enter user id end press <return> ==>  ')
name = input('\n enter user name end press <return> ==>  ')
name = "'{}'".format(name)
temp_table = "'t_{}'".format(face_id)

# sql = "CREATE TABLE if not exists t (id int(11) not null primary key, name varchar(11), 8:00 varchar(11), 10:00 varchar(11), 14:00 varchar(11), 16:00 varchar(11), 19:00 varchar(11), 21:00 varchar(11));"
sql = "CREATE TABLE if not exists temp (id int(11) not null primary key, name varchar(11), temp_table varchar(11));"
SQL.mysql_no_return(sql)

sql = "insert into temp (id, name, temp_table) VALUES ({}, {}, {})".format(face_id, name, temp_table)
SQL.mysql_no_return(sql)

sql = "CREATE TABLE if not exists t_{} (time varchar(11), 上午 varchar(11), 下午 varchar(11), 晚上 varchar(11), 凌晨 varchar(11));".format(face_id)
SQL.mysql_no_return(sql)

print("\n [INFO] Initializing face capture. Look the camera and wait ...")
# Initialize individual sampling face count
count = 0

while(True):

    ret, img = cam.read()
    img = cv2.flip(img, 1) # flip video image vertically
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_detector.detectMultiScale(gray, 1.3, 5)

    for (x,y,w,h) in faces:

        cv2.rectangle(img, (x,y), (x+w,y+h), (255,0,0), 2)     
        count += 1

        # Save the captured image into the datasets folder
        cv2.imwrite("dataset/User." + str(face_id) + '.' + str(count) + ".jpg", gray[y:y+h,x:x+w])
        print(count)
        cv2.imshow('image', img)
        print(count)
    k = cv2.waitKey(100) & 0xff # Press 'ESC' for exiting video
    if k == 27:
        break
    elif count >= 60: # Take 60 face sample and stop video
         break

# Do a bit of cleanup
print("\n [INFO] Exiting Program and cleanup stuff")
cam.release()
cv2.destroyAllWindows()


