import React, { useState } from "react";
import "../App.css";

interface ImageUploadProps {
    onUpload: (file: File) => void;
    isLoading: boolean;
}

export const ImageUpload: React.FC<ImageUploadProps> = ({ onUpload, isLoading }) => {
    const [preview, setPreview] = useState<string | null>(null);
    const [dragActive, setDragActive] = useState(false);

    const handleFile = (file: File) => {
        if (!file.type.startsWith("image/")) {
            alert("Please upload an image file");
            return;
        }
        const objectUrl = URL.createObjectURL(file);
        setPreview(objectUrl);
        onUpload(file);
    };

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            handleFile(e.target.files[0]);
        }
    };

    const handleDrag = (e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        if (e.type === "dragenter" || e.type === "dragover") {
            setDragActive(true);
        } else if (e.type === "dragleave") {
            setDragActive(false);
        }
    };

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        setDragActive(false);
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            handleFile(e.dataTransfer.files[0]);
        }
    };

    return (
        <div className="upload-container">
            <div
                className={`drop-zone ${dragActive ? "active" : ""} ${isLoading ? "disabled" : ""}`}
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
            >
                <input
                    type="file"
                    id="file-upload"
                    accept="image/*"
                    onChange={handleChange}
                    disabled={isLoading}
                    className="file-input"
                />
                <label htmlFor="file-upload" className="upload-label">
                    {preview ? (
                        <div className="preview-container">
                            <img src={preview} alt="Preview" className="image-preview" />
                            <div className="overlay">
                                <span>Change Image</span>
                            </div>
                        </div>
                    ) : (
                        <div className="placeholder">
                            <span className="icon">📁</span>
                            <p>Drag & Drop or Click to Upload</p>
                        </div>
                    )}
                </label>
            </div>
            {isLoading && <p className="processing-text">Processing image...</p>}
        </div>
    );
};
