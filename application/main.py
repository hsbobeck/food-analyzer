#
# B457 Final Project - Food Analyzer (user application part)
# authors: Henry Bobeck, Sam Stazinski, Devarshi Bhadouria, Zane Snider
# date: 04-25-22
#

from flask import Flask, render_template, url_for, request, redirect, flash
from werkzeug.utils import secure_filename
from concurrent.futures import process
import os
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.utils import load_img
from tensorflow.keras.applications.mobilenet_v3 import preprocess_input
from PIL import Image
from food_scraper import foodscraper

# flask things
UPLOAD_FOLDER = 'application/static/uploads/'
MAX_MEGABYTES = 32
app = Flask(__name__)
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_MEGABYTES * 1024 * 1024
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])


# filepath to best performing recognition model
recognition_model_path = 'models/model_v2_MobileNetV3.best.hdf5'
recognition_model = None
# stores each expiration model by food class key
expiration_model_paths = {
    'banana': 'models/banana_v1.best.hdf5',
}
expiration_models = { # these are loaded lazily
    'banana': None,
}
expiration_classes = {
    'banana': ['green', 'overripe', 'ripe']
}
expiration_descriptions = {
    'banana': ['It should be ripe soon.', 'It might be a little old.', 'Appears healthy to eat.']
}
nutritional_info = {
    'banana': {
        'kcal': '105',
        'fat': '0.4g',
        'protein': '1.3g',
    }
}
general_info = { # these are loaded lazily

}
IMG_WIDTH, IMG_HEIGHT = 224, 224
# Recognition class names. These must be the same as those used to train the recognition model. Automatically sorted alphabetically
food_101_classes_to_use = ['tacos', 'waffles', 'sushi', 'pizza', 'nachos', 'pancakes', 'hamburger', 'guacamole', 'donuts', 'hot_dog']
custom_classes_to_use = ['banana']
class_names = sorted(food_101_classes_to_use + custom_classes_to_use)
num_classes = len(class_names)

# runs the given image through the relevant models
# img : filepath to image
def process_image(img):
    img_as_array = np.asarray(load_img(img, color_mode='rgb', target_size=(IMG_WIDTH, IMG_HEIGHT, 3)))
    # run through recognition model
    global recognition_model
    if not recognition_model: # lazy model loading
        recognition_model = tf.keras.models.load_model(recognition_model_path)
    img = preprocess_input(img_as_array)
    img = np.array( [img] ) # this is necessary because the model expects a batch size as first dimension - this will set it to 1!
    prediction = recognition_model.predict(img)
    prediction = np.argmax(prediction)
    prediction = class_names[prediction]
    # if applicable, run through relevant expiration model
    global expiration_models
    expiration = None
    nutritional = None
    if prediction in expiration_model_paths:
        if not expiration_models[prediction]: # lazy model loading
            expiration_models[prediction] = tf.keras.models.load_model(expiration_model_paths[prediction])
        img = preprocess_input(img_as_array)
        img = np.array( [img] )
        expiration = expiration_models[prediction].predict(img)
        expiration = np.argmax(expiration)
        expiration = expiration_descriptions[prediction][expiration]
        nutritional = nutritional_info[prediction]
    # run through general info script
    global general_info
    general = None
    if prediction in general_info: # already loaded
        general = general_info[prediction]
    else: # load for first time
        request = [prediction]
        general = foodscraper.vehicle(request)[prediction][0]
        print(general)
        general_info[prediction] = general
        

    # show results
    return prediction, expiration, nutritional, general

@app.route('/', methods=['GET']) #'POST',
def index():
    if request.method == 'POST':
        pass
    else:
        return render_template('index.html')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No image selected for uploading')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        print('upload_image filename: ' + filename)
        # process image through model
        prediction, expiration, nutritional, general = process_image(filepath)
        #flash('Image successfully uploaded and displayed below')
        return render_template('index.html', filename=filename, prediction=prediction, expiration=expiration, nutritional=nutritional, general=general)
    else:
        flash('Allowed image types are -> png, jpg, jpeg, gif')
        return redirect(request.url)

@app.route('/display/<filename>')
def display_image(filename):
    #print('display_image filename: ' + filename)
    return redirect(url_for('static', filename='uploads/' + filename), code=301)

if __name__ == "__main__":
    app.run(debug=True)
