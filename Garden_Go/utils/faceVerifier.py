import asyncio
import io
import glob
import os
import sys
import time
import uuid
import requests
from urllib.parse import urlparse
from io import BytesIO
# To install this module, run:
# python -m pip install Pillow
from PIL import Image, ImageDraw
from azure.cognitiveservices.vision.face import FaceClient
from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.vision.face.models import TrainingStatusType, Person
from dotenv import load_dotenv
load_dotenv()


class face_client():
    def __init__(self):
        self.KEY = os.environ.get('FACEKEY')
        self.ENDPOINT = os.environ.get('FACEENDPOINT')
    
    def setup(self):
        face_client = FaceClient(self.ENDPOINT, CognitiveServicesCredentials(self.KEY))
        return face_client

class faceVerifier():
    def __init__(self, img1Path: str, img2Url: str):
        self.faceClient = face_client().setup()
        self.img1Path = img1Path
        self.img2Url = img2Url
    
    def getFaceID(self):
        image = open(self.img1Path, 'r+b')
        faces = self.faceClient.face.detect_with_stream(image, detection_model='detection_03')
        return faces[0].face_id
    
    def isSame(self):
        multi_image_name = os.path.basename(self.img2Url)
        detected_faces2 = self.faceClient.face.detect_with_url(url=self.img2Url, detection_model='detection_03')
        
        second_image_face_IDs = list(map(lambda x: x.face_id, detected_faces2))
        first_image_face_ID = self.getFaceID()
        similar_faces = self.faceClient.face.find_similar(face_id=first_image_face_ID, face_ids=second_image_face_IDs)
        if not similar_faces:
            print('No similar faces found in', multi_image_name, '.')
            return False
    
        else:
            print('Similar faces found in', multi_image_name + ':')
            for face in similar_faces:
                first_image_face_ID = face.face_id
        
            face_info = next(x for x in detected_faces2 if x.face_id == first_image_face_ID)
            if face_info:
                print('  Face ID: ', first_image_face_ID)
            return True
    



    
    

if __name__ == "__main__":
    testImg1 = "testImgs/messi.jpeg"
    testImg2 = "testImgs/cristiano.jpg"

    testUrl = "https://upload.wikimedia.org/wikipedia/commons/d/d9/Lionel_Messi_20180626_%28cropped%29.jpg"
    fv = faceVerifier(testImg2, testUrl)
    print(fv.isSame())
    print("Done")
