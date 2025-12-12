from fastapi import FastAPI, HTTPException, status, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from models import PredictionResponse
from inference import (
    get_image_from_bytes,
    is_model_ready,
    run_inference,
)
from logger import logger

app = FastAPI()

origins = ["*"]
methods = ["*"]
headers = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=methods,
    allow_headers=headers,
)


@app.get("/", status_code=status.HTTP_200_OK)
def health_check():
    if not is_model_ready():
        raise HTTPException(status_code=503, detail="Model not ready")
    return {"status": "healthy"}


@app.post("/predict", response_model=PredictionResponse)
async def predict(image: UploadFile):
    try:
        # Read image bytes from the uploaded file
        image_bytes = await image.read()
        input_image = get_image_from_bytes(image_bytes)

        predictions = run_inference(input_image)
        logger.info(f"Predictions: {predictions}")
        return predictions

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {e}")
