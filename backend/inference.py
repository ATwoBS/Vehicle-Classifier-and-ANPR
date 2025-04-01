from ultralytics import YOLO
import torch
import cv2
import numpy as np
import os

class VehicleClassifier:
    def __init__(self, model_path="models/best.pt"):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = YOLO(model_path).to(self.device)

    def predict(self, image_path):
        results = self.model(image_path)

        # Load image for drawing bounding boxes
        image = cv2.imread(image_path)

        if not results[0].boxes:
            return "Unknown", image_path  # If no vehicle is detected, return Unknown

        # Extract class index and bounding box
        labels = results[0].names  # Class names dictionary
        class_indices = results[0].boxes.cls.cpu().numpy().astype(int)  # Get class indices
        pred_class = labels[class_indices[0]]  # Get first detected class

        # Draw bounding boxes
        for box, cls in zip(results[0].boxes.xyxy, class_indices):
            x1, y1, x2, y2 = map(int, box)
            cv2.rectangle(image, (x1, y1), (x2, y2), (0, 0, 255), 3)  # Red bounding box
            #cv2.putText(image, labels[cls], (x1, y1 - 10),
            #cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)  # Red text

        # Save result with bounding box
        results_folder = "static/results"
        os.makedirs(results_folder, exist_ok=True)
        result_path = os.path.join(results_folder, os.path.basename(image_path))
        cv2.imwrite(result_path, image)

        return pred_class, result_path  # Return class and result image path
