import face_recognition.api as face_recognition
import cv2
import click
import pickle
#import roi_backbone.mlearning_knn_model as mlearning
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

recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read('trainer/trainer_haar.yml')
cascadePath = "cascade_data/haarcascade_frontalface.xml"
faceCascade = cv2.CascadeClassifier(cascadePath)
unidentified_image_dir = "../unidentified_images"
img_path = "sample.jpg"
# Load a trained KNN model (if one was passed in)
knn_clf = None
# with open(model_path, 'rb') as f:
#     knn_clf = pickle.load(f)

while True:
        # Grab a single frame of video
    #ret, frame = video_capture.read()

    # rgbimage = cv2.cvtColor(frame, cv2.RGB)
    # Resize frame of video to 1/4 size for faster face recognition processing
    #small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

    # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
    #rgb_small_frame = small_frame[:, :, ::-1]
    # rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
    # Only process every other frame of video to save time
    if process_this_frame:
        # Find all the faces and face encodings in the current frame of video
        #face_locations = face_recognition.face_locations(rgb_small_frame, number_of_times_to_upsample=2)
        #face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations, num_jitters=50)
        # Find all people in the image using a trained classifier model
        # Note: You can pass in either a classifier file name or a classifier model instance
        #load image from the image file
        image = face_recognition.load_image_file(img_path)
        # convert the image to gray scale
        gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
        face_names = []
        faces = faceCascade.detectMultiScale( 
            gray,
            scaleFactor = 1.2,
            minNeighbors = 5,
        )
        print("Number of faces"+ str(len(faces)))
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
            face_names.append(str(id))
        #predictions = mlearning.predict(face_locations, face_encodings, knn_clf=knn_clf, model_path=None)
           # Print results on the console
        #print(predictions)

        
        
        # for id, (top, right, bottom, left) in faces:
        #     #print("- Found {} at ({}, {})".format(name, left, top))
        #     # if(name == "Unknown"):
        #     #     learning_dataset.append(face_encoding)
        #     if(id > 1):
        #         print("- known  {} at ({} X {})".format(str(id), right - left, bottom - top))
        #         face_names.append(str(id))
        #     else:
        #         # if the face is unknown look for the CNN model comparision
        #         loc_width = right - left 
        #         loc_height = bottom - top
        #         print("unknown")
                

    process_this_frame = not process_this_frame

    # Display the results
#     for (top, right, bottom, left), name in zip(face_locations, face_names):
#         # Scale back up face locations since the frame we detected in was scaled to 1/4 size
#         top *= 4
#         right *= 4
#         bottom *= 4
#         left *= 4

#         # Draw a box around the face
#         cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

#         # Draw a label with a name below the face
#         cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
#         font = cv2.FONT_HERSHEY_DUPLEX
#         cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

#     # Display the resulting image
#     cv2.imshow('Video', frame)

#     # Hit 'q' on the keyboard to quit!
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         #print(learning_dataset)
#         break
  
# # Release handle to the webcam
# video_capture.release()
# cv2.destroyAllWindows()
