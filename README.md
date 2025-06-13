# Vehicle-Classifier-and-ANPR
## How to run: 
1. Clone the repository.
2. Create a python environment and activate with using following command
```bash
python -m venv 'env_name' #(windows)
source\Scripts\activate
```
3. Install the project dependencies using the following command for backend 
```bash
pip install -r requirements.txt
```
4. Navigate and Run the backend 
```bash
python app.py
```
5. Navigate and Install dependencies for frontend by following command
```bash
npm install
```
6. Navigate and Run the Frontend
```bash
npm start
```
## Introduction to the project
### Overview
With the rapid growth of vehicular traffic, automated vehicle classification and number plate recognition (ANPR) have become essential in various sectors, including toll booths and smart city applications. This project integrates Vehicle Classification using YOLOv8 (You Only Look Once) and Automatic Number Plate Recognition (ANPR) using EasyOCR, providing an efficient, real-time system for identifying vehicle types and extracting license plate numbers from images.
### Problem statement
Manual vehicle classification and number plate recognition are time-consuming and prone to errors. Traditional methods require human intervention, leading to inefficiencies in toll collection, parking systems, and security checkpoints. The objective of this project is to develop an automated and robust deep learning-based system to: 

1. Vehicle Class Identification: The machine learning model(CNN) classifies vehicles into categories based on the classes defined by FASTag. These classifications are then utilized for accurate toll fee calculation.
2. Automatic Number Plate Recognition: This system automatically extracts vehicle registration plate details from images for seamless identification and processing.

By leveraging YOLOv8 for object detection and EasyOCR for optical character recognition (OCR), the system can effectively automate these processes with high accuracy.

### Objectives
* Develop an AI-powered vehicle classification system to detect and categorize vehicles based on their type required for the Fastag system  (e.g Class4, Class5, Class6, etc.).
* Implement an ANPR system to detect and extract number plates from images and recognize the alphanumeric text
* Create an interactive web-based interface where users can upload images, and the system will return classified vehicle types and extracted license plate numbers.
* Ensure real-time processing and scalability using deep learning models optimized for deployment.

### Tech stack
This project utilizes a combination of deep learning, computer vision, and web technologies for implementation.
* Backend:
1. YOLOv8 (You Only Look Once): A state-of-the-art object detection model used for vehicle classification and number plate detection.
2. EasyOCR: Optical Character Recognition (OCR) model used for extracting text from number plates.
3. Flask: A lightweight Python web framework used to create APIs for processing images and returning predictions.
* Frontend:
1. React.js: A JavaScript framework used for building a user-friendly interface.
2. Axios: A library for making API requests to send images to the backend and receive results.
* Additional Tools & Libraries:
1. OpenCV (cv2): Used for image processing and bounding box visualization.
2. Torch: PyTorch framework for running deep learning models.
3. NumPy & OS libraries: For handling image processing and file management

### System workflow
* The system follows these steps to process images:
1. User Uploads an Image: The frontend provides two upload sections:
2. One for vehicle classification.
3. One for ANPR (Number Plate Recognition).
4. Flask Backend Processes the Image:
5. Vehicle Classification Module: YOLOv8 detects the vehicle and classifies it.
6. ANPR Module: YOLOv8 detects the number plate, crops it, and EasyOCR extracts the text.
7. Result is Displayed to the User:
8. The classified vehicle type and processed image with bounding boxes are displayed.
9. The extracted number plate text and cropped plate image are shown.

### Real-World Applications
* Toll Booth Automation: Automatically classifies vehicle types for accurate toll pricing.
* Parking Systems: Identifies vehicle categories and records number plates for automated ticketing.
* Traffic Law Enforcement: Detects and logs number plates of overspeeding or unauthorized vehicles.
* Smart City Applications: Helps in tracking vehicles for security and analytics.

### Summary
This project presents a fully automated, AI-powered vehicle classification and ANPR system that eliminates the need for manual identification. The combination of YOLO for detection and EasyOCR for text extraction ensures high accuracy and real-time performance. The integration with a web-based frontend makes it user-friendly, scalable, and suitable for practical deployment.
