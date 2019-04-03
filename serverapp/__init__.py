import warnings
warnings.filterwarnings("ignore")

from flask import Flask, request, Response, redirect, jsonify

import jsonpickle, os
import numpy as np
import pickle, cv2, uuid, datetime
import ElRoiApp.roi_backbone.api as face_recognition
import ElRoiApp.roi_backbone.mlearning_knn_model as mlearning
import dlib
detector = dlib.get_frontal_face_detector()
# You can change this to any folder on your system
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



# Initialize the Flask application
app = Flask(__name__)

app.root_path = '/var/www/ElRoiApp/ElRoiApp'

@app.route('/uploadimage', methods=['GET', 'POST'])
def upload_image():
    # Check if a valid image file was uploaded
    facefound = False 
    facenames = []
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            return redirect(request.url)

        if file and allowed_file(file.filename):
            # The image file seems valid! Detect faces and return the result.
            facefound, facenames = detect_faces_in_image("",file)
     # # build a response dict to send back to client
    response = {
        'message': 'image received. and face found : {}'.format(facefound),
        'details': 'Found name - {}'.format( ",".join(str(x) for x in facenames))
    }
     # encode response using jsonpickle
    response_pickled = jsonpickle.encode(response)
    return Response(response=response_pickled, status=200, mimetype="application/json")

def detect_faces_in_image(nparr, file_stream = None):
    
    face_names = []
    face_found = False

    # Load the uploaded image file
    if(file_stream is not None):
        img = face_recognition.load_image_file(file_stream)
    else: 
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    # Get face encodings for any faces in the uploaded image
    dets = detector(img, 1)
    print("detected = " + str(len(dets)))
    if(len(dets) != 0):
    
        # Find all the faces and face encodings in the current frame of video
        face_locations = face_recognition.face_locations(img, number_of_times_to_upsample=2)
        face_encodings = face_recognition.face_encodings(img, face_locations, num_jitters=10)

        if len(face_encodings) > 0:
            face_found = True
            # if the face is unknown look for the CNN model comparision
            #app.logger.info("Checking the CNN Model")
            face_names, unidentified_face_encodings = mlearning.cnn_compare(face_encodings)

        print(face_names)
        file_path = '/var/www/ElRoiApp/ElRoiApp/unidentified_images/'
            
        newfaceid = str(uuid.uuid4())
            #current_time = datetime.datetime.now()
        for i, d in enumerate(dets):
            file_name = newfaceid + '_' + str(i) + '.jpg'
            print("Capture images from the frame")
            cv2.imwrite(os.path.join(file_path, file_name), img[d.top():d.bottom(), d.left():d.right()])
                # decode imag
      
        #     print(unidentified_face_encodings)

            
    # Return the result as json
    return face_found, face_names

def write_unidentified_images(nparr):
    #try:
    nparr = np.fromstring(nparr, np.uint8)
    unidentified_img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    newfaceid = str(uuid.uuid4())
    # using now() to get current time 
    current_time = datetime.datetime.now()
    print("Create image for unknow faces :")
    #im = Image.fromarray(eachencoding)
    #im.save("/var/www/ElRoiApp/ElRoiApp/unidentified_images/"+ newfaceid + '_' + str(current_time) + ".jpeg")
    file_path = '/var/www/ElRoiApp/ElRoiApp/unidentified_images/'
    file_name = newfaceid + '.jpg'
    cv2.imwrite(os.path.join(file_path, file_name), unidentified_img)
    
    #except:
    #    pass
    

# route http posts to this method
@app.route('/detect', methods=['POST'])
def imageparser():
    #Initialize some variables
    face_locations = []
    face_encodings = []
    #face_names = []
    req = request
    # convert string of image data to uint8
    nparr = np.fromstring(req.data, np.uint8)
    # decode image
    #img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
   
    facefound, facenames = detect_faces_in_image(nparr, None)
     # # build a response dict to send back to client
    response = {
        'message': 'image received. and face found : {}'.format(facefound),
        'details': 'Found name - {}'.format( ",".join(str(x) for x in facenames))
    }
     # encode response using jsonpickle
    response_pickled = jsonpickle.encode(response)
    return Response(response=response_pickled, status=200, mimetype="application/json")
   
if __name__ == '__main__':
      app.run(host='0.0.0.0')
