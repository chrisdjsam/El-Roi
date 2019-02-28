import face_recognition.api as face_recognition
import cv2
import click
import pickle
import roi_backbone.mlearning_knn_model as mlearning
import datetime, uuid
# connecting to the database
import os.path


# Get a reference to webcam #0 (the default one)
video_capture = cv2.VideoCapture(0)
# Load a sample picture nd learn how to recognize it.
click.echo_via_pager('-' * 35, 'red')
click.echo_via_pager('      JIREH SYSTEMS           ', 'Green')
click.echo_via_pager('-' * 35, 'red')


# Initialize some variables
cnn_face_locations = []
cnn_face_encodings = []
cnn_face_names = []
process_this_frame = True
model_path="trained_member_knn_model_new.clf"
    
# Load a trained KNN model (if one was passed in)
knn_clf = None
with open(model_path, 'rb') as f:
    knn_clf = pickle.load(f)

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
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations, num_jitters=50)
        # Find all people in the image using a trained classifier model
        # Note: You can pass in either a classifier file name or a classifier model instance
   
        predictions = mlearning.predict(face_locations, face_encodings, knn_clf=knn_clf, model_path=None)
           # Print results on the console
        #print(predictions)

        face_names = []
        
        for name, (top, right, bottom, left) in predictions:
            #print("- Found {} at ({}, {})".format(name, left, top))
            # if(name == "Unknown"):
            #     learning_dataset.append(face_encoding)
            if(len(str(name).split("_")) > 1):
                print("- known  {} at ({} X {})".format(str(name), right - left, bottom - top))
                face_names.append(str(name).split("_")[1])
            else:
                # if the face is unknown look for the CNN model comparision
                loc_width = right - left 
                loc_height = bottom - top
                print("unknown")
                #face_names.append("unknown")
                if((name == "unknown") and ((loc_height > 20) and (loc_height > 20))):
                    # if the face is unknown look for the CNN model comparision
                    print("Checking the CNN Model")
                    rgbimage = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
                    mlearning.cnn_compare(face_encodings)
                    newfaceid = str(uuid.uuid4())
                    # using now() to get current time 
                    current_time = datetime.datetime.now()
                    cv2.imwrite('./unidentified_images/' + newfaceid + '_' + str(current_time) + '.jpg',
                        rgbimage[top:bottom, left:right])

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
        #print(learning_dataset)
        break
  
# Release handle to the webcam
video_capture.release()
cv2.destroyAllWindows()
