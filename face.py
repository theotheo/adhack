import time 
import requests
import cv2
import operator
import numpy as np
import http.client, urllib.request, urllib.parse, urllib.error, base64, requests, json 


#Import library to display results
# import matplotlib.pyplot as plt
# %matplotlib inline 


#Subscribtion to Cognitive Services
#Simply replace subscription key with your Cognitive API Subscription Key the key below is for Demo purpose only
subscription_key = '8fa04488358e43ffbec4b11173fa42ca'
uri_base = 'https://westeurope.api.cognitive.microsoft.com' 

headers = {
#     'Content-Type': 'application/json',
    'Content-Type': 'application/octet-stream',
    'Ocp-Apim-Subscription-Key': subscription_key,
}

# Request parameters.
params = {
    'returnFaceId': 'true',
    'returnFaceLandmarks': 'false',
#     'returnFaceAttributes': 'age,gender,headPose,smile,facialHair,glasses,emotion,hair,makeup,occlusion,accessories,blur,exposure,noise',
    'returnFaceAttributes': 'age,gender'
}

def face(fn):
    try:
        # Execute the REST API call and get the response.
        # fn = '/home/i/LABS/adhack/vasya.jpg'
        # fn = '/home/i/LABS/adhack/oleg.jpg'
    #     fn = '/home/i/LABS/adhack/olya.jpg'
        img = open(fn, 'rb')
        response = requests.post(uri_base + '/face/v1.0/detect', data=img, headers=headers, params=params)
    #     response = requests.request('POST', uri_base + '/face/v1.0/detect', json=body,data=None, headers=headers, params=params)

        parsed = json.loads(response.text)

        return(parsed)
        
    except Exception as e:
        print('Error:')
        print(e)
        return({})