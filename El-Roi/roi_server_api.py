import warnings
warnings.filterwarnings("ignore")

from flask import Flask, request, Response
import jsonpickle
import numpy as np
import pickle, cv2, uuid, datetime
import roi_backbone.api as face_recognition
import roi_backbone.mlearning_knn_model as mlearning
import click, logging


# set the classifier location
model_path="trained_member_knn_model_new.clf"


# Load a trained KNN model (if one was passed in)
knn_clf = None
with open(model_path, 'rb') as f:
    knn_clf = pickle.load(f)


# Initialize the Flask application
app = Flask(__name__)
click.echo_via_pager('-' * 35, 'red')
click.echo_via_pager('      ROI SYSTEMS           ', 'Green')
click.echo_via_pager('-' * 35, 'red')

# route http posts to this method
@app.route('/api/imageparser', methods=['POST'])
def imageparser():
    #Initialize some variables
    face_locations = []
    face_encodings = []
    #face_names = []
    req = request
    # convert string of image data to uint8
    nparr = np.fromstring(req.data, np.uint8)
    # decode image
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
   
    # Find all the faces and face encodings in the current frame of video
    face_locations = face_recognition.face_locations(img, number_of_times_to_upsample=2)
    face_encodings = face_recognition.face_encodings(img, face_locations, num_jitters=10)

    face_names = []
    # if the face is unknown look for the CNN model comparision
    app.logger.info("Checking the CNN Model")
    face_names, unidentified_face_encodings = mlearning.cnn_compare(face_encodings)
    # for x in face_new_names:
    #     face_names.append(x)
    app.logger.info("Length of face_names : {}, unidentified names : {}".format(len(face_names), len(unidentified_face_encodings)))
    if(len(unidentified_face_encodings) >= 1):
        #app.logger.info("face encodings {}".format(unidentified_face_encodings))
        # # ------------------------------------------ KNN Model Prediction ------------------------------
        # # Note: You can pass in either a classifier file name or a classifier model instance
        predictions = mlearning.predict_without_location(len(unidentified_face_encodings), unidentified_face_encodings, knn_clf=knn_clf, model_path=None)
        app.logger.info(predictions)
        for name in predictions:
            app.logger.debug("- Found {} ".format(name))
            if(len(str(name).split("_")) > 1):
                app.logger.debug("Name: "+ str(name).split("_")[1])
                face_names.append(str(name).split("_")[1])
            else:
                newfaceid = str(uuid.uuid4())
                # using now() to get current time 
                current_time = datetime.datetime.now()
                cv2.imwrite('./unidentified_images/' + newfaceid + '_' + str(current_time) + '.jpg', img)
                    
        app.logger.debug('Found name - {}'.format( ",".join(str(x) for x in face_names)) )
                
    # # build a response dict to send back to client
    response = {
        'message': 'image received. size={}x{}'.format(img.shape[1], img.shape[0]),
        'details': 'Found name - {}'.format( ",".join(str(x) for x in face_names))
    }
    
    # encode response using jsonpickle
    response_pickled = jsonpickle.encode(response)

    return Response(response=response_pickled, status=200, mimetype="application/json")
 
if __name__ == '__main__':
      app.run(host='0.0.0.0', port=5001, debug=True)
