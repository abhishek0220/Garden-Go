from azure.cognitiveservices.vision.customvision.prediction import CustomVisionPredictionClient
from msrest.authentication import ApiKeyCredentials
import os
# from dotenv import load_dotenv
# load_dotenv()


class garbagePredictor:
    def __init__(self):
        ENDPOINT = os.environ.get('GARBAGE_ENDPOINT')
        predictionKey = os.environ.get('GARBAGE_PREDICTION_KEY')
        prediction_credentials = ApiKeyCredentials(in_headers={"Prediction-key": predictionKey})
        self.project_id = os.environ.get('GARBAGE_PROJECT_ID')
        self.published_name = os.environ.get('GARBAGE_PUBLISHED_NAME')
        self.predictor = CustomVisionPredictionClient(endpoint=ENDPOINT, credentials=prediction_credentials)
    
    def classify(self, imgData):
        r = self.predictor.classify_image(project_id= self.project_id, published_name=self.published_name, image_data=imgData)

        return r.predictions[0].tag_name
        

if __name__ == '__main__':
    gp = garbagePredictor()
    
    testImg1 = open('testImgs/banana.jpg', 'r+b')
    testImg2 = open('testImgs/bottle.jpg', 'r+b')
    print(gp.classify(testImg2))