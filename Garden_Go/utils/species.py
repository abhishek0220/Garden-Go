import http.client
import urllib.request
import urllib.parse
import urllib.error
import base64
import os
import json


SUBKEY = os.getenv('SPECIES_API_KEY')

headers = {
    # Request headers
    'Content-Type': 'application/octet-stream',
    'Ocp-Apim-Subscription-Key': SUBKEY,
}

conn = http.client.HTTPSConnection('aiforearth.azure-api.net')


def post(imgBase64: str):
    try:
        conn.request(
            "POST", "/species-classification/v2.0/predict?1&classifyAndDetect", imgBase64, headers)
        response = conn.getresponse()
        body = response.read()
        return json.loads(body)["predictions"][0]

    except Exception as e:
        print(e.__repr__())

    return None


def getSpecies(imgSrc: str):
    with open(imgSrc, "rb") as imgFile:
        resp = post(imgFile.read())
    if resp is None:
        return None
    return (resp["species"], resp["species_common"])


if __name__ == "__main__":
    path = "./something.jpg"
    print(getSpecies(path))
