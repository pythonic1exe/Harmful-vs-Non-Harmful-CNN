import axios from "axios";
import type { PredictionResponse } from "./types";

const API_URL = "http://127.0.0.1:8000";

export const uploadImage = async (file: File): Promise<PredictionResponse> => {
    const formData = new FormData();
    formData.append("file", file);

    try {
        const response = await axios.post<PredictionResponse>(
            `${API_URL}/predict-with-caption`,
            formData,
            {
                headers: {
                    "Content-Type": "multipart/form-data",
                },
            }
        );
        return response.data;
    } catch (error) {
        console.error("Error uploading image:", error);
        throw error;
    }
};
