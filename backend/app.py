from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from inference import VehicleClassifier
from anpr import ANPR
from config import UPLOAD_FOLDER, RESULTS_FOLDER, PLATE_RESULTS_FOLDER, MODEL_PATH, ANPR_MODEL_PATH
import re
app = Flask(__name__)
CORS(app)

# Create necessary directories
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)
os.makedirs(PLATE_RESULTS_FOLDER, exist_ok=True)

# Initialize models
classifier = VehicleClassifier(MODEL_PATH)
anpr_detector = ANPR(ANPR_MODEL_PATH)

@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    classification_result, result_image_path = classifier.predict(filepath)

    return jsonify({
        "classification": classification_result,
        "image_url": f"/static/results/{os.path.basename(result_image_path)}"
    })

@app.route("/anpr_upload", methods=["POST"])
def anpr_upload():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    

    plate_text, plate_image_path = anpr_detector.detect_plate(filepath)

    # Ensure plate_text is a list and take the last item as the number plate
    if isinstance(plate_text, list) and len(plate_text) > 0:
        plate_text = plate_text[-1]  # Get the last recognized text
    
    # Return response
    return jsonify({
        "plate_text": plate_text.strip(),
        "plate_image_url": f"/static/plates/{os.path.basename(plate_image_path)}"
    })




@app.route("/static/results/<filename>")
def get_result_image(filename):
    return send_from_directory(RESULTS_FOLDER, filename)

@app.route("/static/plates/<filename>")
def get_plate_image(filename):
    return send_from_directory(PLATE_RESULTS_FOLDER, filename)

if __name__ == "__main__":
    app.run(debug=True)
