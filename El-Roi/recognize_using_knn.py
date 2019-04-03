import pickle
import numpy as np
import cv2
import os, json
import face_recognition.api as face_recognition

#set the classifier location
model_path = "/var/www/ElRoiApp/ElRoiApp/trained_member_knn_model_new.clf"
unidentified_image_path = "/var/www/ElRoiApp/ElRoiApp/unidentified_images"
# Load a trained KNN model (if one was passed in)
knn_clf = None
with open(model_path, 'rb') as f:
    knn_clf = pickle.load(f)

def unrecognize_names(unidentified_image_dir):
    unidentified_face_encodings = []
    # Loop through each unidentified images
    for img_path in image_files_in_folder(unidentified_image_dir):
        image = face_recognition.load_image_file(img_path)
        # Find all the faces and face encodings in the current frame of video
        face_locations = face_recognition.face_locations(image, number_of_times_to_upsample=2)
        face_encodings = face_recognition.face_encodings(image, face_locations, num_jitters=10)
        unidentified_face_encodings.append(face_encodings)
    return unidentified_face_encodings

unidentified_face_encodings = mlearning.unrecognize_names(unidentified_image_path)

# # ------------------------------------------ KNN Model Prediction ------------------------------
# # Note: You can pass in either a classifier file name or a classifier model instance

predictions = mlearning.predict_without_location(len(unidentified_face_encodings), unidentified_face_encodings, knn_clf=knn_clf, model_path=None)
       

face_names = []
unknown_image_count = 0        
for name, (top, right, bottom, left) in predictions:
    #print("- Found {} at ({}, {})".format(name, left, top))
    if(len(str(name).split("_")) > 1):
        face_names.append(str(name).split("_")[1])
    else:
        unknown_image_count += 1

print('Found name - {}'.format( ",".join(str(x) for x in np.unique(face_names))))
print('\n unknown images - {}'.format(unknown_image_count))