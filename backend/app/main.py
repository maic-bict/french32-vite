from pathlib import Path
from typing import Dict, List

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from .ml_pipeline import FoodVisionEngine
from .models import MealItem, MealLog
from .nutrition import macros_for_food
from .schemas import DetectedFood, MealAnalysisResponse, SaveMealRequest

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Food Vision Nutrition API", version="0.1.0")
vision_engine = FoodVisionEngine()


def _analyze(image_url: str, plate_size: str) -> Dict:
    image_path = Path(image_url)
    if not image_path.exists():
        raise HTTPException(status_code=404, detail="Imagen no encontrada")

    predictions = vision_engine.detect_foods(str(image_path))
    items: List[DetectedFood] = []

    totals = {"calories": 0.0, "protein": 0.0, "carbs": 0.0, "fat": 0.0}

    for pred in predictions:
        grams = vision_engine.estimate_grams(pred, plate_size)
        macro = macros_for_food(pred.food_name, grams)
        needs_confirmation = pred.confidence < 0.8

        item = DetectedFood(
            food_name=pred.food_name,
            confidence=pred.confidence,
            estimated_grams=grams,
            calories=macro.calories,
            protein=macro.protein,
            carbs=macro.carbs,
            fat=macro.fat,
            bounding_box=pred.bbox,
            needs_confirmation=needs_confirmation,
        )
        items.append(item)
        totals["calories"] += macro.calories
        totals["protein"] += macro.protein
        totals["carbs"] += macro.carbs
        totals["fat"] += macro.fat

    confidence = vision_engine.aggregate_confidence(predictions)
    status = "needs_user_confirmation" if any(i.needs_confirmation for i in items) else "ready_to_save"

    return {
        "image_url": image_url,
        "confidence": round(confidence, 2),
        "items": items,
        "totals": {k: round(v, 2) for k, v in totals.items()},
        "status": status,
    }


@app.post("/api/v1/meals/analyze", response_model=MealAnalysisResponse)
def analyze_meal(payload: SaveMealRequest):
    return _analyze(payload.image_url, payload.plate_size)


@app.post("/api/v1/meals/save")
def save_meal(payload: SaveMealRequest, db: Session = Depends(get_db)):
    analysis = _analyze(payload.image_url, payload.plate_size)

    adjustments = {a.food_name: a.corrected_grams for a in payload.manual_adjustments}
    total = {"calories": 0.0, "protein": 0.0, "carbs": 0.0, "fat": 0.0}

    meal_log = MealLog(
        user_id=payload.user_id,
        image_url=payload.image_url,
        total_calories=0,
        total_protein=0,
        total_carbs=0,
        total_fat=0,
        confidence=analysis["confidence"],
        status="confirmed_by_user",
    )

    for item in analysis["items"]:
        grams = adjustments.get(item.food_name, item.estimated_grams)
        macro = macros_for_food(item.food_name, grams)
        meal_item = MealItem(
            food_name=item.food_name,
            confidence=item.confidence,
            estimated_grams=grams,
            calories=macro.calories,
            protein=macro.protein,
            carbs=macro.carbs,
            fat=macro.fat,
            bounding_box=item.bounding_box.model_dump(),
        )
        meal_log.items.append(meal_item)
        total["calories"] += macro.calories
        total["protein"] += macro.protein
        total["carbs"] += macro.carbs
        total["fat"] += macro.fat

    meal_log.total_calories = round(total["calories"], 2)
    meal_log.total_protein = round(total["protein"], 2)
    meal_log.total_carbs = round(total["carbs"], 2)
    meal_log.total_fat = round(total["fat"], 2)

    db.add(meal_log)
    db.commit()
    db.refresh(meal_log)

    return {
        "meal_log_id": meal_log.id,
        "status": meal_log.status,
        "totals": {
            "calories": meal_log.total_calories,
            "protein": meal_log.total_protein,
            "carbs": meal_log.total_carbs,
            "fat": meal_log.total_fat,
        },
    }
