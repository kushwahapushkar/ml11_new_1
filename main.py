# from flask import Flask,render_template

# app = Flask(__name__)

# @app.route('/')
# def welcome():
#     return render_template('index.html')
#     # return "fo"

# if __name__ == '__main__':
#     app.run(debug=True)


# 1. creating Flask application
# 2. creating .pkl file of our Model
# 3. adding respective functionalities of buttons/ creating api's 

from flask import Flask, flash, request, redirect, url_for, render_template
import urllib.request
import os
from werkzeug.utils import secure_filename
import pickle
from PIL import Image
# import torchvision
import torchvision.transforms as transforms
import layers
import torch
app = Flask(__name__)

UPLOAD_FOLDER = 'static/uploads/'

app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'webp'])

model = layers.get_model()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    return render_template('index.html')
    # return "hello world"

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
        blur_img = Image.open(os.path.join(app.config['UPLOAD_FOLDER'],filename))
        blur_img = blur_img.convert('RGB')
        transform = transforms.ToTensor()
        blur_tensor = transform(blur_img)
        _,height,width = blur_tensor.shape
        height = height - height%4
        width = width - width%4
        blur_tensor = blur_tensor[:,:(height),:(width)]

        with torch.inference_mode():
            deblur_tensor = model(blur_tensor)
            deblur_tensor = (deblur_tensor>0).type(torch.float) * deblur_tensor # removing negative values 
        rev_transform = transforms.ToPILImage()
        deblur_img = rev_transform(deblur_tensor.detach())
        deblur_img.save(os.path.join(app.config['UPLOAD_FOLDER'], 'deblur.png'))
        # flash('Image deblurred succesfully')
        return render_template('index.html', filename=filename)
    else:
        flash('Allowed image types are - png, jpg, jpeg, webp')
        return redirect(request.url)

@app.route('/display/<filename>')
def display_image(filename):
    #print('display_image filename: ' + filename)
    return redirect(url_for('static', filename='uploads/' + filename), code=301)

if __name__ == "__main__":
    app.run(debug=True)
