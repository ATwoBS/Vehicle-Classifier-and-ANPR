import React, { useState } from "react";
import axios from "axios";
import "../styles/styles.css";

const ANPRUpload = () => {
    const [selectedFile, setSelectedFile] = useState(null);
    const [preview, setPreview] = useState(null);
    const [plateNumber, setPlateNumber] = useState("");
    const [resultImage, setResultImage] = useState("");

    const handleFileChange = (event) => {
        const file = event.target.files[0];
        setSelectedFile(file);
        setPreview(URL.createObjectURL(file));
    };

    const handleDrop = (event) => {
        event.preventDefault();
        const file = event.dataTransfer.files[0];
        setSelectedFile(file);
        setPreview(URL.createObjectURL(file));
    };

    const handleUpload = async () => {
        if (!selectedFile) {
            alert("Please select an image first!");
            return;
        }
    
        const formData = new FormData();
        formData.append("file", selectedFile);
    
        try {
            const response = await axios.post("http://127.0.0.1:5000/anpr_upload", formData);
            
            // Fix incorrect response keys
            setPlateNumber(response.data.plate_text);  
            setResultImage(`http://127.0.0.1:5000${response.data.plate_image_url}`);  
    
        } catch (error) {
            console.error("Error uploading file:", error);
        }
    };
    
    const handleClear = () => {
        setSelectedFile(null);
        setPreview(null);
        setPlateNumber("");
        setResultImage("");
    };

    return (
        <div className="container">
            <div
                className="drop-zone"
                onDragOver={(e) => e.preventDefault()}
                onDrop={handleDrop}
            >
                {preview ? (
                    <img src={preview} alt="Preview" className="preview-image" />
                ) : (
                    <p>Drag & Drop Image Here or Click to Upload</p>
                )}
                <input type="file" onChange={handleFileChange} accept="image/*" />
            </div>
            <div className="button-container">
                <button onClick={handleUpload}>Upload</button>
                <button onClick={handleClear} className="clear-button">Clear</button>
            </div>

            {plateNumber && (
                <div className="result">
                    <h3>Plate Number: {plateNumber}</h3>
                    {resultImage && <img src={resultImage} alt="Processed" className="result-image" />}
                </div>
            )}
        </div>
    );
};

export default ANPRUpload;
