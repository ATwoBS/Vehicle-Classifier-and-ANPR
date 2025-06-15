from pathlib import Path
import os

# Auto-detect project structure - handle both local and Docker environments
current_file = Path(__file__).resolve()

# Check if we're in Docker container structure
if current_file.name == 'config.py' and current_file.parent.name == 'app':
    # Docker: config.py is at /app/config.py
    project_root = current_file.parent
    backend_dir = project_root / "backend"  # Add this line
else:
    # Local: config.py is at backend/config.py
    backend_dir = current_file.parent
    project_root = backend_dir.parent

# Define paths relative to project root
UPLOAD_FOLDER = str(project_root / "static" / "uploads")
RESULTS_FOLDER = str(project_root / "static" / "results") 
PLATE_RESULTS_FOLDER = str(project_root / "static" / "plates")
MODEL_PATH = str(project_root / "models" / "best.pt")
ANPR_MODEL_PATH = str(project_root / "models" / "best_anpr.pt")

# Create directories if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)
os.makedirs(PLATE_RESULTS_FOLDER, exist_ok=True)