from oauth2client.client import GoogleCredentials
from google.cloud import bigquery
from googleapiclient import discovery
from googleapiclient import errors
import numpy as np
import json



def get_db_data():
    bigquery_client = bigquery.Client()
    query_job = bigquery_client.query("""SELECT * FROM `braided-grammar-239803.face.face_features` """ )
    res = query_job.result()

    id = []
    name = []
    features = []
    for row in res:
        id.append(row[0])
        name.append(row[1])
        
        tmp = []
        for i in range(512):
            tmp.append(row[2 + i])
        tmp = np.array([tmp])
        features.append(tmp)
    
    print ("===>>> INFO: get all features DONE")
    return id, name, features


def calculate_distance(feature1, feature2):
    feature1 = feature1/np.linalg.norm(feature1, axis=1, keepdims=True)
    feature2 = feature2/np.linalg.norm(feature2, axis=1, keepdims=True)
    dist = np.linalg.norm(feature1 - feature2)
    return dist


def search_similar_face(new_features, th):
    print ("===>>> INFO: calculating the distance")
    new_features = np.array(new_features)
    id, name, features = get_db_data()
    
    dist = []
    for i in features:
        tmp = calculate_distance(i, new_features)
        dist.append(tmp)
        
    dist = np.array(dist)
    rank = np.argpartition(dist, 3)
    print ("===>>> INFO: calculate all distances DONE")
    
    tmp = {}
    tmp['rank1'] = {}
    tmp['rank1']['id'] = id[rank[0]]
    tmp['rank1']['name'] = name[rank[0]]
    tmp['rank1']['distance'] = dist[rank[0]]
    
    tmp['rank2'] = {}
    tmp['rank2']['id'] = id[rank[1]]
    tmp['rank2']['name'] = name[rank[1]]
    tmp['rank2']['distance'] = dist[rank[1]]
    
    tmp['rank3'] = {}
    tmp['rank3']['id'] = id[rank[2]]
    tmp['rank3']['name'] = name[rank[2]]
    tmp['rank3']['distance'] = dist[rank[2]]
    
    return tmp


def face_comparison(req):
    print ("===>>> INFO the request is coming")
    json_data = req.get_json()
    data = json_data.get("predictions", None)
    data = data[0]['output']
    data = np.array([data])
    result = search_similar_face(new_features=data, th=0.7)
    
    headers = {}
    headers['Access-Control-Allow-Origin'] = '*'
    headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS, POST'
    headers['Access-Control-Allow-Credentials'] = 'true'
    headers['Access-Control-Allow-Headers'] = 'Authorization, Content-Type'
    headers['Content-Type'] = 'application/json'
    return (json.dumps(result), 200, headers)
    
    
    



