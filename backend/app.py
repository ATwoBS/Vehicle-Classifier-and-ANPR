from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
import os
from pathlib import Path
from config import UPLOAD_FOLDER, RESULTS_FOLDER, PLATE_RESULTS_FOLDER, ANPR_MODEL_PATH, backend_dir, project_root, MODEL_PATH

app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)

# Debug output
print(f"🔍 MODEL PATH DEBUG:")
print(f"   Backend dir: {backend_dir}")
print(f"   Project root: {project_root}")
print(f"   Model path: {MODEL_PATH}")
print(f"   Model exists: {os.path.exists(MODEL_PATH)}")

# Import config after we know the structure
try:
    from config import UPLOAD_FOLDER, RESULTS_FOLDER, PLATE_RESULTS_FOLDER, ANPR_MODEL_PATH
    print(f"✅ Config imported successfully")
    print(f"   ANPR_MODEL_PATH: {ANPR_MODEL_PATH}")
    print(f"   ANPR model exists: {os.path.exists(ANPR_MODEL_PATH)}")
except Exception as e:
    print(f"❌ Config import failed: {e}")
    exit(1)

# Import other modules
try:
    from backend.model_security_checker import ModelSecurityChecker, check_model_security
    print(f"✅ Security checker imported")
except Exception as e:
    print(f"❌ Security checker import failed: {e}")
    exit(1)

print("Checking model security...")
# Use the calculated model path instead of hardcoded relative path
if check_model_security(MODEL_PATH):
    checker = ModelSecurityChecker()
    print("✅ Model loaded safely!")
else:
    print("❌ Model failed security check!")
    exit(1)  # Exit if model is not safe

# Create necessary directories
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)
os.makedirs(PLATE_RESULTS_FOLDER, exist_ok=True)

# Additional security check with detailed analysis
try:
    checker = ModelSecurityChecker(str(backend_dir / "model_imports.whitelist"))
    result = checker.check_model_file(MODEL_PATH)
    if result['safe']:
        print("✅ Model passed detailed security check")
    else:
        print(f"⚠️  Model has blocked imports: {result['blocked_imports']}")
        # Decide whether to continue or exit based on your security requirements
    
except Exception as e:
    print(f"❌ Security check failed: {e}")

# Initialize models only after security checks pass
print(f"🔍 Attempting to load models...")
print(f"   VehicleClassifier with: {MODEL_PATH}")
print(f"   ANPR with: {ANPR_MODEL_PATH}")

try:
    from backend.inference import VehicleClassifier
    print("✅ VehicleClassifier imported")
    classifier = VehicleClassifier(MODEL_PATH)
    print("✅ VehicleClassifier initialized")
except Exception as e:
    print(f"❌ VehicleClassifier failed: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

try:
    from backend.anpr import ANPR
    print("✅ ANPR imported")
    anpr_detector = ANPR(ANPR_MODEL_PATH)
    print("✅ ANPR initialized")
except Exception as e:
    print(f"❌ ANPR failed: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print(f"✅ All models loaded successfully!")

# Serve React App
@app.route('/')
def serve_react_app():
    return send_from_directory(app.static_folder, 'index.html')

# Serve static files (JS, CSS, images from React build)
@app.route('/<path:path>')
def serve_static_files(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        # If file doesn't exist, serve React app (for client-side routing)
        return send_from_directory(app.static_folder, 'index.html')

# Health check endpoint for HF Spaces
@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy', 'message': 'Server is running'}), 200


@app.route("/api/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    try:
        classification_result, result_image_path = classifier.predict(filepath)
        return jsonify({
            "classification": classification_result,
            "image_url": f"/static/results/{os.path.basename(result_image_path)}"
        })
    except Exception as e:
        return jsonify({"error": f"Classification failed: {str(e)}"}), 500

@app.route("/api/anpr_upload", methods=["POST"])
def anpr_upload():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    try:
        plate_text, plate_image_path = anpr_detector.detect_plate(filepath)

        # Ensure plate_text is a list and take the last item as the number plate
        if isinstance(plate_text, list) and len(plate_text) > 0:
            plate_text = plate_text[-1]  # Get the last recognized text
        
        # Return response
        return jsonify({
            "plate_text": plate_text.strip(),
            "plate_image_url": f"/static/plates/{os.path.basename(plate_image_path)}"
        })
    except Exception as e:
        return jsonify({"error": f"ANPR failed: {str(e)}"}), 500

@app.route("/static/results/<filename>")
def get_result_image(filename):
    return send_from_directory(RESULTS_FOLDER, filename)

@app.route("/static/plates/<filename>")
def get_plate_image(filename):
    return send_from_directory(PLATE_RESULTS_FOLDER, filename)

@app.route('/debug')
def debug_files():
    static_path = app.static_folder
    files = os.listdir(static_path) if os.path.exists(static_path) else []
    return jsonify({
        'static_folder': static_path,
        'files': files,
        'index_exists': os.path.exists(os.path.join(static_path, 'index.html'))
    })

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=False)