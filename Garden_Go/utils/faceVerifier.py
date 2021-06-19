import os
from azure.cognitiveservices.vision.face import FaceClient
from msrest.authentication import CognitiveServicesCredentials

# from dotenv import load_dotenv
# load_dotenv('../../.env')


class FaceClientCustom:
    def __init__(self) -> None:
        self.KEY = os.environ.get('FACEKEY')
        self.ENDPOINT = os.environ.get('FACEENDPOINT')
    
    def setup(self) -> FaceClient:
        face_client = FaceClient(self.ENDPOINT, CognitiveServicesCredentials(self.KEY))
        return face_client


class FaceVerifier:
    def __init__(self, img1path: str, img2url: str) -> None:
        self.faceClient = FaceClientCustom().setup()
        self.img1Path = img1path
        self.img2Url = img2url
    
    def get_face_id(self):
        image = open(self.img1Path, 'r+b')
        faces = self.faceClient.face.detect_with_stream(image, detection_model='detection_03', face_id_time_to_live=100)
        return faces[0].face_id
    
    def is_face_same(self):
        multi_image_name = os.path.basename(self.img2Url)
        detected_faces2 = self.faceClient.face.detect_with_url(
            url=self.img2Url,
            detection_model='detection_03',
            face_id_time_to_live=100
        )
        second_image_face_id = list(map(lambda x: x.face_id, detected_faces2))
        first_image_face_id = self.get_face_id()
        similar_faces = self.faceClient.face.find_similar(face_id=first_image_face_id, face_ids=second_image_face_id)
        if not similar_faces:
            print('No similar faces found in', multi_image_name, '.')
            return False
    
        else:
            print('Similar faces found in', multi_image_name + ':')
            for face in similar_faces:
                first_image_face_id = face.face_id
        
            face_info = next(x for x in detected_faces2 if x.face_id == first_image_face_id)
            if face_info:
                print('  Face ID: ', first_image_face_id)
            return True


def test_code():
    test_img1 = "testImgs/messi.jpeg"
    test_img2 = "testImgs/cristiano.jpg"

    test_url = "https://upload.wikimedia.org/wikipedia/commons/d/d9/Lionel_Messi_20180626_%28cropped%29.jpg"
    fv = FaceVerifier(test_img1, test_url)
    print(fv.is_face_same())
    print("Done")
