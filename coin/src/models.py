from pydantic import BaseModel


# Pydantic models for request/response
class PredictionRequest(BaseModel):
    image: bytes


class PredictionResponse(BaseModel):
    mm_per_pixel: float
    coin_label: str
    coin_center_x: int
    coin_center_y: int
    coin_radius_px: int
