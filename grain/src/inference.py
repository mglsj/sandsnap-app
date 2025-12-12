from helpers import get_image_from_bytes
from models import Coin, PredictionResponse
from sedinet.predict import predict_grain_size
import numpy as np
from logger import logger

TILE_SIZE = 1024


def prepare_tiles(img: np.ndarray, coin: Coin | None) -> list[np.ndarray]:
    """
    Crops the image into squares for the AI, avoiding the coin.
    """
    logger.info("[*] Tiling image for analysis...")

    tiles: list[np.ndarray] = []
    h, w, _ = img.shape

    # Simple sliding window
    step = TILE_SIZE
    for y in range(0, h - step, step):
        for x in range(0, w - step, step):
            # Check if this tile overlaps with the coin (basic box collision)
            # We add a buffer to the coin radius to be safe
            if (
                coin is not None
                and x < coin.center_x + coin.radius_px + 50
                and x + step > coin.center_x - coin.radius_px - 50
                and y < coin.center_y + coin.radius_px + 50
                and y + step > coin.center_y - coin.radius_px - 50
            ):
                continue  # Skip this tile, it contains the coin

            tile = img[y : y + TILE_SIZE, x : x + TILE_SIZE]
            tiles.append(tile)

    logger.info(f"    - Generated {len(tiles)} valid sand tiles.")

    return tiles


def run_sedinet_analysis(tiles: list[np.ndarray]):
    """
    Passes the tiles to the SediNet model.
    """
    logger.info("[*] Running SediNet Model...")

    try:
        all_predictions: list[list[float]] = []
        for tile in tiles:
            # Returns [P10, P16, P25, P50, P50mean, P65, P75, P84, P90]
            predictions = predict_grain_size(tile)
            all_predictions.append(predictions)

        if not all_predictions:
            return None

        # Convert to numpy array for easy column-wise operations
        # Shape: (num_tiles, 9)
        all_predictions_np = np.array(all_predictions)

        # Calculate median for each percentile across all tiles
        aggregated_preds = np.median(all_predictions_np, axis=0)

        logger.info("    - Aggregated Predictions (px): ", aggregated_preds)
        logger.info("[*] SediNet analysis complete.")

        return aggregated_preds

    except Exception as e:
        logger.error(f"Error loading SediNet model: {e}")


percentiles = ["10", "16", "25", "50", "50mean", "65", "75", "84", "90"]


def run_inference(
    image_bytes: bytes, coin: Coin | None, mm_per_pixel: float
) -> PredictionResponse:
    image = get_image_from_bytes(image_bytes)
    img = np.array(image)

    tiles = prepare_tiles(img, coin)
    if not tiles:
        raise ValueError("No valid sand tiles could be generated from the image.")

    grain_size_results_px = run_sedinet_analysis(tiles)

    if grain_size_results_px is None:
        raise ValueError("SediNet analysis failed to produce results.")

    results = {}
    for perc, size in zip(percentiles, grain_size_results_px):
        results[f"D{perc}"] = size * mm_per_pixel

    logger.info(f"Final grain size results (mm): {results}")

    return PredictionResponse(
        size_mm=grain_size_results_px[3] * mm_per_pixel,
        distribution_mm=results,
    )
