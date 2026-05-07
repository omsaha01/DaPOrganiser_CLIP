# 📸 Photo Sorter
**Intelligent RAW photo classification using CLIP**

Sort 3000+ RAW photos into genres in minutes — no Lightroom subscription needed.

---

## 🧠 What You'll Learn From This Project

| Module | Concept |
|--------|---------|
| `extractor.py` | How RAW files work, binary file parsing, rawpy |
| `culler.py` | Computer vision, Laplacian operator, perceptual hashing |
| `classifier.py` | CLIP, embeddings, cosine similarity, zero-shot classification |
| `exif_reader.py` | EXIF metadata standard, GPS coordinates, EXIF rational format |
| `organizer.py` | Safe file I/O, shutil, conflict resolution |
| `main.py` | CLI design with argparse, rich terminal UI |

---

## 🚀 Setup

```bash
# 1. Clone or navigate to the project
cd photo-sorter

# 2. Create virtual environment (always do this!)
python -m venv venv
source venv/bin/activate        # Mac/Linux
# venv\Scripts\activate         # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run on your photos
python main.py --input /path/to/your/photos --output /path/to/sorted
```

---

## ⚙️ Usage

```bash
# Basic (safe copy mode)
python main.py --input ./photos --output ./sorted

# Move files instead of copying (faster, no duplicates)
python main.py --input ./photos --output ./sorted --mode move

# More tolerant blur detection (good for indoor/low light)
python main.py --input ./photos --output ./sorted --blur-threshold 50

# Stricter duplicate detection
python main.py --input ./photos --output ./sorted --duplicate-threshold 5

# All options
python main.py --help
```

---

## 📁 Output Structure

```
sorted/
├── landscape/          ← Mountains, nature, scenics
├── portrait/           ← People, faces
├── street/             ← Urban, candid, documentary
├── travel/             ← Landmarks, cultural sites
├── wildlife/           ← Animals in nature
├── abstract/           ← Macro, minimalist, artistic
├── architecture/       ← Buildings, structures
├── _review/            ← Ambiguous — needs manual check
└── _rejected/
    └── rejected.log    ← List of blurry/duplicate shots
```

---

## 🔧 Tuning the Pipeline

### Blur Threshold (`--blur-threshold`)
| Shooting Style | Recommended Value |
|---|---|
| Studio / tripod work | 120–150 |
| Outdoor daylight | 80–100 (default) |
| Indoor / low light | 40–60 |
| Night / long exposure | 20–40 |

### Duplicate Threshold (`--duplicate-threshold`)
| Value | Behavior |
|---|---|
| 3–5 | Very strict — only near-identical shots |
| 6–8 | Default — catches burst duplicates |
| 10–12 | Loose — catches similar scenes |

### Ambiguity Threshold (`--ambiguity-threshold`)
- Lower (0.05) → fewer photos in `_review`, might misclassify edge cases
- Higher (0.25) → more photos in `_review`, more conservative

---

## 🗺️ Roadmap

- [x] **Phase 1** — RAW extraction + culling + CLIP classification + file organization
- [ ] **Phase 2** — EXIF-boosted classification + SQLite embedding store + confidence logging
- [ ] **Phase 3** — Semantic search ("moody rainy street")
- [ ] **Phase 4** — Streamlit web UI for visual review
- [ ] **Phase 5** — Instagram export pipeline (auto-resize, sharpen, batch export)

---

## 🧪 How CLIP Classification Works

```
Your photo (RAW)
      ↓
Extract embedded JPEG preview (rawpy)
      ↓
Preprocess: resize, normalize (CLIP transform)
      ↓
Encode to 512-dim embedding vector (ViT-B-32)
      ↓
Compare with pre-encoded genre text vectors
("a scenic landscape photo", "a portrait of a person", ...)
      ↓
Cosine similarity → Softmax → Probability per genre
      ↓
Top genre = classification, confidence gap = ambiguity check
```

---

## 📦 Tech Stack

| Library | Purpose |
|---|---|
| `open-clip-torch` | CLIP model for zero-shot classification |
| `rawpy` | RAW file reading (Sony ARW, Canon CR2, Nikon NEF, etc.) |
| `Pillow` | Image loading and processing |
| `opencv-python` | Blur detection via Laplacian variance |
| `ImageHash` | Perceptual hashing for duplicate detection |
| `piexif` | EXIF metadata reading |
| `rich` | Beautiful CLI output |
| `PyTorch` | Deep learning backend for CLIP |