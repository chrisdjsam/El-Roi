import requests
import json, time
import cv2, dlib
import logging

# detect image in from the frame
detector = dlib.get_frontal_face_detector()

# load config from a JSON file (or anything outputting a python dictionary)
with open("roi.webserver.conf") as f:
    config = json.load(f)

#prepare the endpoint
addr = config['postimage']['address']
api_endpoint = addr + config['postimage']['uri']

# Get a reference to webcam #0 (the default one)
video_capture = cv2.VideoCapture(0)
process_this_frame = True

while True:
        # Grab a single frame of video
    ret, frame = video_capture.read()
    # encode image as jpeg
    _, img_encoded = cv2.imencode('.jpg', frame)
    
    # Resize frame of video to 1/4 size for faster face recognition processing
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

    # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
    rgb_small_frame = small_frame[:, :, ::-1]
    rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

    #detect faces from the frame
    dets = detector(rgb_small_frame, 1)
    
    if(len(dets) == 0):
        logging.debug("No faces are in the frame; detected = " + str(len(dets)))
        time.sleep(1)
        continue
    # for i, d in enumerate(dets):
    #     print("detected {} and d {}".format(i,d))
    # Only process every other frame of video to save time
    if process_this_frame:
        
        # prepare headers for http request
        content_type = 'image/jpeg'
        headers = {'content-type': content_type}

        # send http request with image and receive response
        response = requests.post(api_endpoint, data=img_encoded.tostring(), headers=headers)
        # decode response
        print (response.text)
        logging.info(response.text)
    process_this_frame = not process_this_frame
    
    # Hit 'q' on the keyboard to quit!
    if cv2.waitKey(1) & 0xFF == ord('q'):
        #print(learning_dataset)
        break

# Release handle to the webcam
video_capture.release()
cv2.destroyAllWindows()

