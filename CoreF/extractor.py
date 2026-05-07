# core/extractor.py
import io
import logging
from pathlib import Path
import rawpy    
from PIL import Image

logger = logging.getLogger(__name__)

SUPPORTED_RAW  = {".arw", ".cr2", ".cr3", ".nef", ".orf", ".rw2", ".dng", ".raf"}
SUPPORTED_JPEG = {".jpg", ".jpeg"}
ALL_SUPPORTED  = SUPPORTED_RAW | SUPPORTED_JPEG


def extract_raw_preview(raw_path: Path) -> Image.Image | None:
    try:
        with rawpy.imread(str(raw_path)) as raw:
            thumb = raw.extract_thumb()

            if thumb.format == rawpy.ThumbFormat.JPEG:
                return Image.open(io.BytesIO(thumb.data)).convert("RGB")
                

            elif thumb.format == rawpy.ThumbFormat.BITMAP:
                return Image.fromarray(thumb.data).convert("RGB")
                
    except Exception as e:
        logger.warning(f"Failed on {raw_path.name}: {e}")
    return None


def load_image(path: Path) -> Image.Image | None:
    ext = path.suffix.lower()
    if ext in SUPPORTED_RAW:
        return extract_raw_preview(path)
    elif ext in SUPPORTED_JPEG:
        try:
            return Image.open(path).convert("RGB")
        except Exception as e:
            logger.warning(f"Failed on {path.name}: {e}")
            return None
    return None


def scan_directory(directory: Path) -> list[Path]:
    if not directory.exists():
        raise FileNotFoundError(f"Not found: {directory}")
    found = set()
    for ext in ALL_SUPPORTED:
        found.update(directory.rglob(f"*{ext}"))
        found.update(directory.rglob(f"*{ext.upper()}"))
    return sorted(found)