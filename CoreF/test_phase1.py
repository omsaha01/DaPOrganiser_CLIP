# test_phase1.py
from pathlib import Path
from extractor import load_image, scan_directory
from utils_op import cull_photos
from classifier import PhotoClassifier

# ── Test 1: Scan + Extract ────────────────────────────────────────
print("\n=== Test 1: Extractor ===")
paths = scan_directory(Path("E:/Edit/DCIM/100MSDCF/CityLandScape"))
print(f"Found {len(paths)} photos")

loaded = []
for path in paths:
    img = load_image(path)
    if img:
        loaded.append((path, img))
        print(f"  ✅ {path.name} → {img.size}")
    else:
        print(f"  ❌ {path.name} → failed")

# ── Test 2: Culler ────────────────────────────────────────────────
print("\n=== Test 2: Culler ===")
cull_results = cull_photos(loaded)
for r in cull_results:
    status = "❌ REJECTED" if r.is_rejected else "✅ KEEP"
    print(f"  {status} | {r.path.name} | blur={r.blur_score:.1f} | dupe={r.is_duplicate}")

# ── Test 3: Classifier ────────────────────────────────────────────
print("\n=== Test 3: Classifier ===")
classifier = PhotoClassifier()

keepers = [(p, img) for (p, img) in loaded 
           if not next(r for r in cull_results if r.path == p).is_rejected]

for path, img in keepers:
    result = classifier.classify(img, path)
    ambig = " ⚠️ ambiguous" if result.is_ambiguous else ""
    print(f"\n  {path.name}")
    print(f"  → {result.genre.upper()} ({result.confidence:.0%}){ambig}")
    for genre, score in sorted(result.all_scores.items(), key=lambda x: -x[1]):
        bar = "█" * int(score * 40)
        print(f"     {genre:<14} {score:.1%}  {bar}")