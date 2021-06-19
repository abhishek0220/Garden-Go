from Garden_Go import schemas
from io import BytesIO
from PIL import Image
import base64
import uuid
import os
from Garden_Go.utils.cloud_storage import CloudStorage


def upload_user_image(user: schemas.UserCreate) -> str:
    cloud_storage = CloudStorage()
    image_data = bytes(user.display_picture, encoding="ascii")
    im = Image.open(BytesIO(base64.b64decode(image_data)))
    tmp_name = ''.join(user.name.split()).lower()[:8]
    loc = f'{tmp_name}_{str(uuid.uuid4())}.jpg'
    file_loc = os.path.join(os.getcwd(), loc)
    im = im.convert("RGB")
    im.save(file_loc)
    public_url = cloud_storage.upload(file_loc, loc)
    os.remove(file_loc)
    return public_url
