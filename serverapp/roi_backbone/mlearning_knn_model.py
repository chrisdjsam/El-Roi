from sklearn import neighbors
import os, re, io, json
import numpy as np
import cv2, pickle, uuid, datetime
import ElRoiApp.roi_backbone.api as face_recognition 
from ElRoiApp.roi_backbone.ElRoi import ElRoi
import ElRoiApp.roi_backbone.external_api as ccb

# allow only image extension to learn 
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# load config from a JSON file (or anything outputting a python dictionary)
with open("/var/www/ElRoiApp/ElRoiApp/roi.conf") as f:
    config = json.load(f)
# create a El-Roi instance
roi = ElRoi(config)


def convert_array(text):
    out = io.BytesIO(text)
    out.seek(0)
    return np.load(out)

# get the trainned cnn dataset
def get_cnn_dataset():
    known_names = []
    known_personid = []
    known_face_encodings = []
    dataset = roi.db.get_member_encoded_face()
    # checking wheather the id exist or not
    for row in dataset:
        outp = convert_array(row[roi.db.FIELD_MEMBER_FACE_ENCODING])
        # print(outp)
        known_names.append(row[roi.db.FIELD_MEMBER_FIRST_NAME] + " " + row[roi.db.FIELD_MEMBER_LAST_NAME])
        known_face_encodings.append(outp)
        known_personid.append(row[roi.db.FIELD_MEMBER_PERSON_ID])

    # commiting into the database
    return known_names, known_face_encodings, known_personid

def image_files_in_folder(folder):
    return [os.path.join(folder, f) for f in os.listdir(folder) if re.match(r'.*\.(jpg|jpeg|png)', f, flags=re.I)]



def train(train_dir, model_save_path=None, n_neighbors=None, knn_algo='auto', verbose=True):
    """
    Trains a k-nearest neighbors classifier for face recognition.

    :param train_dir: directory that contains a sub-directory for each known person, with its name.

     (View in source code to see train_dir example tree structure)

     Structure:
        <train_dir>/
        ├── <person1>/
        │   ├── <somename1>.jpeg
        │   ├── <somename2>.jpeg
        │   ├── ...
        ├── <person2>/
        │   ├── <somename1>.jpeg
        │   └── <somename2>.jpeg
        └── ...

    :param model_save_path: (optional) path to save model on disk
    :param n_neighbors: (optional) number of neighbors to weigh in classification. Chosen automatically if not specified
    :param knn_algo: (optional) underlying data structure to support knn.default is ball_tree
    :param verbose: verbosity of training
    :return: returns knn classifier that was trained on the given data.
    """
    X = []
    y = []

    # Loop through each person in the training set
    for class_dir in os.listdir(train_dir):
        if not os.path.isdir(os.path.join(train_dir, class_dir)):
            continue

        # Loop through each training image for the current person
        for img_path in image_files_in_folder(os.path.join(train_dir, class_dir)):
            image = face_recognition.load_image_file(img_path)
            face_bounding_boxes = face_recognition.face_locations(image)

            if len(face_bounding_boxes) != 1:
                # If there are no people (or too many people) in a training image, skip the image.
                if verbose:
                    print("Image {} not suitable for training: {}".format(img_path, "Didn't find a face" if len(face_bounding_boxes) < 1 else "Found more than one face"))
            else:
                # Add face encoding for current image to the training set
                X.append(face_recognition.face_encodings(image, known_face_locations=face_bounding_boxes)[0])
                y.append(class_dir)

    # Determine how many neighbors to use for weighting in the KNN classifier
    if n_neighbors is None:
        n_neighbors = int(round(math.sqrt(len(X))))
        if verbose:
            print("Chose n_neighbors automatically:", n_neighbors)

    # Create and train the KNN classifier
    knn_clf = neighbors.KNeighborsClassifier(n_neighbors=n_neighbors, algorithm=knn_algo, weights='uniform')
    knn_clf.fit(X, y)

    # Save the trained KNN classifier
    if model_save_path is not None:
        with open(model_save_path, 'wb') as f:
            pickle.dump(knn_clf, f)

    return knn_clf
