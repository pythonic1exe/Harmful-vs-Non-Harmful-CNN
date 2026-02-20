# Backend — Harmful Content Detector API

A **FastAPI** backend that classifies images as harmful or non-harmful using a custom-trained CNN model, then generates an AI caption via **OpenAI GPT-4o** (or optionally Google Gemini).

---

## Directory Structure

```
backend/
├── main.py                        # FastAPI app, startup logic, routes
├── requirements.txt               # Python dependencies
├── BACKEND.md                     # This file
├── models/
│   └── best_harmful_detector.keras  # Keras CNN model (auto-downloaded if missing)
└── services/
    ├── __init__.py
    ├── openai_service.py          # GPT-4o image captioning (active)
    └── gemini_service.py          # Google Gemini captioning (alternative)
```

---

## Tech Stack

| Component     | Technology                          |
|---------------|-------------------------------------|
| Web framework | FastAPI + Uvicorn                   |
| ML inference  | TensorFlow 2.16 / Keras             |
| Image handling| Pillow, NumPy                       |
| Captioning    | OpenAI GPT-4o (`gpt-4o`)           |
| Alt captioning| Google Gemini (`gemini-2.0-flash-exp`) |
| Model download| gdown (Google Drive)                |
| Config        | python-dotenv                       |

---

## Prerequisites

- Python 3.10+
- `OPENAI_API_KEY` — required for caption generation
- `GDRIVE_FILE_ID` — Google Drive file ID of the `.keras` model
- `GEMINI_API_KEY` — optional, only needed if switching to Gemini

---

## Setup

```bash
# 1. Create and activate virtual environment
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create .env file
cat > .env <<EOF
OPENAI_API_KEY=sk-...
GDRIVE_FILE_ID=your_google_drive_file_id
GEMINI_API_KEY=your_gemini_api_key   # optional
EOF

# 4. Start the server
uvicorn main:app --reload
```

Server runs at `http://127.0.0.1:8000`.

> On first startup, if `models/best_harmful_detector.keras` is not present, it is automatically downloaded from Google Drive using `gdown`.

---

## Environment Variables

| Variable         | Required | Description                                        |
|------------------|----------|----------------------------------------------------|
| `OPENAI_API_KEY` | Yes      | OpenAI API key for GPT-4o captioning               |
| `GDRIVE_FILE_ID` | Yes      | Google Drive file ID for CNN model auto-download   |
| `GEMINI_API_KEY` | No       | Gemini API key (only needed if using GeminiService)|

---

## API Reference

### `GET /`
Health check endpoint.

**Response:**
```json
{ "message": "Harmful Image Detection API is running!" }
```

---

### `POST /predict`
Classifies an image using the CNN only. No caption is generated.

**Request:** `multipart/form-data`
| Field | Type | Description              |
|-------|------|--------------------------|
| `file`| File | JPEG or PNG image to classify |

**Response:**
```json
{
  "label": "HARMFUL",
  "confidence": 0.9231,
  "threshold": 0.5
}
```

| Field        | Type   | Description                                      |
|--------------|--------|--------------------------------------------------|
| `label`      | string | `"HARMFUL"` or `"NON_HARMFUL"`                   |
| `confidence` | float  | Raw sigmoid output — probability of being harmful |
| `threshold`  | float  | Decision boundary (default `0.5`)                |

---

### `POST /predict-with-caption`
Classifies an image **and** generates an AI-powered caption using GPT-4o.

**Request:** `multipart/form-data`
| Field | Type | Description              |
|-------|------|--------------------------|
| `file`| File | JPEG or PNG image to classify |

**Success response:**
```json
{
  "label": "NON_HARMFUL",
  "confidence": 0.1042,
  "threshold": 0.5,
  "caption": {
    "title": "Golden Retriever on a Sunny Beach",
    "description": "A happy golden retriever runs along a sandy beach with ocean waves in the background."
  }
}
```

**Partial response (captioning failed):**
```json
{
  "label": "NON_HARMFUL",
  "confidence": 0.1042,
  "threshold": 0.5,
  "caption_error": "Failed to generate caption: ..."
}
```

---

## CNN Model Details

| Property        | Value                              |
|-----------------|------------------------------------|
| Format          | Keras `.keras`                     |
| Input size      | 128 × 128 × 3 (RGB)               |
| Output          | Single sigmoid neuron              |
| Output meaning  | Probability of being harmful       |
| Decision threshold | 0.5 (configurable via `THRESHOLD` in `main.py`) |
| Storage         | Google Drive — auto-downloaded on startup |
| Local path      | `models/best_harmful_detector.keras` |

**Image preprocessing pipeline:**
1. Open image with Pillow, convert to RGB
2. Resize to 128 × 128
3. Normalize pixel values to `[0, 1]`
4. Expand dims to shape `(1, 128, 128, 3)` for batch inference

---

## Services

### `OpenAIService` (`services/openai_service.py`)
- Model: `gpt-4o`
- Sends base64-encoded image + prompt to OpenAI Chat Completions API
- Returns a `dict` with `title` (≤ 8 words) and `description` (1–2 sentences)
- Raises `ValueError` if `OPENAI_API_KEY` is not set

### `GeminiService` (`services/gemini_service.py`)
- Model: `gemini-2.0-flash-exp`
- Uses `google-genai` SDK with inline image bytes
- Same output format as `OpenAIService` (`title` + `description`)
- Raises `ValueError` if `GEMINI_API_KEY` is not set
- **Not active by default** — swap it in `main.py` to use instead of OpenAI

#### Switching to Gemini
In `main.py`, replace:
```python
from services.openai_service import get_openai_service
...
openai_service = get_openai_service()
caption = openai_service.generate_caption(image_bytes)
```
with:
```python
from services.gemini_service import GeminiService
...
gemini_service = GeminiService()
caption = gemini_service.generate_caption(image_bytes)
```

---

## CORS Configuration

Allowed origins (configured in `main.py`):
- `http://localhost:5173`
- `http://127.0.0.1:5173`
- `http://localhost:5174`

Update `allow_origins` in `main.py` if the frontend is served on a different port.

---

## Accepted File Types

| MIME type     | Extension |
|---------------|-----------|
| `image/jpeg`  | `.jpg`    |
| `image/jpg`   | `.jpg`    |
| `image/png`   | `.png`    |

Other types return HTTP `415 Unsupported Media Type`.

---

## Dependencies (`requirements.txt`)

| Package              | Version   | Purpose                        |
|----------------------|-----------|--------------------------------|
| `fastapi`            | 0.111.1   | Web framework                  |
| `uvicorn[standard]`  | 0.22.0    | ASGI server                    |
| `tensorflow`         | 2.16.2    | CNN model inference            |
| `numpy`              | 1.26.4    | Array operations               |
| `Pillow`             | 10.1.0    | Image loading and resizing     |
| `gdown`              | 4.7.1     | Google Drive model download    |
| `python-multipart`   | 0.0.8     | Multipart file upload parsing  |
| `google-genai`       | 0.2.2     | Gemini API SDK                 |
| `openai`             | latest    | OpenAI API SDK                 |
