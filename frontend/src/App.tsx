import { useState } from "react";
import { uploadImage } from "./api";
import { ImageUpload } from "./components/ImageUpload";
import { ResultDisplay } from "./components/ResultDisplay";
import type { PredictionResponse } from "./types";
import "./App.css";

function App() {
  const [result, setResult] = useState<PredictionResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleUpload = async (file: File) => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await uploadImage(file);
      // Create a local preview URL
      const previewUrl = URL.createObjectURL(file);
      setResult({ ...data, imagePreview: previewUrl });
    } catch (err: any) {
      console.error(err);
      setError("Failed to process image. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    setResult(null);
    setError(null);
  };

  return (
    <div className="app-container">
      <h1 className="title">Harmful Content Detector</h1>
      <p className="subtitle">Upload an image to analyze its content</p>

      {error && <div className="error-message">{error}</div>}

      {!result ? (
        <ImageUpload onUpload={handleUpload} isLoading={isLoading} />
      ) : (
        <ResultDisplay result={result} onReset={handleReset} imagePreview={result.imagePreview} />
      )}
    </div>
  );
}

export default App;
