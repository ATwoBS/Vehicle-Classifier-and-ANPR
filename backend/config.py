import os

UPLOAD_FOLDER = "static/uploads"
RESULTS_FOLDER = "static/results"
PLATE_RESULTS_FOLDER = "static/plates"
MODEL_PATH = "models/best.pt"
ANPR_MODEL_PATH = "models/best_anpr.pt"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)
os.makedirs(PLATE_RESULTS_FOLDER, exist_ok=True)
