from typing import Annotated
from inference import run_inference
from fastapi import FastAPI, Form, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from models import Coin, PredictionRequest, PredictionResponse
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
    return {"status": "healthy"}


@app.post("/predict", response_model=PredictionResponse)
async def predict(request: Annotated[PredictionRequest, Form()]):
    try:
        image = request.image
        image_bytes = await image.read()

        if (
            request.coin_center_x is None
            or request.coin_center_y is None
            or request.coin_radius_px is None
        ):
            coin = None
        else:
            coin = Coin(
                center_x=request.coin_center_x,
                center_y=request.coin_center_y,
                radius_px=request.coin_radius_px,
            )

        mm_per_pixel = request.mm_per_pixel

        predictions = run_inference(image_bytes, coin, mm_per_pixel)
        logger.info(f"Predictions: {predictions}")
        return predictions

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {e}")
