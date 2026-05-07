# core/classifier.py
from dataclasses import dataclass, field
from pathlib import Path
import torch
import open_clip
from PIL import Image


GENRE_PROMPTS: dict[str, list[str]] = {


    "landscape": [
        "wide natural landscape photography of mountains, forests, rivers",
        "untouched wilderness scenery with dramatic natural lighting",
        "scenic nature vista with sky and terrain"
    ],


    "portrait": [
        "close up portrait photography of a human face with soft background blur",
        "studio headshot with controlled lighting",
        "professional human face portrait photography"
    ],


    "street": [
        "candid street photography with people in motion in urban environment",
        "documentary city life photography with natural moments",
        "urban street scene capturing human interactions"
    ],

    "cityscape": [
        "wide city skyline with buildings and lights at night",
        "aerial view of dense urban cityscape",
        "panoramic view of modern city skyline"
    ],


    "architecture": [
        "modern architectural building exterior with geometric design",
        "interior architecture photography with clean lines and structure",
        "historic building facade with architectural detail"
    ],


    "travel": [
        "travel photography showing tourist landmarks and cultural scenes",
        "people exploring famous destinations and monuments",
        "vacation photography capturing experiences and locations"
    ],

    "wildlife": [
        "wild animal in natural habitat wildlife photography",
        "bird or mammal captured in wilderness environment",
        "close up nature wildlife behavior photography"
    ],

    "still_life": [
        "studio product photography of objects on clean background",
        "carefully arranged objects in still life composition",
        "tabletop object photography with controlled lighting"
    ],

    "abstract": [
        "abstract photography with shapes colors and textures",
        "minimalist geometric artistic composition",
        "macro texture photography with artistic focus"
    ],

    "night_photography": [
        "night photography with long exposure and artificial lights",
        "low light urban scene with neon lighting",
        "dark environment photography with illuminated subjects"
    ],


    "adventure": [
        "outdoor adventure photography with hiking climbing or exploration",
        "person in extreme natural environment like mountains or cliffs",
        "action oriented outdoor exploration photography"
    ],

    "event": [
        "crowded public event photography with stage or celebration",
        "concert wedding or festival photography with groups of people",
        "live event documentation with audience and activity"
    ],
    
    "sports":[
        "sports action photography with athletes in motion",
        "dynamic sports event photography capturing athletic performance"
    ]
    
}

@dataclass
class ClassificationResult:
    path: Path
    genre: str
    confidence: float
    all_scores: dict[str, float] = field(default_factory=dict)
    is_ambiguous: bool = False
    second_genre: str = ""
    second_confidence: float = 0.0


class PhotoClassifier:

    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"  Device: {self.device}")

        self.model,_,self.preprocess=open_clip.create_model_and_transforms(model_name="ViT-B-32",pretrained="laion2b_s34b_b79k")
        
        self.model=self.model.to(self.device).eval()
        self.tokenizer=open_clip.get_tokenizer("ViT-B-32")

        self.genre_names,self.text_features=self._encode_genres()


    def _encode_genres(self) -> tuple[list[str], torch.Tensor]:
        genre_names = []
        genre_vectors = []

        with torch.no_grad():
            for genre_name, prompts in GENRE_PROMPTS.items():
                tokens = self.tokenizer(prompts).to(self.device)
                embeddings = self.model.encode_text(tokens)
                embeddings = embeddings / embeddings.norm(dim=-1, keepdim=True)
                avg_embedding = embeddings.mean(dim=0)
                avg_embedding = avg_embedding / avg_embedding.norm()
                genre_names.append(genre_name)
                genre_vectors.append(avg_embedding)
        return genre_names, torch.stack(genre_vectors)

    def classify(
        self,
        image: Image.Image,
        path: Path,
        ambiguity_threshold: float = 0.15,) -> ClassificationResult:
        
        with torch.no_grad():
            img= self.preprocess(image).unsqueeze(0).to(self.device)
            encoded_image = self.model.encode_image(img)
            normalized_image = encoded_image / encoded_image.norm(dim=-1, keepdim=True)
            similarities = (normalized_image @ self.text_features.T).squeeze(0)
            probs = (similarities * 100).softmax(dim=-1).cpu().numpy()
            all_scores={
                genre: float(prob) for genre, prob in zip(self.genre_names, probs)
            }
            sorted_genres = sorted(all_scores.items(), key=lambda x: x[1], reverse=True)
            top_genre, top_score = sorted_genres[0] 
            second_genre, second_score = sorted_genres[1]
            is_ambiguous = (top_score - second_score) < ambiguity_threshold
            
        
        return ClassificationResult(path=path, genre=top_genre, confidence=top_score, all_scores=all_scores, is_ambiguous=is_ambiguous, 
                                     second_genre=second_genre, second_confidence=second_score)