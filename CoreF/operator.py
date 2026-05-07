import cv2
import imagehash
import numpy as np
from dataclasses import dataclass
from pathlib import Path
from PIL import Image


@dataclass
class CullResult:
    path: Path
    blur_score: float
    is_blurry: bool
    is_duplicate: bool
    duplicate_of: Path | None = None

    @property
    def is_rejected(self):
        return self.is_blurry or self.is_duplicate


def compute_blur_score(image: Image.Image, resize_to: int = 512) -> float: 
    img = image.copy()
    img.thumbnail((resize_to, resize_to))
    image_np = np.array(img)
    gray = cv2.cvtColor(image_np, cv2.COLOR_RGB2GRAY)
    laplacian = cv2.Laplacian(gray, cv2.CV_64F)
    return laplacian.var()


def compute_phash(image: Image.Image) -> imagehash.ImageHash:
    return imagehash.phash(image.resize((64, 64)))


def cull_photos(
    photos: list[tuple[Path, Image.Image]],
    blur_threshold: float = 80.0,
    duplicate_threshold: int = 8,
) -> list[CullResult]:
    results = []
    seen_hashes: dict[imagehash.ImageHash, Path] = {}

    for path, image in photos:
        blur_score = compute_blur_score(image)
        phash_score = compute_phash(image)
        is_blurry = blur_score < blur_threshold
        is_duplicate = False
        
        for seen_hash, seen_path in seen_hashes.items():
            if phash_score - seen_hash <= duplicate_threshold:
                results.append(CullResult(
                    path=path,
                    blur_score=blur_score,
                    is_blurry=is_blurry,
                    is_duplicate=True,
                    duplicate_of=seen_path
                ))
                break
        else:
            seen_hashes[phash_score] = path
            results.append(CullResult(
                path=path,
                blur_score=blur_score,
                is_blurry=is_blurry,
                is_duplicate=False
            ))
    return results