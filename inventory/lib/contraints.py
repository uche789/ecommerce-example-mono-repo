import re

def is_valid_image(mimeType: str) -> bool:
    """Check if file is a valid image (webp, jpeg, png, tiff, etc.)."""
    allowed_mime_types = {
        "image/jpeg",
        "image/png",
        "image/webp",
        "image/tiff",
        "image/gif",
        "image/bmp"
    }

    return mimeType in allowed_mime_types

def matchesExpression(pattern, value) -> bool:
    # pattern = r"\s*\d+\s*,"
    matches = re.match(pattern, value)
    return matches != None

def hasAnyAttributes(obj):
    return bool(obj.__dict__)