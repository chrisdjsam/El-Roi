import cv2
import dlib
import os
import re
import time
import sys

detector = dlib.get_frontal_face_detector()
imagefile = []


def image_files_in_folder(folder):
    return [os.path.join(folder, f) for f in os.listdir(folder) if re.match(r'.*\.(jpg|jpeg|png)', f, flags=re.I)]


running_nummber = 0
if len(sys.argv) is not 2:
    imagefile.append(str(sys.argv[1]))
    lastname = str(sys.argv[2])
else:
    if os.path.exists(str(sys.argv[1])):
        lastname = 0
        running_nummber = 1
        for file in image_files_in_folder(str(sys.argv[1])):
            imagefile.append(file)

if not os.path.exists('./cropped_faces'):
    os.makedirs('./cropped_faces')

for eachimage in imagefile:
    img = cv2.imread(eachimage)
    print("Image file: " + eachimage)
    dets = detector(img, 1)
    print("detected = " + str(len(dets)))
    if(running_nummber > 0):
        lastname += 1
    for i, d in enumerate(dets):
        cv2.imwrite('./Cropped_faces/face' + str(i + 1) + '_' + str(lastname) + '.jpg',
                    img[d.top():d.bottom(), d.left():d.right()])
