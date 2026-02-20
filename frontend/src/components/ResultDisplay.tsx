import React from "react";
import type { PredictionResponse } from "../types";
import "../App.css";

interface ResultDisplayProps {
    result: PredictionResponse;
    onReset: () => void;
    imagePreview?: string;
}

export const ResultDisplay: React.FC<ResultDisplayProps> = ({ result, onReset, imagePreview }) => {
    const isHarmful = result.label === "HARMFUL";

    return (
        <div className={`result-container ${isHarmful ? "harmful" : "safe"}`}>
            {imagePreview && (
                <div className="result-image-container">
                    <img src={imagePreview} alt="Analyzed" className="result-image" />
                </div>
            )}
            <div className="status-badge">
                {isHarmful ? "⚠️ HARMFUL CONTENT DETECTED" : "✅ SAFE CONTENT"}
            </div>

            <div className="confidence">
                Confidence: {(result.confidence * 100).toFixed(2)}%
            </div>

            {result.caption && (
                <div className="caption-box">
                    <h2>{result.caption.title}</h2>
                    <p>{result.caption.description}</p>
                </div>
            )}

            {result.caption_error && (
                <div className="error-box">
                    <p>⚠️ Caption could not be generated: {result.caption_error}</p>
                </div>
            )}

            <button onClick={onReset} className="reset-button">
                Analyze Another Image
            </button>
        </div>
    );
};
