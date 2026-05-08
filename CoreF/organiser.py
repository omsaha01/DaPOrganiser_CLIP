# core/organizer.py
import shutil
from dataclasses import dataclass
from pathlib import Path
from coreF.classifier import ClassificationResult


@dataclass
class OrganizeResult:
    source: Path
    destination: Path
    genre: str
    action: str          # "copied", "moved", "failed: <reason>"

    @property
    def success(self) -> bool:
        return self.action in ("copied", "moved")


def _resolve_conflict(dest: Path) -> Path:
    if not dest.exists():
        return dest 
    counter=0
    while True:
        counter+=1
        new_dest=dest.with_name(f"{dest.stem}_{counter}{dest.suffix}")
        if not new_dest.exists():
            return new_dest

def organize_photos(
    results: list[ClassificationResult],
    output_dir: Path,
    mode: str = "copy",
    ambiguous_folder: str = "_review",
) -> list[OrganizeResult]:
    output_dir.mkdir(parents=True, exist_ok=True)
    organize_results = []

    for result in results:
        if result.is_ambiguous:
            target_folder = ambiguous_folder
        else:
            target_folder = result.genre
        target_dir = output_dir / target_folder
        target_dir.mkdir(parents=True, exist_ok=True)
        dest=_resolve_conflict(target_dir / result.path.name) 
        try:
            if mode == "copy":
                shutil.copy2(str(result.path), str(dest))
                action = "copied"
                organize_results.append(OrganizeResult(
                    source=result.path,
                    destination=dest,
                    genre=target_folder,
                    action=action
                ))
            elif mode == "move":
                shutil.move(str(result.path), str(dest))
                action = "moved"
                organize_results.append(OrganizeResult(
                    source=result.path,
                    destination=dest,
                    genre=target_folder,
                    action=action
                ))
        except Exception as e:
            action = f"failed: {e}"
            organize_results.append(OrganizeResult(
                    source=result.path,
                    destination=dest,
                    genre=target_folder,
                    action=action
                ))
    return organize_results


def get_organize_stats(results: list[OrganizeResult]) -> dict:
    from collections import Counter
    genre_counts = Counter(r.genre for r in results if r.success)
    return {
        "total": len(results),
        "successful": sum(1 for r in results if r.success),
        "failed": sum(1 for r in results if not r.success),
        "by_genre": dict(genre_counts),
    }