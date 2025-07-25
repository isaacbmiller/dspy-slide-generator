import dspy
import re

def lm_with_temp(temperature: float = 0.0, model: str = "gpt-4.1"):
    return dspy.LM(model=model, temperature=temperature)


def clean_slide_name(slide_name: str):
    # Replace any character that is not alphanumeric, dash, or underscore with underscore
    cleaned = re.sub(r'[^a-zA-Z0-9_-]', '_', slide_name)
    # Remove leading/trailing underscores and collapse multiple underscores
    cleaned = re.sub(r'_+', '_', cleaned).strip('_')
    return cleaned.lower()

def to_PIL_image(dspy_image):
    """
    Convert a dspy.Image to a PIL Image object.

    Args:
        dspy_image: dspy.Image instance (see @image.py)

    Returns:
        PIL.Image.Image object

    Raises:
        ImportError: if Pillow is not installed
        ValueError: if the image data cannot be decoded
    """
    # Defensive: handle None
    if dspy_image is None:
        raise ValueError("dspy_image is None")

    # Try to import PIL.Image
    try:
        from PIL import Image as PILImage
    except ImportError:
        raise ImportError("Pillow is required to convert dspy.Image to PIL Image.")

    url = getattr(dspy_image, "url", None)
    if url is None:
        raise ValueError("dspy.Image does not have a 'url' attribute.")

    if url.startswith("data:"):
        # Parse data URI: data:[<mediatype>][;base64],<data>
        import base64
        import io
        header, b64data = url.split(",", 1)
        if ";base64" in header:
            image_bytes = base64.b64decode(b64data)
            return PILImage.open(io.BytesIO(image_bytes))
        else:
            raise ValueError("Only base64-encoded data URIs are supported.")
    elif url.startswith("http://") or url.startswith("https://"):
        # Download the image
        import requests
        import io
        response = requests.get(url)
        response.raise_for_status()
        return PILImage.open(io.BytesIO(response.content))
    else:
        # Assume it's a file path
        from os.path import exists
        if exists(url):
            return PILImage.open(url)
        else:
            raise ValueError(f"Cannot resolve image source: {url}")
