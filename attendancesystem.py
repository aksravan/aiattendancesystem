import cv2
import face_recognition as fr
import keyboard
import numpy as np
import os
import smtplib

from datetime import datetime, date
from email.mime.multipart import MIMEMultipart 
from email.mime.text import MIMEText 
from email.mime.base import MIMEBase 
from email import encoders
from stdiomask import getpass
from time import time

#setting images paths and names of the students
def setStudentImagesPath():
    imageList = os.listdir(studentPath)
    for cl in imageList:
        curImg = cv2.imread(f'{studentPath}/{cl}')
        studentImages.append(curImg)
        studentNames.append(os.path.splitext(cl)[0])

#setting image path and names of the teachers
def setTeacherImagesPath():
    imageList = os.listdir(teacherPath)
    for cl in imageList:
        curImg = cv2.imread(f'{teacherPath}/{cl}')
        teacherImages.append(curImg)
        teacherNames.append(os.path.splitext(cl)[0])

# creating file for record attendance
def getAttendance(name):
    with open(f'attendance{file}.csv', 'r+') as f:
        myData = f.readlines()
        names = []
        for line in myData:
            entry = line.split(',')
            names.append(entry[0])
        
        
        # writing name on the file
        if name not in names:
            now = datetime.now()
            tym = now.strftime('%H:%M:%S')
            todayDate = str(date.today())
            f.writelines(name + ',' + todayDate + ',' + tym + '\n')
            print(name)
    f.close()

# finding encoding for the personImages
def findStudentEncoding(studentImages):
    studentEncodeList = []
    for img in studentImages:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = fr.face_encodings(img)[0]
        studentEncodeList.append(encode)
    return studentEncodeList

# finding encoding for the personImages
def findTeacherEncoding(teacherImages):
    teacherEncodeList = []
    for img in teacherImages:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = fr.face_encodings(img)[0]
        teacherEncodeList.append(encode)
    return teacherEncodeList

#getting videos of all the students
def captureTeacherVideo():
    # initiliaze the webcam
    cap = cv2.VideoCapture(0)
    while True:
        flag = False
        success, liveImg = cap.read()
        imgS = cv2.resize(liveImg, (0, 0), None, 0.25, 0.25)
        imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

        facesCurFrame = fr.face_locations(imgS)
        encodeCurFrame = fr.face_encodings(imgS, facesCurFrame)

        for eFace, faceLoc in zip(encodeCurFrame, facesCurFrame):
            matches = fr.compare_faces(encodeTeacherListKnown, eFace)
            faceDis = fr.face_distance(encodeTeacherListKnown, eFace)
            matchIndex = np.argmin(faceDis)  # now we have the index of the user

            if matches[matchIndex]:
                name = teacherNames[matchIndex].upper()
                print('Hello!', name)
                flag = True
                break
                
        # creating bounding box which shows the image of the person
        cv2.imshow('Teacher Webcam', liveImg)
        cv2.waitKey(1)
        if flag:
            cv2.destroyAllWindows()
            break
    return True

#getting videos of all the students
def captureStudentVideo():
    # initiliaze the webcam
    cap = cv2.VideoCapture(0)
    while True:
        #getting time that is 15 minutes 
        endTime = time()
        seconds_elapsed = endTime - startTime
        hours, rest = divmod(seconds_elapsed, 3600)
        minutes, seconds = divmod(rest, 60)
        #if time exceeds or equal to 15 minutes it will stop immediately
        if minutes >= 1:
            cv2.destroyAllWindows()
            break
        

        success, liveImg = cap.read()
        imgS = cv2.resize(liveImg, (0, 0), None, 0.25, 0.25)
        imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

        facesCurFrame = fr.face_locations(imgS)
        encodeCurFrame = fr.face_encodings(imgS, facesCurFrame)

        for eFace, faceLoc in zip(encodeCurFrame, facesCurFrame):
            matches = fr.compare_faces(encodeStudentListKnown, eFace)
            faceDis = fr.face_distance(encodeStudentListKnown, eFace)      #get face distance of every student with the student on the webcam
            matchIndex = np.argmin(faceDis)  # now we have the index of the user

            if matches[matchIndex]:
                name = studentNames[matchIndex].upper()
                print(name)
                getAttendance(name)
        # creating bounding box which shows the image of the person
        cv2.imshow('Student Webcam', liveImg)
        cv2.waitKey(1)

#sending mail toh the desired teacher. . .
def sendMail():
    fromaddr = "kumarprabhat26@gmail.com"
    toaddr = "thakurdsingh14@gmail.com"
    
    # instance of MIMEMultipart 
    message = MIMEMultipart() 
    # storing the senders email address and receiver email address 
    message['From'], message['To'], message['Subject'] = fromaddr , toaddr, 'Attendance'
    # string to store the body of the mail 
    body = "Thank you! For using our project for this purpose."
    
    # attach the body with the msg instance 
    message.attach(MIMEText(body, 'plain')) 
    
    # open the file to be sent  
    filename = "attendance.csv"
    attachment = open("attendance.csv", "rb") 
    
    # instance of MIMEBase and named as p 
    p = MIMEBase('application', 'octet-stream') 
    
    # To change the payload into encoded form 
    p.set_payload((attachment).read()) 
    
    # encode into base64 
    encoders.encode_base64(p) 
    
    p.add_header('Content-Disposition', "attachment; filename= %s" % filename) 
    
    # attach the instance 'p' to instance 'msg' 
    message.attach(p) 
    
    # creates SMTP session 
    s = smtplib.SMTP('smtp.gmail.com', 587) 
    
    # start TLS for security 
    s.starttls() 
    
    # Authentication 
    s.login(fromaddr, "allfather420") 
    
    # Converts the Multipart msg into a string 
    text = message.as_string() 
    
    # sending the mail 
    s.sendmail(fromaddr, toaddr, text) 
    
    # terminating the session 
    s.quit() 
    

if __name__ == '__main__':
    password = '1234'
    file = datetime.now().strftime('%H%M%S')
    #adding headings in the attendance sheet
    with open(f'attendance{file}.csv', 'w+') as f:
        f.writelines("Name,Date,Time\n")
    f.close()

    studentPath = 'studentImages'
    studentImages = []
    studentNames = []

    teacherPath = 'teacherImages'
    teacherImages = []
    teacherNames = []
    print('press enter to start. . .')
    
    keyboard.wait('enter')
        
    print('Starting teacher\'s encoding. . .')
    setTeacherImagesPath()

    #getting the encodes of all the teachers
    encodeTeacherListKnown = findTeacherEncoding(teacherImages)

    #getting time for furthur checking for 15 minutes time limit
    startTime = time()

    print('Teacher encoding completed. . .')
    status = captureTeacherVideo()

    if status:
        while True:
            pswrd = getpass()
            if pswrd == password:
                break
            
        setStudentImagesPath()
        print('Starting student\'s encoding. . .')

        encodeStudentListKnown = findStudentEncoding(studentImages)

        print('Ready to scan students. . . ')
        keyboard.wait('enter')
        startTime = time()
        captureStudentVideo()
        print('attendance is completed. . .')

        print('sending mail to teacher. . .')
        sendMail()
        print('mail sent successfully. . .')
            