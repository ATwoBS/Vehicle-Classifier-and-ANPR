#! /bin/bash

# Start the backend first
cd backend
export FLASK_APP=app.py
flask run --host=0.0.0.0 --port=5000 &

# Then start React
cd ../frontend
npm install
npm run build
serve -s build -l 3000