def predict_without_location(number_of_faces, faces_encodings, knn_clf=None, model_path=None, distance_threshold=0.42):
    """
    Recognizes faces in given image using a trained KNN classifier

    :param X_img_path: path to image to be recognized
    :param knn_clf: (optional) a knn classifier object. if not specified, model_save_path must be specified.
    :param model_path: (optional) path to a pickled knn classifier. if not specified, model_save_path must be knn_clf.
    :param distance_threshold: (optional) distance threshold for face classification. the larger it is, the more chance
           of mis-classifying an unknown person as a known one.
    :return: a list of names and face locations for the recognized faces in the image: [(name, bounding box), ...].
        For faces of unrecognized persons, the name 'unknown' will be returned.
    """
    # if not os.path.isfile(X_img_path) or os.path.splitext(X_img_path)[1][1:] not in ALLOWED_EXTENSIONS:
    #     raise Exception("Invalid image path: {}".format(X_img_path))

    if knn_clf is None and model_path is None:
        raise Exception("Must supply knn classifier either thourgh knn_clf or model_path")


    # Find encodings for faces in the test iamge
    #faces_encodings = face_recognition.face_encodings(X_img, known_face_locations=face_locations)

    # Use the KNN model to find the best matches for the test face
    closest_distances = knn_clf.kneighbors(faces_encodings, n_neighbors=2)
    are_matches = [closest_distances[0][i][0] <= distance_threshold for i in range(number_of_faces)]

    # Predict classes and remove classifications that aren't within the threshold
    return [(pred) if rec else ("unknown") for pred, rec in zip(knn_clf.predict(faces_encodings), are_matches)]

def predict(face_locations, faces_encodings, knn_clf=None, model_path=None, distance_threshold=0.42):
    """
    Recognizes faces in given image using a trained KNN classifier

    :param X_img_path: path to image to be recognized
    :param knn_clf: (optional) a knn classifier object. if not specified, model_save_path must be specified.
    :param model_path: (optional) path to a pickled knn classifier. if not specified, model_save_path must be knn_clf.
    :param distance_threshold: (optional) distance threshold for face classification. the larger it is, the more chance
           of mis-classifying an unknown person as a known one.
    :return: a list of names and face locations for the recognized faces in the image: [(name, bounding box), ...].
        For faces of unrecognized persons, the name 'unknown' will be returned.
    """
    # if not os.path.isfile(X_img_path) or os.path.splitext(X_img_path)[1][1:] not in ALLOWED_EXTENSIONS:
    #     raise Exception("Invalid image path: {}".format(X_img_path))

    if knn_clf is None and model_path is None:
        raise Exception("Must supply knn classifier either thourgh knn_clf or model_path")

  
    # If no faces are found in the image, return an empty result.
    if len(face_locations) == 0:
        return []

    # Find encodings for faces in the test iamge
    #faces_encodings = face_recognition.face_encodings(X_img, known_face_locations=face_locations)

    # Use the KNN model to find the best matches for the test face
    closest_distances = knn_clf.kneighbors(faces_encodings, n_neighbors=2)
    are_matches = [closest_distances[0][i][0] <= distance_threshold for i in range(len(face_locations))]

    # Predict classes and remove classifications that aren't within the threshold
    return [(pred, loc) if rec else ("unknown", loc) for pred, loc, rec in zip(knn_clf.predict(faces_encodings), face_locations, are_matches)]

def cnn_compare(face_encodings):
    """

    :param encoding set from the image
    :param unidentied face location array [top:bottom, left:right]
    : returns: names
    """
    face_names = []
    unidentified_faces = []
    found_externalid = []
    # # ------------------------------------------ CNN Model Comparision -----------------------------
    for face_encoding in face_encodings:
        # See if the face is a match for the known face(s)
        matches = face_recognition.compare_faces(cnn_known_face_encodings, face_encoding, tolerance=0.40)
        # If a match was found in known_face_encodings, just use the first one.
        if True in matches:
            first_match_index = matches.index(True)
            name = cnn_known_face_names[first_match_index]
            personid = cnn_known_personid[first_match_index]
            print("Match PID {}".format(personid))
            externalid = 0
            # check for the person id is registered in the attenadance or not if TRUE we will not call the attendance for the day
            if(not roi.db.ismemberrecorded_by_personid(personid)):
                externalid = roi.db.get_member_by_id(personid)
                print("Call DB  to insert a record : "+ str(externalid))
                roi.db.insert_attendance((personid,))
                print("Call CCB service with  External id : "+ str(externalid))
                ccb.record_attendance_external_id(externalid)
            face_names.append(name)
        else:
            unidentified_faces.append(face_encoding)
            face_names.append("Unidentified")
    # # ----------------------------------------------------------------------------------------------
    return face_names,  unidentified_faces

#load the encoded image vecors from db
cnn_known_face_names, cnn_known_face_encodings, cnn_known_personid = get_cnn_dataset()
