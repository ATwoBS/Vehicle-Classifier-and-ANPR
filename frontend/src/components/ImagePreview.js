import React from "react";

function ImagePreview({ file }) {
  const previewUrl = URL.createObjectURL(file);

  return (
    <div className="image-preview">
      <img src={previewUrl} alt="Preview" />
    </div>
  );
}

export default ImagePreview;
