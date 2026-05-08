🎯 The Problem
You come back from a shoot with 3000+ RAW/any files. Before you can edit or post, you need to sort them — landscapes go here, portraits go there, street shots somewhere else. Manually, this takes hours.
Existing tools like Lightroom require expensive subscriptions. digiKam can tag by face or colour, but can't understand what a photo means — it can't tell a moody street scene from a travel landmark.
Photo Sorter uses CLIP — the same vision-language model powering modern AI image search — to understand your photos semantically and sort them automatically.

✨ Features

🤖 Zero-shot genre classification — no training required, just describe your genres in plain English
📷 Native RAW support — reads Sony ARW, Canon CR2/CR3, Nikon NEF, Fuji RAF and more without exporting
🗑️ Intelligent culling — removes blurry shots via Laplacian blur detection and burst duplicates via perceptual hashing
⚡ Batch processing — handles thousands of photos with controlled memory usage
🔍 EXIF-aware — uses focal length and GPS metadata to boost classification confidence
📁 Safe by default — copy mode preserves all originals until you're confident
🎯 Ambiguity flagging — uncertain classifications go to _review/ for manual sorting
💻 Fully offline — after the one-time model download, no internet needed


🖥️ Demo
Step 1: Scanning for photos
  Found 3,312 photos in /Volumes/SD_CARD/DCIM

Step 2: Extracting previews
  Loaded 3,312 photos

Step 3: Culling
  Kept 2,847 photos | Rejected 465 (blurry: 312, duplicates: 153)

Step 4: Classifying genres
  Device: cpu/GPU | Model: CLIP ViT-B-32

Step 5: Results

  ┌─────────────────────────────────────────┐
  │         Genre Distribution              │
  ├──────────────┬────────┬─────────────────┤
  │ Genre        │ Photos │ % of keepers    │
  ├──────────────┼────────┼─────────────────┤
  │ landscape    │    981 │ 34.5%           │
  │ travel       │    632 │ 22.2%           │
  │ portrait     │    511 │ 18.0%           │
  │ street       │    398 │ 14.0%           │
  │ architecture │    201 │  7.1%           │
  │ wildlife     │    124 │  4.4%           │
  └──────────────┴────────┴─────────────────┘

  ⚠️  142 photos flagged for manual review in _review/

Step 6: Organizing files
  ✅ 2,705 files copied | ❌ 0 failed
  📂 Output: ./sorted

📁 Output Structure
sorted/
├── landscape/          ← Mountains, nature, wide shots
├── portrait/           ← People, faces
├── street/             ← Urban, candid, documentary
├── travel/             ← Landmarks, cultural destinations
├── wildlife/           ← Animals in nature
├── architecture/       ← Buildings, structures
├── _review/            ← Ambiguous — needs a quick manual check
└── _rejected/
    └── rejected.log    ← List of culled shots (originals untouched)

🛠️ Setup
Requirements: Python 3.11+, ~2GB disk space for the CLIP model
bash# 1. Clone the repo
git clone (https://github.com/omsaha01/DaPOrganiser_CLIP)
cd DaPOrganiser_CLIP

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate       # Mac/Linux
# venv\Scripts\activate        # Windows

# 3. Install dependencies
pip install -r requirements.txt

The CLIP model (~350MB) downloads automatically on first run. After that, everything works offline.


🚀 Usage
Basic
bashpython main.py --input /path/to/photos --output /path/to/sorted
With options
bashpython main.py \
  --input  ./photos     \
  --output ./sorted     \
  --mode   copy         \
  --batch-size 50
All flags
FlagDefaultDescription--input -irequiredFolder with RAW/JPEG photos--output -orequiredDestination for sorted photos--modecopycopy preserves originals · move saves disk space--batch-size50Photos per batch — lower if you have limited RAM--blur-threshold80.0Laplacian variance below this = blurry shot--duplicate-threshold8pHash distance ≤ this = duplicate/burst shot--ambiguity-threshold0.15Confidence gap below this = flagged for review
Tuning for your setup
bash# Low RAM (8GB) machine
python main.py --input ./photos --output ./sorted --batch-size 25

# Indoor / low-light photography
python main.py --input ./photos --output ./sorted --blur-threshold 40

# Heavy burst shooter
python main.py --input ./photos --output ./sorted --duplicate-threshold 5
