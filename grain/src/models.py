from fastapi import UploadFile
from pydantic import BaseModel


class Coin(BaseModel):
    center_x: int
    center_y: int
    radius_px: int


class PredictionRequest(BaseModel):
    mm_per_pixel: float
    coin_center_x: int | None
    coin_center_y: int | None
    coin_radius_px: int | None
    image: UploadFile


class PredictionResponse(BaseModel):
    size_mm: float
    distribution_mm: dict[str, float]
