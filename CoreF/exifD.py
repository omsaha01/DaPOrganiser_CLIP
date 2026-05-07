# core/exif_reader.py
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import piexif


@dataclass
class ExifData:
    path: Path
    focal_length: float | None = None
    aperture: float | None = None
    iso: int | None = None
    timestamp: datetime | None = None
    gps_lat: float | None = None
    gps_lon: float | None = None

    @property
    def has_gps(self) -> bool:
        return self.gps_lat is not None and self.gps_lon is not None

    @property
    def genre_hints(self) -> list[str]:
        # TODO 1:
        hints = []
        if self.focal_length is not None:
                  if self.focal_length <= 24:
                        hints.append("landscape")
                  elif 30 <= self.focal_length <= 55:
                        hints.append("street")
                  elif 70 <= self.focal_length <= 200:
                        hints.append("portrait")
                  elif self.focal_length > 200:
                        hints.append("wildlife")
                  elif self.has_gps:
                        hints.append("travel")
        return list(set(hints))


def _rational_to_float(rational) -> float | None:
    try:
        return rational[0] / rational[1] if rational[1] != 0 else None
    except (TypeError, IndexError):
        return None


def read_exif(path: Path) -> ExifData:
    data = ExifData(path=path)
    try:
        exif_dict = piexif.load(str(path))
    except Exception:
        return data

    exif = exif_dict.get("Exif", {})

    # TODO 3 — focal length:
    if piexif.ExifIFD.FocalLength in exif:
        data.focal_length = _rational_to_float(exif[piexif.ExifIFD.FocalLength])

    # TODO 4 — aperture:
    if piexif.ExifIFD.FNumber in exif:
        data.aperture = _rational_to_float(exif[piexif.ExifIFD.FNumber])

    # TODO 5 — ISO:
    if piexif.ExifIFD.ISOSpeedRatings in exif:
        data.iso = exif[piexif.ExifIFD.ISOSpeedRatings]
        
    # TODO 6 — timestamp:
    key = piexif.ExifIFD.DateTimeOriginal
    if key in exif:
        value = exif[key]
        if isinstance(value, bytes):
            value = value.decode("utf-8").strip("\x00").strip()
        try:
            data.timestamp = datetime.strptime(value, "%Y:%m:%d %H:%M:%S")
        except (ValueError, TypeError):
            pass
    return data