from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

load_dotenv()
import gdown
import tensorflow as tf
import numpy as np
from PIL import Image
import io
from services.openai_service import get_openai_service

# ----------------------------------------------------------------------------
# CONFIGURATION
# ----------------------------------------------------------------------------

MODEL_DIR = "models"
MODEL_FILENAME = "best_harmful_detector.keras"
MODEL_PATH = os.path.join(MODEL_DIR, MODEL_FILENAME)

# Google Drive file ID
# Google Drive file ID
GDRIVE_FILE_ID = os.getenv("GDRIVE_FILE_ID")
GDRIVE_URL = f"https://drive.google.com/uc?id={GDRIVE_FILE_ID}"

IMG_SIZE = (128, 128)  # Must match training size
THRESHOLD = 0.5

app = FastAPI(
    title="Harmful Image Detection API",
    description="CNN-based harmful/violent image classifier with optional Gemini captioning",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

model = None

# ----------------------------------------------------------------------------
# STARTUP: DOWNLOAD + LOAD MODEL
# ----------------------------------------------------------------------------

@app.on_event("startup")
def startup_load_model():
    global model

    os.makedirs(MODEL_DIR, exist_ok=True)

    if not os.path.exists(MODEL_PATH):
        print(f"⚡ Model not found at {MODEL_PATH}. Downloading from Google Drive...")

        try:
            gdown.download(
                url=GDRIVE_URL,
                output=MODEL_PATH,
                quiet=False,
                fuzzy=True
            )
            print("✅ Model downloaded successfully!")

        except Exception as e:
            raise RuntimeError(f"❌ Failed to download model: {e}")

    else:
        print(f"✅ Model already exists at {MODEL_PATH}")

    try:
        print("⚡ Loading model into memory...")
        model = tf.keras.models.load_model(MODEL_PATH)
        print("✅ Model loaded and ready!")
    except Exception as e:
        raise RuntimeError(f"❌ Failed to load model: {e}")


# ----------------------------------------------------------------------------
# HELPER: IMAGE PREPROCESSING
# ----------------------------------------------------------------------------

def preprocess_image(image_bytes: bytes):
    try:
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        img = img.resize(IMG_SIZE)
        img_arr = np.array(img, dtype=np.float32) / 255.0
        img_arr = np.expand_dims(img_arr, axis=0)
        return img_arr
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid image file")


# ----------------------------------------------------------------------------
# ROUTES
# ----------------------------------------------------------------------------

@app.get("/")
def root():
    return {"message": "Harmful Image Detection API is running!"}


@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    """
    Classify image as harmful or non-harmful using CNN.
    
    This endpoint only returns the CNN classification result.
    """
    if model is None:
        raise HTTPException(status_code=500, detail="Model not loaded")

    # Validate file type
    if file.content_type not in ["image/jpeg", "image/png", "image/jpg"]:
        raise HTTPException(status_code=415, detail="Unsupported file type")

    image_bytes = await file.read()
    img_arr = preprocess_image(image_bytes)

    # Model prediction
    pred = model.predict(img_arr)
    prob = float(pred[0][0])

    label = "HARMFUL" if prob >= THRESHOLD else "NON_HARMFUL"

    return {
        "label": label,
        "confidence": round(prob, 4),
        "threshold": THRESHOLD
    }


@app.post("/predict-with-caption")
async def predict_with_caption(file: UploadFile = File(...)):
    """
    Classify image as harmful or non-harmful using CNN.
    If non-harmful, generate a caption using OpenAI API.
    
    Returns:
    Returns:
        - For all images: CNN classification + Gemini caption (title & description)
    """
    if model is None:
        raise HTTPException(status_code=500, detail="Model not loaded")

    # Validate file type
    if file.content_type not in ["image/jpeg", "image/png", "image/jpg"]:
        raise HTTPException(status_code=415, detail="Unsupported file type")

    image_bytes = await file.read()
    img_arr = preprocess_image(image_bytes)

    # Step 1: CNN Classification
    pred = model.predict(img_arr)
    prob = float(pred[0][0])
    label = "HARMFUL" if prob >= THRESHOLD else "NON_HARMFUL"

    response = {
        "label": label,
        "confidence": round(prob, 4),
        "threshold": THRESHOLD
    }

    # Step 2: If non-harmful, generate caption with Gemini
    # Step 2: Generate caption with OpenAI for all images
    try:
        openai_service = get_openai_service()
        caption = openai_service.generate_caption(image_bytes)
        response["caption"] = caption
    except ValueError as e:
        # OPENAI_API_KEY not set
        raise HTTPException(
            status_code=500, 
            detail=f"OpenAI API not configured: {str(e)}"
        )
    except Exception as e:
        # OpenAI API error - return CNN result with error message
        response["caption_error"] = f"Failed to generate caption: {str(e)}"

    return response


# ----------------------------------------------------------------------------
# RUN SERVER
# ----------------------------------------------------------------------------
# uvicorn main:app --reload
