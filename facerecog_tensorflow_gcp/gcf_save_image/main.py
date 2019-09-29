import io
import cv2
import ast
import base64
import datetime
import numpy as np
from PIL import Image
from google.cloud import storage


# Take in base64 string and return PIL image
def stringToImage(base64_string):
    imgData = base64.b64decode(base64_string)
    return Image.open(io.BytesIO(imgData)) , True


def hello_pubsub(event, context):
    """Triggered from a message on a Cloud Pub/Sub topic.
    Args:
         event (dict): Event payload.
         context (google.cloud.functions.Context): Metadata for the event.
    """
    print ("===>>> ", event)
    print ("===>>> ", context)
    base64_string = base64.b64decode(event['data']).decode('utf-8') #ast.literal_eval(event.decode('utf-8'))    
    print(base64_string)
    img, status = stringToImage(base64_string)
    
    if status:
        filename = str(datetime.datetime.now()) + '.jpg'
        img = np.array(img)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = cv2.imencode('.jpg', img)[1]
        img = img.tobytes()

        client = storage.Client()
        bucket = client.bucket("face_recog_image")
        bucket.blob(filename).upload_from_string(img)
        print ("===>>> INFO: Image decoding success")
        print ("===>>> INFO: Save image success")
        
    else:
        print ("===>>> INFO: Image decoding error")
                                
