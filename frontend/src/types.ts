export interface PredictionResponse {
    label: "HARMFUL" | "NON_HARMFUL";
    confidence: number;
    threshold: number;
    caption?: {
        title: string;
        description: string;
    };
    caption_error?: string;
    imagePreview?: string;
}
