# main.py
import argparse
from pathlib import Path
from rich.console import Console
from rich.table import Table
from collections import Counter

from coreF.extractor import scan_directory, load_image
from coreF.utils_op import cull_photos
from coreF.exifD import read_exif
from coreF.classifier import PhotoClassifier
from coreF.organiser import organize_photos, get_organize_stats

console = Console()

def run_pipeline(args):
    input_dir = Path(args.input)
    output_dir = Path(args.output)

    # ── Step 1: Scan ─────────────────────────────────────────────
    console.print("\n[bold yellow]Step 1:[/bold yellow] Scanning for photos")
    paths = scan_directory(input_dir)
    console.print(f"  Found [green]{len(paths)}[/green] photos")

    # ── Step 2: Load previews ─────────────────────────────────────
    console.print("\n[bold yellow]Step 2:[/bold yellow] Extracting previews")
    loaded = []
    for path in paths:
        img = load_image(path)
        if img:
            loaded.append((path, img))
    console.print(f"  Loaded [green]{len(loaded)}[/green] photos")

    # ── Step 3: Cull ──────────────────────────────────────────────
    console.print("\n[bold yellow]Step 3:[/bold yellow] Culling")
    results=cull_photos(loaded, blur_threshold=args.blur_threshold,
                duplicate_threshold=args.duplicate_threshold)
    keepers= [photo.path for photo in results if not photo.is_rejected]
    console.print(f"  Kept [green]{len(keepers)}[/green] photos, Rejected [red]{len(results)-len(keepers)}[/red]")    
    loaded_dict={path: img for path, img in loaded}
    keepers_photos=[(path, loaded_dict[path]) for path in keepers]

    # ── Step 4: Classify ──────────────────────────────────────────
    console.print("\n[bold yellow]Step 4:[/bold yellow] Classifying genres")
    classifier=PhotoClassifier()
    classified=[]
    for path,img in keepers_photos:
        result=classifier.classify(img, path, ambiguity_threshold=args.ambiguity_threshold)
        print(f"  {path.name}: {result.genre} ({result.confidence:.2f})")
        classified.append(result)
    # Load model once

    # ── Step 5: Print summary table ───────────────────────────────
    console.print("\n[bold yellow]Step 5:[/bold yellow] Results")
    table = Table(title="Genre Distribution")
    table.add_column("Genre", style="cyan")
    table.add_column("Photos", style="green", justify="right")
    table.add_column("%", justify="right")
    
    genre_counts = Counter(r.genre for r in classified)
    
    total = len(classified)
    for genre, count in sorted(genre_counts.items(), key=lambda x: -x[1]):
        table.add_row(genre, str(count), f"{count/total:.1%}")

    console.print(table)

    # ── Step 6: Organize ──────────────────────────────────────────
    console.print("\n[bold yellow]Step 6:[/bold yellow] Organizing files")
    org_results=organize_photos(classified, output_dir, mode=args.mode)
    stats=get_organize_stats(org_results)
    console.print(f"  ✅ {stats['successful']} files {args.mode}d | ❌ {stats['failed']} failed")
    console.print(f"  📂 Output: {output_dir}")



def main():
    parser = argparse.ArgumentParser(description="📸 Photo Sorter")
    parser.add_argument("--input",  "-i", required=True)
    parser.add_argument("--output", "-o", required=True)
    parser.add_argument("--mode", choices=["copy","move"], default="copy")
    parser.add_argument("--blur-threshold", type=float, default=80.0)
    parser.add_argument("--duplicate-threshold", type=int, default=8)
    parser.add_argument("--ambiguity-threshold", type=float, default=0.15)
    args = parser.parse_args()
    run_pipeline(args)


if __name__ == "__main__":
    main()