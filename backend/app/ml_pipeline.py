from dataclasses import dataclass
from typing import List

import cv2
import numpy as np


@dataclass
class Prediction:
    food_name: str
    confidence: float
    bbox: dict
    mask_area_px: int


class FoodVisionEngine:
    """
    Ejemplo de pipeline CV/ML:
    - Detección multicategoría con YOLOv8 (placeholder)
    - Segmentación para área útil
    - Estimación de gramos usando área relativa + tamaño de plato
    """

    PLATE_FACTORS = {"small": 0.85, "medium": 1.0, "large": 1.2}

    def detect_foods(self, image_path: str) -> List[Prediction]:
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError("No se pudo leer la imagen")

        # Placeholder de salida de YOLO + segmentación.
        h, w = image.shape[:2]
        return [
            Prediction("chicken_breast", 0.91, {"x": int(w * 0.1), "y": int(h * 0.25), "width": int(w * 0.35), "height": int(h * 0.35)}, 14000),
            Prediction("white_rice", 0.86, {"x": int(w * 0.52), "y": int(h * 0.28), "width": int(w * 0.3), "height": int(h * 0.32)}, 12000),
            Prediction("broccoli", 0.72, {"x": int(w * 0.35), "y": int(h * 0.62), "width": int(w * 0.25), "height": int(h * 0.2)}, 8000),
        ]

    def estimate_grams(self, prediction: Prediction, plate_size: str = "medium") -> float:
        plate_factor = self.PLATE_FACTORS.get(plate_size, 1.0)
        # Heurística simplificada: gramos = área_segmentada * factor / densidad base.
        density_lookup = {
            "chicken_breast": 0.010,
            "white_rice": 0.012,
            "broccoli": 0.006,
        }
        density = density_lookup.get(prediction.food_name, 0.009)
        grams = prediction.mask_area_px * density * plate_factor
        return round(float(grams), 1)

    def aggregate_confidence(self, predictions: List[Prediction]) -> float:
        if not predictions:
            return 0.0
        return float(np.mean([p.confidence for p in predictions]))
