import requests
import json, time
# #import cv2, dlib
# #import dlib
import numpy as np
# import logging
# import picamera

#from picamera.array import PiRGBArray
from picamera import PiCamera
import time, uuid, os

# import the necessary packages
# camera = PiCamera()
# camera.resolution = (640, 480)
# camera.framerate = 32
# camera.hflip = True
# rawCapture = PiRGBArray(camera, size=(640, 480))

 
# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
# camera.resolution = (640, 480)
# camera.framerate = 32

 
# # allow the camera to warmup
# time.sleep(0.1)
# Get a reference to the Raspberry Pi camera.
# If this fails, make sure you have a camera connected to the RPi and that you
#camera = picamera.PiCamera()
#camera.resolution = (320, 240)
camera.resolution = (640, 480)
camera.hflip = True
output = np.empty((640, 480, 3), dtype=np.uint8)

# detect image in from the frame
#detector = dlib.get_frontal_face_detector()

# load config from a JSON file (or anything outputting a python dictionary)
with open("roi.webserver.conf") as f:
    config = json.load(f)

#prepare the endpoint
addr = config['postimage']['address']
api_endpoint = addr + config['postimage']['uri']

# Get a reference to webcam #0 (the default one)
#video_capture = cv2.VideoCapture(0)
process_this_frame = True
i = 0

while True:     
        # capture frames from the camera
#for frame in camera.capture_continuous(rawCapture, 'rgb', use_video_port=True):
    

        # Use the video-port for captures...
        # for foo in camera.capture_continuous(stream, 'jpeg',
        #                                      use_video_port=True):
        #     stream.truncate(0)
        # Grab a single frame of video
    #ret, frame = video_capture.read()
    #print(frame.array)
    print("Capturing image :"+ str(process_this_frame) + str(i))
    #camera.flash_mode = 'on'
    # # Grab a single frame of video from the RPi camera as a numpy array
    camera.capture(output, format="rgb")
    camera.capture(output, format='png')
    i += 1
    #camera.capture(output, resize=(640, 480), format="rgb")
    # encode image as jpeg
    #_, img_encoded = cv2.imencode('.jpg', frame)
    
    # Resize frame of video to 1/4 size for faster face recognition processing
    #small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

    # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
    #rgb_small_frame = small_frame[:, :, ::-1]
    #rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

    #detect faces from the frame
    #dets = detector(rgb_small_frame, 1)
    
    # if(len(dets) == 0):
    #     logging.debug("No faces are in the frame; detected = " + str(len(dets)))
    #     time.sleep(1)
    #     continue
    # for i, d in enumerate(dets):
    #     print("detected {} and d {}".format(i,d))
    # Only process every other frame of video to save time
    if process_this_frame:
        print("Create image for unknow faces :")
        newfaceid = str(uuid.uuid4())
        file_path = '~/clientapps/images'
        file_name = newfaceid + '.png'
        #output = (output >> 2).astype(np.uint8)
        with open(os.path.join(file_path, file_name), 'wb') as f:
            output.tofile(f)

        time.sleep(0.1)
    #     # prepare headers for http request
    
        #content_type = 'image/jpeg'
        #headers = {'content-type': content_type}
    #     print("Request URL :" + api_endpoint)
    #     # send http request with image and receive response
    #     #response = requests.post(api_endpoint, data=img_encoded.tostring(), headers=headers)
        #response = requests.post(api_endpoint, data=output.tostring(), headers=headers)
        #rawCapture.truncate(0)
    #     # decode response
        #print (response.text)
    #     logging.info(response.text)
    process_this_frame = not process_this_frame
    # # clear the stream in preparation for the next frame
	#output.truncate(0)
    # Hit 'q' on the keyboard to quit!
    if 0xFF == ord('q'):
        #print(learning_dataset)
        break

# Release handle to the webcam
# video_capture.release()
# cv2.destroyAllWindows()

