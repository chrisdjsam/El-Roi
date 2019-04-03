import cv2
import numpy as np
from PIL import Image
import os, re, json
# create a El-Roi instance
from roi_backbone import ElRoi
# load config from a JSON file (or anything outputting a python dictionary)
with open("../roi.conf") as f:
    config = json.load(f)

roi = ElRoi(config)
# Path for face image database
path = '../knn_training_model/training_dataset'

recognizer = cv2.face.LBPHFaceRecognizer_create()
detector = cv2.CascadeClassifier("cascade_data/haarcascade_frontalface.xml");

def image_files_in_folder(folder):
    return [os.path.join(folder, f) for f in os.listdir(folder) if re.match(r'.*\.(jpg|jpeg|png)', f, flags=re.I)]

# function to get the images and label data
def getImagesAndLabels(path):

    imagePaths = [os.path.join(path,f) for f in os.listdir(path)]     
    faceSamples=[]
    ids = []
      # Loop through each person in the training set
    for class_dir in os.listdir(path):
        if not os.path.isdir(os.path.join(path, class_dir)):
            continue
        id = int(class_dir.split('_')[0])
        # Loop through each training image for the current person
        for imagePath in image_files_in_folder(os.path.join(path, class_dir)):
            
            PIL_img = Image.open(imagePath).convert('L') # convert it to grayscale
            img_numpy = np.array(PIL_img,'uint8')

            
            faces = detector.detectMultiScale(img_numpy)
            for (x,y,w,h) in faces:
                faceSamples.append(img_numpy[y:y+h,x:x+w])
                ids.append(id)
    return faceSamples,ids

print ("\n [INFO] Training faces. It will take a few seconds. Wait ...")
faces,ids = getImagesAndLabels(path)
print(ids)
recognizer.train(faces, np.array(ids))

# Save the model into trainer/trainer.yml
recognizer.write('trainer/trainer_haar.yml') # recognizer.save() worked on Mac, but not on Pi

# Print the numer of faces trained and end program
print("\n [INFO] {0} faces trained. Exiting Program".format(len(np.unique(ids))))