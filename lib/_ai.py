import os

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import numpy as np
import keras
import base64

from io import BytesIO
from PIL import Image

model: keras.Model = keras.models.load_model('./models/1.keras')

ANSWERS = ['bag', 'bed', 'bucket', 'chair', 'clock', 'curtain', 'hat']

def get_predictions(images):
    """ Get predictions of image classification """
    _model: keras.Model = keras.models.clone_model(model)
    _model.set_weights(model.get_weights())
    predictions = []
    for image in images:
        image_io = BytesIO(base64.b64decode(image))
        image = np.asarray(Image.open(image_io)).reshape(1, 100, 100, 3)
        
        prediction = _model(image).numpy() # <- thread safe
        predictions.append(prediction)

    return predictions

def get_solutions(images: list[str], target: str):
    """ Solve an AWS captcha """
    solutions = []
    predictions = get_predictions(images)
    for i, prediction in enumerate(predictions, 0):
        answer = ANSWERS[prediction.argmax(1)[0]]
        if answer == target:
            solutions.append(i)

    return solutions