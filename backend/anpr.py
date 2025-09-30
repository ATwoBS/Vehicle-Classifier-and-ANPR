from ultralytics import YOLO
import torch
import cv2
import numpy as np
import os
import easyocr

class ANPR:
    def __init__(self, model_path):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = YOLO(model_path).to(self.device)
        self.ocr = easyocr.Reader(["en"])  # OCR for English text

    def detect_plate(self, image_path):
        results = self.model(image_path)
        image = cv2.imread(image_path)

        if not results[0].boxes:
            print("[DEBUG] No plate detected!")
            return "No plate detected", image_path

        # Get the first detected plate bounding box
        x1, y1, x2, y2 = map(int, results[0].boxes.xyxy[0])
        plate_image = image[y1:y2, x1:x2]

        # Ensure directory exists
        plates_dir = "static/plates"
        os.makedirs(plates_dir, exist_ok=True)

        # Save the extracted plate
        plate_path = os.path.join(plates_dir, os.path.basename(image_path))
        cv2.imwrite(plate_path, plate_image)

        # Perform OCR on the cropped plate image
        plate_texts = self.ocr.readtext(plate_image, detail=0)

        print("[DEBUG] Extracted Plate Text:", plate_texts)  # Debugging

        # Filter out unwanted text like "IND" and pick the last element
        plate_texts = [text for text in plate_texts if text.upper() != "IND"]
        plate_text = plate_texts[-1] if plate_texts else "Unreadable"

        return plate_text, plate_path
