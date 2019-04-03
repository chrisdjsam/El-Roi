import cv2, requests
import os, json
from picamera.array import PiRGBArray
from picamera import PiCamera
import uuid, time
import pickle
import numpy as np

# connecting to the database
import os.path

# load config from a JSON file (or anything outputting a python dictionary)
with open("/home/pi/clientapps/roi.webserver.conf") as f:
    config = json.load(f)

#prepare the endpoint
addr = config['postimage']['address']
api_endpoint = addr + config['postimage']['uri']

face_detector = cv2.CascadeClassifier('/home/pi/clientapps/lbpcascade_frontalface.xml')


def image_files_in_folder(folder):
    return [os.path.join(folder, f) for f in os.listdir(folder) if re.match(r'.*\.(jpg|jpeg|png)', f, flags=re.I)]

# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.resolution = (640, 480)
camera.hflip = True
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(640, 480))

# allow the camera to warmup
time.sleep(0.1)
process_this_frame = True
# Initialize some variables
# capture frames from the camera
content_type = 'image/jpeg'
headers = {'content-type': content_type}
print("Request URL :" + api_endpoint)


for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):

	# grab the raw NumPy array representing the image, then initialize the timestamp
	# and occupied/unoccupied text
    image = frame.array
    image = cv2.flip(image, 1)
    _, img_encoded = cv2.imencode('.jpg', image) 
    
    #front face detection
    img = cv2.imdecode(img_encoded, cv2.IMREAD_COLOR)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
  
    #convert the image to gray scale  
    #gray = cv2.imencode(img_encoded, cv2.COLOR_BGR2GRAY)
    file_path = 'images'
    file_name =  'gray.jpg'
    cv2.imwrite(os.path.join(file_path, file_name), gray)

    img_numpy = np.array(image,'uint8')
    faces = face_detector.detectMultiScale(img_numpy, 1.2)
    #faces = face_detector.detectMultiScale(gray, 1.2, 5)
    rawCapture.truncate(0)
    if(len(faces) == 0 ):
        print("No face were detected.")
        continue
    
    if process_this_frame:
        print("Length of faces detected : {}".format(len(faces)))
        response = requests.post(api_endpoint, data=img_encoded.tostring(), headers=headers)
        # decode response
        print (response.text)
        
    key = cv2.waitKey(1) & 0xFF
 
	# clear the stream in preparation for the next frame
    
    time.sleep(0.1)
    process_this_frame = not process_this_frame
   
	# if the `q` key was pressed, break from the loop
    if key == ord("q"):
        break
    
