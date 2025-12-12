from PIL import Image
import io


def get_image_from_bytes(image_bytes: bytes) -> Image.Image:
    """
    Converts image bytes to a PIL Image.
    """
    return Image.open(io.BytesIO(image_bytes))
