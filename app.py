from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
import os
import requests
from io import BytesIO
from PIL import Image

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Dummy model function (replace this with your real model logic)
def predict_disease_combined(image_path):
    # Simulate prediction
    return {
        "Plant": "Tomato",
        "Disease": "Early Blight",
        "Confidence": 95.5,
        "Prevention": "Use fungicides and practice crop rotation."
    }

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    if 'image' not in request.files:
        return jsonify({"Error": "No image part in the request."})

    file = request.files['image']

    if file.filename == '':
        return jsonify({"Error": "No file selected."})

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(image_path)

        result = predict_disease_combined(image_path)

        # Optionally delete uploaded file
        os.remove(image_path)

        return jsonify(result)

    return jsonify({"Error": "File type not allowed."})

@app.route('/predict_url', methods=['POST'])
def predict_url():
    try:
        data = request.get_json()
        image_url = data.get('image_url', '')

        if not image_url:
            return jsonify({"Error": "No image URL provided."})

        response = requests.get(image_url)
        if response.status_code != 200:
            return jsonify({"Error": "Failed to fetch image from URL."})

        image_bytes = BytesIO(response.content)

        # Save to temp file
        temp_path = os.path.join(app.config['UPLOAD_FOLDER'], "temp_image.jpg")
        with open(temp_path, 'wb') as f:
            f.write(image_bytes.read())

        result = predict_disease_combined(temp_path)

        if os.path.exists(temp_path):
            os.remove(temp_path)

        return jsonify(result)
    except Exception as e:
        return jsonify({"Error": str(e)})

if __name__ == '__main__':
    app.run(debug=True)
