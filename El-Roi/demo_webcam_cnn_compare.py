import face_recognition.api as face_recognition
import cv2
import os, json
import io
import click
import pickle
import numpy as np

# connecting to the database
import os.path

# create a El-Roi instance
from roi_backbone import ElRoi
# load config from a JSON file (or anything outputting a python dictionary)
with open("roi.conf") as f:
    config = json.load(f)

roi = ElRoi(config)

# Get a reference to webcam #0 (the default one)
video_capture = cv2.VideoCapture(0)
# Load a sample picture nd learn how to recognize it.
click.echo_via_pager('-' * 35, 'red')
click.echo_via_pager('      JIREH SYSTEMS           ', 'Green')
click.echo_via_pager('-' * 35, 'red')



def image_files_in_folder(folder):
    return [os.path.join(folder, f) for f in os.listdir(folder) if re.match(r'.*\.(jpg|jpeg|png)', f, flags=re.I)]


def convert_array(text):
    out = io.BytesIO(text)
    out.seek(0)
    return np.load(out)
# get known people from the trained dataset


def get_known_people_dataset():
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
        known_personid.append(row[roi.db.FIELD_MEMBER_FACE_ENCODING])

    # commiting into the database
    return known_names, known_face_encodings, known_personid

# log the member entry


def logentrybypersonid(personid):
    # cursor.execute("SELECT person FROM tbl_members WHERE person_id = ?", (personid,))
    # row = cursor.fetchone()
    # membername = row[1]
    # memberid = row[0]

    # insert an entry for the id
    cursor.execute(
        "SELECT * FROM tbl_register_timestamp WHERE person_id = ? and datetime(timestamp, 'localtime') > datetime('now', '-1 days', 'localtime') ", (personid,))
    isRecordExist = 0
    # checking wheather the id exist or not
    for row in cursor:
        isRecordExist = 1

    #print('total count - ' + str(isRecordExist))
    if(isRecordExist == 0):
        print("Member id from log:" + str(personid))
        cursor.execute(
            "insert into tbl_register_timestamp(person_id) values ('" + personid + "')")
        # commiting into the database
        connect.commit()
        #print("Time stamp has been added to the member : " + str(personid))
    # else:
        #print("Time stamp has been already found for the member " + personid)
    # return membername

#def analyse_sampledata():


# find most occurace to reduce the un intented data

def store_decoded_image(personid,encoded_image):
    if(personid in learning_dataset):
        if (len(learning_dataset[personid]) != 15):
            learning_dataset[personid].append(encoded_image)
        # else:
        #     analyse_sampledata()
        print("Lenght of the item - "+ str(len(learning_dataset[personid])))
    else:
        learning_dataset[personid] = [encoded_image]
    print(learning_dataset)
    # for key in learning_dataset:zt
    #     print(key, learning_dataset[key])



# Iterate picture folder and get the encoding and facename
# known_face_names, known_face_encodings = scan_known_people('./face_recognition/known_people')
known_face_names, known_face_encodings, known_personid = get_known_people_dataset()

# Initialize some variables
face_locations = []
face_encodings = []
face_names = []
process_this_frame = True
most_occurace = []
mscount = 0
learning_dataset = []
while True:
        # Grab a single frame of video
    ret, frame = video_capture.read()

    # rgbimage = cv2.cvtColor(frame, cv2.RGB)
    # Resize frame of video to 1/4 size for faster face recognition processing
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

    # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
    rgb_small_frame = small_frame[:, :, ::-1]
    # rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
    # Only process every other frame of video to save time
    if process_this_frame:
        # Find all the faces and face encodings in the current frame of video
        face_locations = face_recognition.face_locations(rgb_small_frame, number_of_times_to_upsample=2)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations, num_jitters=15)
        face_names = []
        for face_encoding in face_encodings:
            # See if the face is a match for the known face(s)
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=0.45)
            name = "Unknown"

            # If a match was found in known_face_encodings, just use the first one.
            if True in matches:
                first_match_index = matches.index(True)
                name = known_face_names[first_match_index]

                # get the person id by base name
            #     personid = known_personid[first_match_index]
            #     #most_occurace.append(personid)
            #     #print(most_occurace)
            #     if(mscount >= 15):
            #         #store_decoded_image(personid, face_encoding)
            #         mscount = 0
            #         if(personid != ""):

            #             # insert a record for the known person
            #             logentrybypersonid(personid)

            # # print('-------------------------')
            # if(name == "Unknown"):
            #     learning_dataset.append(face_encoding)

            face_names.append(name)

    process_this_frame = not process_this_frame

    # Display the results
    for (top, right, bottom, left), name in zip(face_locations, face_names):
        # Scale back up face locations since the frame we detected in was scaled to 1/4 size
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4

        # Draw a box around the face
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

        # Draw a label with a name below the face
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

    # Display the resulting image
    cv2.imshow('Video', frame)

    # Hit 'q' on the keyboard to quit!
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print(learning_dataset)
        break
    mscount += 1
# Release handle to the webcam
video_capture.release()
cv2.destroyAllWindows()
