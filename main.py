# main.py
import argparse
from pathlib import Path
from rich.console import Console
from rich.table import Table
from collections import Counter
import gc

from coreF.extractor import scan_directory, load_image
from coreF.utils_op import cull_photos
from coreF.exifD import read_exif
from coreF.classifier import PhotoClassifier
from coreF.organiser import organize_photos, get_organize_stats

console = Console()


def run_pipeline(args):
    input_dir  = Path(args.input)
    output_dir = Path(args.output)
    batch_size = args.batch_size

    # ── Step 1: Scan (just paths, no images loaded yet) ──────────
    console.print("\n[bold yellow]Step 1:[/bold yellow] Scanning for photos")
    all_paths = scan_directory(input_dir)
    console.print(f"  Found [green]{len(all_paths)}[/green] photos")

    # ── Pre-load classifier ONCE outside the batch loop ──────────
    # Loading CLIP model is expensive (~5s) — do it once, reuse it
    console.print("\n[bold yellow]Loading CLIP model...[/bold yellow]")
    classifier = PhotoClassifier()

    # ── Batch loop ────────────────────────────────────────────────
    total      = len(all_paths)
    all_classified = []   # accumulate only ClassificationResults (tiny, no images)
    total_kept     = 0
    total_rejected = 0

    # Split all_paths into chunks of batch_size
    # range(0, 3300, 50) → [0, 50, 100, ..., 3300]
    batches = [all_paths[i:i+batch_size] for i in range(0, total, batch_size)]

    for batch_num, batch_paths in enumerate(batches, 1):
        console.print(
            f"\n[bold cyan]Batch {batch_num}/{len(batches)}[/bold cyan] "
            f"({len(batch_paths)} photos)"
        )

        # TODO 1 — Load this batch only
        # Same as before but only for batch_paths
        loaded = []
        for path in batch_paths:
            img = load_image(path)
            if img:
                loaded.append((path, img))

        # TODO 2 — Cull this batch
        # Same cull_photos call as before
        # Build keeper_photos from this batch's results
        cull_results = cull_photos(
            loaded,
            blur_threshold=args.blur_threshold,
            duplicate_threshold=args.duplicate_threshold
        )
        loaded_dict  = {path: img for path, img in loaded}
        keeper_paths = [r.path for r in cull_results if not r.is_rejected]
        keeper_photos = [(p, loaded_dict[p]) for p in keeper_paths]

        kept     = len(keeper_photos)
        rejected = len(loaded) - kept
        total_kept     += kept
        total_rejected += rejected
        console.print(f"  Culled → kept [green]{kept}[/green] | rejected [red]{rejected}[/red]")

        # TODO 3 — Classify this batch
        classified_batch = []
        for path, img in keeper_photos:
            result = classifier.classify(img, path, args.ambiguity_threshold)
            classified_batch.append(result)

        # TODO 4 — Organize this batch immediately
        org_results = organize_photos(classified_batch, output_dir, mode=args.mode)
        stats = get_organize_stats(org_results)
        console.print(f"  Organized → [green]{stats['successful']}[/green] files {args.mode}d")

        # Accumulate just the lightweight results (no images)
        all_classified.extend(classified_batch)

        # ── CRITICAL: Free memory before next batch ───────────────
        # Delete all image objects from this batch
        del loaded, loaded_dict, keeper_photos, classified_batch, org_results
        gc.collect()  # Force Python to release the memory NOW

    # ── Final summary table (after all batches) ───────────────────
    console.print("\n[bold yellow]Final Summary[/bold yellow]")
    table = Table(title=f"Genre Distribution ({len(all_classified)} photos)")
    table.add_column("Genre",  style="cyan")
    table.add_column("Photos", style="green", justify="right")
    table.add_column("%",      justify="right")

    genre_counts = Counter(r.genre for r in all_classified)
    total_classified = len(all_classified)
    for genre, count in sorted(genre_counts.items(), key=lambda x: -x[1]):
        table.add_row(genre, str(count), f"{count/total_classified:.1%}")

    console.print(table)
    console.print(f"\n  📥 Total scanned  : {total}")
    console.print(f"  ✅ Total kept     : [green]{total_kept}[/green]")
    console.print(f"  🗑️  Total rejected : [red]{total_rejected}[/red]")
    console.print(f"  📂 Output         : {output_dir}")


def main():
    parser = argparse.ArgumentParser(description="📸 Photo Sorter")
    parser.add_argument("--input",  "-i", required=True)
    parser.add_argument("--output", "-o", required=True)
    parser.add_argument("--mode",   choices=["copy","move"], default="copy")
    parser.add_argument("--blur-threshold",      type=float, default=80.0)
    parser.add_argument("--duplicate-threshold", type=int,   default=8)
    parser.add_argument("--ambiguity-threshold", type=float, default=0.15)
    parser.add_argument("--batch-size",          type=int,   default=50,
                        help="Photos per batch. Lower = less RAM. Default: 50")
    args = parser.parse_args()
    run_pipeline(args)