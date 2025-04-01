import React from "react";
import FileUpload from "./components/FileUpload";
import ANPRUpload from "./components/ANPRUpload";
import "./styles/styles.css";

function App() {
    return (
        <div className="app-container">
            <div className="upload-section">
                <h2>Vehicle Classification</h2>
                <FileUpload />
            </div>
            <div className="upload-section">
                <h2>ANPR (Number Plate Recognition)</h2>
                <ANPRUpload />
            </div>
        </div>
    );
}

export default App;
