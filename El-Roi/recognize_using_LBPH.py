import cv2
import numpy as np
import os, re
import face_recognition.api as face_recognition

recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read('trainer/trainer_lbp.yml')
cascadePath = "cascade_data/lbpcascade_frontalface.xml"
faceCascade = cv2.CascadeClassifier(cascadePath)
unidentified_image_dir = "../unidentified_images"

font = cv2.FONT_HERSHEY_SIMPLEX

#iniciate id counter
id = 0

def image_files_in_folder(folder):
    return [os.path.join(folder, f) for f in os.listdir(folder) if re.match(r'.*\.(jpg|jpeg|png)', f, flags=re.I)]


print("Start LBPH image recognize Program.")
for img_path in image_files_in_folder(unidentified_image_dir):
   
    #load image from the image file
    image = face_recognition.load_image_file(img_path)
    # convert the image to gray scale
    gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)

    faces = faceCascade.detectMultiScale( 
        gray,
        scaleFactor = 1.2,
        minNeighbors = 5,
    )

    for(x,y,w,h) in faces:

        id, confidence = recognizer.predict(gray[y:y+h,x:x+w])

            # Check if confidence is less them 100 ==> "0" is perfect match 
        if (confidence < 100):
                #id = names[id]
                
            confidence = "  {0}%".format(round(100 - confidence))
            print("Found person id : {} ".format(id))
            print("Confidence Level - {}".format( confidence))
        else:
            id = "unknown"
            confidence = "  {0}%".format(round(100 - confidence))
            print("Found person id : Unknown")
            print("Confidence Level - {}".format( confidence))
 
   

print("\n Exiting Program.")