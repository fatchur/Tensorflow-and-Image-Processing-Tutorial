from oauth2client.client import GoogleCredentials
from google.cloud import bigquery
from googleapiclient import discovery
from googleapiclient import errors
from google.cloud import pubsub_v1
from PIL import Image
import requests
import io
import uuid
import base64
import cv2
import json
import numpy as np


# Take in base64 string and return PIL image
def stringToImage(base64_string):
    """Function for decoding the base64 image
    
    Arguments:
        base64_string {[type]} -- [description]
    
    Returns:
        [type] -- [description]
    """
    imgData = base64.b64decode(base64_string)
    return Image.open(io.BytesIO(imgData)) , True


def predict_ml_engine(json_data):
    """Function for predicting via ml engine
    
    Arguments:
        json_data {[type]} -- [description]
    
    Returns:
        [type] -- [description]
    """
    PROJECTID = 'braided-grammar-239803'
    projectID = 'projects/{}'.format(PROJECTID)
    modelName = 'insight_face'
    modelID = '{}/models/{}'.format(projectID, modelName)
    credentials = GoogleCredentials.get_application_default()
    ml = discovery.build('ml', 'v1', credentials=credentials)
    request_body = {"instances": [json_data]}
    req = ml.projects().predict(name=modelID, body=request_body)
    
    resp = None
    status = 'fail'
    
    try:
        resp = req.execute()
        status = 'success'
    except errors.HttpError as err:
        resp = str(err._get_reason())
    return resp, status


def save_image(base64string):
    project_id = "braided-grammar-239803"
    topic_name = "save_image"
    
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project_id, topic_name)
    message_future = publisher.publish(topic_path, data=base64string.encode('utf-8'))
    print ("===>>> INFO image is already saved successfully")
    
    
def insert_feature(name, features):
    bigquery_client = bigquery.Client()
    query_str = "INSERT INTO `braided-grammar-239803.face.face_features` (id, name, "
                                      
    # hard loop to add feature name
    for i in range(512):
        query_str = query_str + 'feature' + str(i) + ", "
    query_str = query_str[:-2] + ')'
    query_str = query_str + ' VALUES ('
    query_str = query_str + "'" + str(uuid.uuid1()) + "', " + "'" + name + "', "
    
    # hard loop to add feature name
    for i, val in enumerate(features):
        query_str = query_str + str(val) + ", "
    query_str = query_str[:-2] + ');'
    
    query_job = bigquery_client.query(query_str)
    query_job.result()
    print ('===>>> insert to db success')
    
    
def search_face(resp):
    url = 'https://us-central1-braided-grammar-239803.cloudfunctions.net/face_comparison'
    headers = {'Content-type': 'application/json'}
    json_data = resp
    response = requests.post(url, json=json_data)
    response = response.json()
    return response
    
    
def predict(req):
    json_data = req.get_json()

    # --------------------------------------- #
    # Part for handling options cors problem  #
    # --------------------------------------- #
    if req.method == 'OPTIONS':
        # Allows GET requests from origin https://mydomain.com with
        # Authorization header
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST,OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'
        }
        return ('', 204, headers)

    base64string = json_data.get('image', None)
    task = json_data.get('task', None)
    
    # --------------------------------------- #
    # Saving the image to gcs via pubsub      #
    # --------------------------------------- #
    save_image(base64string)
    
    #---------------------------------------------------------------------------#
    #                     ML Engine Request standard                            #
    # - encode your image with jpg first                                        #
    # - convert it with base64 string                                           #
    # - the format is : {"instances": [json_data]}                              #
    # - json_data = {'input': {'b64': base64.b64encode(jpg_enc_img).decode()},  #
    #                'input2': {'b64': base64.b64encode(jpg_enc_img2).decode()}}#  
    #---------------------------------------------------------------------------#
    jpg_file = {'input': {'b64':base64string}}
    resp, status = predict_ml_engine(jpg_file)
    print ("===>>>INFO: is AI engine job success: ", status) 
    
    # --------------------------------------- #
    # preparing the response json             #
    # --------------------------------------- #
    conclusion={}
    conclusion['data'] = None
    conclusion['message'] = None
    http_status = 400
    
    if status == 'success': 
        http_status = 200
        
        # --------------------------------------- #
        # Check the task is for inserting new face feature  
        # or getting the face identity            #
        # --------------------------------------- #
        if task=='insert':
            print ("===>>>INFO: Trying to insert face feature to gbq")
            info = json_data.get('info', None)
            face_name = info['name']
            features = resp['predictions'][0]['output'] 
            insert_feature(face_name, features)
            conclusion['message'] = "inserting new face to database: success"
        
        elif task=='search':
            print ("===>>>INFO: Trying to search the similar face")
            face_result = search_face(resp)
            conclusion['data'] = face_result
            conclusion['message'] = "searching face identity: success"
            
    else: 
        conclusion['message'] = "fail to process the request image in AI engine"

    headers = {}
    headers['Access-Control-Allow-Origin'] = '*'
    headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS, POST'
    headers['Access-Control-Allow-Credentials'] = 'true'
    headers['Access-Control-Allow-Headers'] = 'Authorization, Content-Type'
    headers['Content-Type'] = 'application/json'
    
    return (json.dumps(conclusion), http_status, headers)

