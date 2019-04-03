import io
import roi_backbone.api as face_recognition
import cv2
import os
import re
import click
import sqlite3
import pickle
import numpy as np
import uuid, json

# connecting to the database
import os.path
# create a El-Roi instance
from roi_backbone import ElRoi
# load config from a JSON file (or anything outputting a python dictionary)
with open("../roi.conf") as f:
    config = json.load(f)

roi = ElRoi(config)

def insertmember(member_firstname, member_lastname, member_face_encoding):

    params = (member_firstname, member_lastname)

    personid = ""
    personid = roi.db.get_member_by_name(params)
    if(personid == ""):
        personid = str(uuid.uuid4())
        params = (member_firstname, member_lastname, "", "", personid,'')
        roi.db.insert_member(params)
   
    if(personid != ""):
        storememberfaces(personid, member_face_encoding)
    return personid


def storememberfaces(personid, member_face_encoding):
    # generate member_face_id
    member_face_id = str(uuid.uuid4())
    # insering a new student data
    params = (personid, member_face_id, pickle.dumps(member_face_encoding))
    roi.db.insert_faces(params)

# scan images from the folder

def scan_known_people(train_dir):
    known_names = []
    known_face_encodings = []
    print("CNN image pre-process starting.........")
      # Loop through each person in the training set
    for class_dir in os.listdir(train_dir):
        if not os.path.isdir(os.path.join(train_dir, class_dir)):
            continue

        # Loop through each training image for the current person
        for file in image_files_in_folder(os.path.join(train_dir, class_dir)):
            basename = os.path.splitext(os.path.basename(file))[0]
            print('{} filename'.format(basename))
            if(len(basename.split("_")) > 1):
                member_firstname = basename.split('_')[0]
                member_lastname = basename.split('_')[1]
            else:
                member_firstname = basename
                member_lastname = ""

            face_image = face_recognition.load_image_file(file)
            face_locations = face_recognition.face_locations(face_image, number_of_times_to_upsample=2, model='cnn')
            encodings = face_recognition.face_encodings(face_image, known_face_locations=face_locations, num_jitters=30)
            if len(encodings) > 1:
                click.echo("WARNING: More than one face found in {}. Only considering the first face.".format(file))

            if len(encodings) == 0:
                click.echo("WARNING: No faces found in {}. Ignoring file.".format(file))
            else:
                known_names.append(basename)
                # known_face_encodings.append(encodings[0])
                insertmember(member_firstname, member_lastname, encodings[0])
                click.echo(f'Member {basename} has been added.', color='green')


def image_files_in_folder(folder):
    return [os.path.join(folder, f) for f in os.listdir(folder) if re.match(r'.*\.(jpg|jpeg|png)', f, flags=re.I)]


# Iterate picture folder and get the encoding and facename
scan_known_people('knn_training_model/training_dataset/')

