# Harmful Content Detector

An AI-powered web application that classifies uploaded images as **harmful** or **non-harmful** using a custom-trained CNN model, and generates a natural-language caption for every image using OpenAI GPT-4o.

---

## How It Works

```
User uploads image
       │
       ▼
  FastAPI Backend
       │
       ▼
CNN Model (TensorFlow/Keras)
  ├── HARMFUL   → confidence score shown, caption still generated
  └── NON-HARMFUL → confidence score shown, caption generated
       │
       ▼
OpenAI GPT-4o (image captioning)
  └── Returns: title + description
       │
       ▼
React Frontend displays result
```

1. The user uploads a JPEG or PNG image via the browser.
2. The backend runs the image through a pre-trained Keras CNN model (`best_harmful_detector.keras`) to classify it as `HARMFUL` or `NON_HARMFUL` with a confidence score.
3. Regardless of the classification, OpenAI GPT-4o generates a short title and description for the image.
4. The frontend displays the classification badge, confidence percentage, image preview, and the AI-generated caption.

---

## Project Structure

```
AIPROJECT2-master/
├── backend/
│   ├── main.py                    # FastAPI app, routes, model loading
│   ├── requirements.txt           # Python dependencies
│   ├── models/
│   │   └── best_harmful_detector.keras   # CNN model (auto-downloaded if missing)
│   └── services/
│       ├── openai_service.py      # GPT-4o image captioning service
│       └── gemini_service.py      # Gemini image captioning service (alternative)
└── frontend/
    ├── index.html
    ├── vite.config.ts
    ├── package.json
    └── src/
        ├── main.tsx               # React entry point
        ├── App.tsx                # Root component, state management
        ├── api.ts                 # Axios API client
        ├── types.ts               # TypeScript interfaces
        └── components/
            ├── ImageUpload.tsx    # Drag-and-drop / click-to-upload component
            └── ResultDisplay.tsx  # Classification result + caption display
```

---

## Tech Stack

| Layer     | Technology                               |
|-----------|------------------------------------------|
| Frontend  | React 19, TypeScript, Vite, Axios        |
| Backend   | FastAPI, Uvicorn                         |
| ML Model  | TensorFlow / Keras (CNN, 128×128 input)  |
| Captioning| OpenAI GPT-4o (primary), Google Gemini (alternative) |
| Model Storage | Google Drive (auto-downloaded via gdown) |

---

## Prerequisites

- Python 3.10+
- Node.js 18+
- An **OpenAI API key** (required for captions)
- A **Google Drive file ID** for the model (set via environment variable)
- *(Optional)* A **Gemini API key** if you want to switch to the Gemini captioning service

---

## Setup & Running

### 1. Backend

```bash
cd backend

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create a .env file with your API keys
cat > .env <<EOF
OPENAI_API_KEY=sk-...
GDRIVE_FILE_ID=your_google_drive_file_id
GEMINI_API_KEY=your_gemini_api_key   # optional
EOF

# Start the server
uvicorn main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

> **Note:** On first startup, the CNN model is automatically downloaded from Google Drive if it is not already present in `backend/models/`.

### 2. Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start the dev server
npm run dev
```

The app will be available at `http://localhost:5173`.

---

## API Reference

### `GET /`
Health check.

**Response:**
```json
{ "message": "Harmful Image Detection API is running!" }
```

---

### `POST /predict`
Classify an image without generating a caption.

**Request:** `multipart/form-data` with a `file` field (JPEG or PNG).

**Response:**
```json
{
  "label": "HARMFUL" | "NON_HARMFUL",
  "confidence": 0.9231,
  "threshold": 0.5
}
```

---

### `POST /predict-with-caption`
Classify an image **and** generate an AI caption.

**Request:** `multipart/form-data` with a `file` field (JPEG or PNG).

**Response:**
```json
{
  "label": "HARMFUL" | "NON_HARMFUL",
  "confidence": 0.1042,
  "threshold": 0.5,
  "caption": {
    "title": "Golden Retriever on a Sunny Beach",
    "description": "A happy golden retriever runs along a sandy beach with ocean waves in the background."
  }
}
```

If captioning fails, a `caption_error` string is returned instead of `caption`.

---

## Environment Variables

| Variable          | Required | Description                                          |
|-------------------|----------|------------------------------------------------------|
| `OPENAI_API_KEY`  | Yes      | OpenAI API key for GPT-4o image captioning           |
| `GDRIVE_FILE_ID`  | Yes      | Google Drive file ID for the CNN model download      |
| `GEMINI_API_KEY`  | No       | Google Gemini API key (alternative captioning service)|

---

## Model Details

- **Architecture:** Convolutional Neural Network (CNN)
- **Input size:** 128 × 128 × 3 (RGB)
- **Output:** Single sigmoid neuron — probability of being harmful
- **Threshold:** 0.5 (configurable via `THRESHOLD` in `main.py`)
- **Format:** Keras `.keras` file
- **Storage:** Google Drive, auto-downloaded on startup via `gdown`

---

## Frontend Features

- **Drag-and-drop** or click-to-upload image input
- **Image preview** before and after submission
- **Live loading state** during analysis
- **Color-coded result card** — red for harmful, green for safe
- **AI caption** (title + description) displayed for every image
- **Reset button** to analyze another image

---

## Development Notes

- The frontend proxies API calls to `http://127.0.0.1:8000`. If you change the backend port, update `API_URL` in [frontend/src/api.ts](frontend/src/api.ts).
- CORS is pre-configured for `localhost:5173` and `localhost:5174`.
- Accepted image formats: `image/jpeg`, `image/png`, `image/jpg`.
- The `GeminiService` in [backend/services/gemini_service.py](backend/services/gemini_service.py) is an alternative captioning backend. To switch, replace the `OpenAIService` calls in `main.py` with `GeminiService`.
