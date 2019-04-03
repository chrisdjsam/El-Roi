# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2, uuid
 
# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(640, 480))
 
# allow the camera to warmup
time.sleep(0.1)

# capture frames from the camera
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
	# grab the raw NumPy array representing the image - this array
	# will be 3D, representing the width, height, and # of channels
	image = frame.array
    newfaceid = str(uuid.uuid4())
    # show the frame
	#cv2.imshow("Frame", image)
    
    # using now() to get current time 
    #current_time = datetime.datetime.now()
    print("Create image for unknow faces :")
    #im = Image.fromarray(eachencoding)
    #im.save("/var/www/ElRoiApp/ElRoiApp/unidentified_images/"+ newfaceid + '_' + str(current_time) + ".jpeg")
    file_path = '~/clientapps/images'
    file_name = newfaceid + '.png'
    cv2.imwrite(os.path.join(file_path, file_name), image)
	key = cv2.waitKey(1) & 0xFF
 
	# clear the stream in preparation for the next frame
	rawCapture.truncate(0)
 
	# if the `q` key was pressed, break from the loop
	if key == ord("q"):
		break