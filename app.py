from flask import Flask, flash, request, redirect, url_for, render_template
import urllib.request
import os
from werkzeug.utils import secure_filename
import tensorflow as tf
import cv2
import numpy as np

app = Flask(__name__)

UPLOAD_FOLDER = 'static/uploads/'

model = tf.keras.models.load_model('static\model\dog_cat_classifier.h5')
IMAGE_SIZE = (128,128)

app.secret_key = "Janith"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
	

@app.route('/')
def home():
	return render_template('index.html')

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
		file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
		img = cv2.imread('static/uploads/'+filename)
		resized_image = tf.image.resize(img, IMAGE_SIZE)
		scaled_image = resized_image/255
		yhat = model.predict(np.expand_dims(scaled_image, 0))
		
		pred = prediction(yhat)
		
		#print('upload_image filename: ' + filename)
		flash('Image successfully uploaded and displayed below')
		return render_template('index.html', filename=filename,pred = pred)
    
	    
	
	else:
		flash('Allowed image types are - png, jpg, jpeg, gif')
		return redirect(request.url)

@app.route('/display/<filename>')
def display_image(filename):
	#print('display_image filename: ' + filename)
	return redirect(url_for('static', filename='uploads/' + filename), code=301)
    
def prediction(yhat):
	if yhat > 0.5:
		return ("This is Dog")
	else:
		return ("This is Cat")

if __name__ == "__main__":
    app.run(debug = True)