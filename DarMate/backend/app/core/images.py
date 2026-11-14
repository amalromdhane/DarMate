import io

from PIL import Image

from app.core.exceptions import ValidationFailedError

MIN_W, MIN_H = 640, 480
MAX_W, MAX_H = 6000, 6000
ALLOWED_FORMATS = {"JPEG", "PNG", "WEBP"}

Image.MAX_IMAGE_PIXELS = MAX_W * MAX_H      # protège contre les « decompression bombs »


def check_image(content: bytes) -> None:
    """Vérifie le contenu réel du fichier : un .exe ou un script renommé en .jpg est refusé."""
    try:
        Image.open(io.BytesIO(content)).verify()
        img = Image.open(io.BytesIO(content))
        fmt, (w, h) = img.format, img.size
    except Exception:
        raise ValidationFailedError("Fichier invalide : seules les images JPG, PNG et WebP sont acceptées.")

    if fmt not in ALLOWED_FORMATS:
        raise ValidationFailedError("Format non autorisé : JPG, PNG ou WebP uniquement.")
    if w < MIN_W or h < MIN_H:
        raise ValidationFailedError(f"Image trop petite ({w}×{h}, minimum {MIN_W}×{MIN_H}).")
    if w > MAX_W or h > MAX_H:
        raise ValidationFailedError(f"Image trop grande ({w}×{h}, maximum {MAX_W}×{MAX_H}).")