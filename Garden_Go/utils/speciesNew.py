import base64
import requests
import os 
import json
API_KEY = os.getenv("PLANT_ID_KEY")


def identifyPlant(encdImg):
    images = [encdImg]
    # images.append(encdImg)
    # see the docs for more optional attributes
    # https://github.com/Plant-id/Plant-id-API/wiki/Plant-details
    params = {
        "api_key": API_KEY,
        "images": images,
        "modifiers": ["crops_fast"],
        "plant_language": "en",
        "plant_details": ["common_names",
                          "edible_parts",
                          "name_authority",
                          "propagation_methods",
                          "taxonomy",
                          "url",
                          "wiki_description",
                          "wiki_image"
                         ],
        }

    headers = {
        "Content-Type": "application/json"
        }

    response = requests.post("https://api.plant.id/v2/identify",
                             json=params,
                             headers=headers)
    print(response)
    print("##############################")
    return response.json()


def getSpeciesfromSrc(imgSrc: str):
    with open(imgSrc,"rb") as imgFile:
        imgEncd = base64.b64encode(imgFile.read()).decode("ascii")
    return identifyPlant(imgEncd)


def getSpecies(imgraw: bytes):
    imgEncd = base64.b64encode(imgraw).decode("ascii")
    return identifyPlant(imgEncd)


def getScore(speciesName: str):
    # Make a points based system later.
    return 5

if __name__ == '__main__':
    val = getSpeciesfromSrc("./pic1.jpeg")
    print(json.dumps(val))