# openCV
#import cv2
# for numpy arrays
import numpy as np
#import dlib
# for creating folders
import os
import sys, json
import uuid
import time
import urllib
# connecting to the database
# create a El-Roi instance
from roi_backbone import ElRoi
# load config from a JSON file (or anything outputting a python dictionary)
with open("roi.conf") as f:
    config = json.load(f)

roi = ElRoi(config)


def insertmember(member_firstname, member_lastname, member_phone, member_email):

    params = (member_firstname, member_lastname)
    memberid = ""
    memberid = roi.db.get_member_by_name(params)
  
    if(memberid == ""):
        memberid = str(uuid.uuid4())
        params = (member_firstname, member_lastname, member_email, member_phone, personid)
        roi.db.insert_member(params)
   
    return memberid

while(True):
    # Build the DB with the members.
    print('-' * 40)
    member_firstname = input("Enter member's << first name >> : ")
    member_lastname = input("Enter member's << last name >> : ")
    member_email = input("Enter member's << email address >> : ")
    member_phone = input("Enter member's << phone number >> : ")
    params = (member_firstname, member_lastname, member_phone, member_email)
    # calling the sqlite3 database
    memberid = insertmember(member_firstname, member_lastname, member_phone, member_email)

    cap = cv2.VideoCapture(0)
    detector = dlib.get_frontal_face_detector()

    # creating the person or member folder
    folderName = "knn_training_model/training_dataset/" + str(memberid) + '_' + member_firstname
    folderPath = os.path.join(os.path.dirname(
        os.path.realpath(__file__)), folderName)
    if not os.path.exists(folderPath):
        os.makedirs(folderPath)

    sampleNum = 0
    print("The camara is scanning your face. Please look at the cam.")
    while(True):
        # reading the camera input
        ret, img = cap.read()
        # Converting to GrayScale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        dets = detector(img, 1)
        # loop will run for each face detected
        for i, d in enumerate(dets):
            sampleNum += 1
            cv2.imwrite(folderPath + "/" + str(member_firstname) + "_" + str(member_lastname) + "_face" + str(sampleNum) + ".jpg",
                        img[d.top():d.bottom(), d.left():d.right()])                                                # Saving the faces
            cv2.rectangle(img, (d.left(), d.top()), (d.right(),
                                                     d.bottom()), (0, 255, 0), 2)  # Forming the rectangle
            print(".", end='')
            sys.stdout.flush()
            # waiting time of 200 milisecond
            cv2.waitKey(200)

        # showing the video input from camera on window
        cv2.imshow('frame', img)
        cv2.waitKey(1)

        # will take 10 faces
        if(sampleNum >= 10):
            break

    # turning the webcam off
    cap.release()

    # Closing all the opened windows
    cv2.destroyAllWindows()
    print('{} - Member has been added - {}'.format(member_firstname, memberid) )
    print('-' * 40)
    #  quit!
    isContinue = input("Would you like to add more (y/n) ? : ")
    if(isContinue == 'n'):
        break

# close db
#connect.close()
