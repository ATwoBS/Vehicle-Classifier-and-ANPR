import React, { useState } from "react";
import FileUpload from "../components/FileUpload";
import ImagePreview from "../components/ImagePreview";

const Home = () => {
    const [preview, setPreview] = useState(null);

    return (
        <div className="container">
            <h1>Drag and Drop the image to see its class</h1>
            <FileUpload setPreview={setPreview} />
            {preview && <ImagePreview image={preview} />}
        </div>
    );
};

export default Home;
