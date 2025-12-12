from fastapi import HTTPException
from models import PredictionResponse
from ultralytics import YOLO
import cv2
import numpy as np
from logger import logger

# Model initialization and readiness state
model_yolo: YOLO = None
_model_ready = False

MODEL_PATH = "/app/src/best.pt"


def _initialize_model():
    """Initialize the YOLO model."""
    global model_yolo, _model_ready

    try:
        model_yolo = YOLO(MODEL_PATH)
        _model_ready = True

    except Exception as e:
        logger.error(f"Error initializing YOLO model: {e}")
        _model_ready = False
        model_yolo = None


# Initialize model on module import
_initialize_model()


def is_model_ready() -> bool:
    """Check if the model is ready for inference."""
    return _model_ready and model_yolo is not None


def get_image_from_bytes(image_bytes: bytes):
    """Convert image from bytes to cv2 image"""
    image_array = np.frombuffer(image_bytes, dtype=np.uint8)
    image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

    return image


COIN_DIAMETER_MM = 24.26


def segment(image):
    results = model_yolo(image, retina_masks=True)
    result = results[0]

    if result.masks is None or len(result.masks.xy) == 0:
        logger.warning("No coins segmented by YOLO.")
        raise HTTPException(status_code=400, detail="No coins segmented by YOLO.")

    segment = result.masks.xy[0]
    points = np.array(segment, dtype=np.int32)

    classidx = int(result.boxes.cls.item())

    return points, classidx


def run_inference(input_image):
    """Run inference on an image using YOLO11n model."""
    global model_yolo

    # Check if model is ready
    if not is_model_ready():
        logger.error("Model not ready for inference")
        raise HTTPException(status_code=503, detail="Model not ready for inference")

    try:
        logger.info("[*] Running YOLO Model for Coin Detection...")

        # Make predictions and get raw results
        points, classidx = segment(input_image)

        label = {0: "₹1", 1: "₹2", 2: "₹5", 3: "₹10"}
        classname = label[classidx]

        ellipse = cv2.fitEllipse(points)

        (center, (width, height), angle) = ellipse

        diameter = (width + height) / 2.0

        return PredictionResponse(
            mm_per_pixel=float(COIN_DIAMETER_MM / diameter),
            coin_label=classname,
            coin_center_x=int(center[0]),
            coin_center_y=int(center[1]),
            coin_radius_px=int(diameter / 2),
        )

        # Add a little padding to the box so we don't cut off the edges of the circle
        # x, y, w, h = cv2.boundingRect(points)

        # padding = 20
        # img_h, img_w = input_image.shape[:2]
        # x1 = max(0, x - padding)
        # y1 = max(0, y - padding)
        # x2 = min(img_w, x + w + padding)
        # y2 = min(img_h, y + h + padding)

        # if (x1, y1, x2, y2) == (0, 0, w, h):
        #     logger.warning("No coin detected in the image.")
        #     raise HTTPException(
        #         status_code=400, detail="No coin detected in the image."
        #     )

        # logger.info(f"{classname} detected at [{x1}, {y1}, {x2}, {y2}] by YOLO")

        # # 3. CROP (Region of Interest)
        # roi = input_image[y1:y2, x1:x2].copy()

        # # Adjust polygon points to be relative to the ROI's top-left corner
        # rel_points = points - [x1, y1]

        # # Create a mask for the ROI using an enclosing ellipse
        # roi_mask = np.zeros(roi.shape[:2], dtype=np.uint8)

        # if len(rel_points) >= 5:
        #     # Fit an ellipse to the contour points
        #     ellipse = cv2.fitEllipse(rel_points)
        #     # Draw the ellipse on the mask
        #     cv2.ellipse(roi_mask, ellipse, 255, -1)  # -1 means filled ellipse
        #     mask_type = "ellipse"
        # else:
        #     # Fallback to polygon if not enough points for ellipse
        #     cv2.fillPoly(roi_mask, [rel_points], 255)
        #     mask_type = "polygon"

        # # 4. CV2 FINE MEASUREMENT (Hough Circle)
        # gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        # gray_roi = cv2.bitwise_and(gray_roi, gray_roi, mask=roi_mask)
        # gray_roi = cv2.medianBlur(gray_roi, 5)  # Blur to remove noise

        # logger.info(f"Using {mask_type} mask for Hough Circle detection.")

        # # Detect circles inside the YOLO box
        # circles = cv2.HoughCircles(
        #     gray_roi,
        #     cv2.HOUGH_GRADIENT,
        #     dp=1,
        #     minDist=50,
        #     param1=50,
        #     param2=30,
        #     minRadius=10,
        #     maxRadius=0,
        # )

        # if circles is not None:
        #     circles = np.uint16(np.around(circles))
        #     c_x_rel, c_y_rel, c_r = circles[0][0]  # Take the strongest circle found

        #     # Translate circle coordinates back to the original image's frame
        #     c_x_abs = x1 + c_x_rel
        #     c_y_abs = y1 + c_y_rel

        #     diameter_px = c_r * 2
        #     mm_per_pixel = COIN_DIAMETER_MM / diameter_px

        #     return PredictionResponse(
        #         mm_per_pixel=float(mm_per_pixel),
        #         coin_label=classname,
        #         coin_center_x=int(c_x_abs),
        #         coin_center_y=int(c_y_abs),
        #         coin_radius_px=int(c_r),
        #     )
        # else:
        #     logger.warning("Hough Circle detection failed.")
        #     raise HTTPException(
        #         status_code=400,
        #         detail="Coin detected but circle fitting failed. Ensure the coin is fully visible and clear.",
        #     )

    except Exception as e:
        logger.exception(f"Error during YOLO detection: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error during YOLO detection: {e}",
        )
