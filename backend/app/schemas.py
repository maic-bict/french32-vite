from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class BoundingBox(BaseModel):
    x: int
    y: int
    width: int
    height: int


class DetectedFood(BaseModel):
    food_name: str
    confidence: float = Field(ge=0, le=1)
    estimated_grams: float = Field(gt=0)
    calories: float = Field(ge=0)
    protein: float = Field(ge=0)
    carbs: float = Field(ge=0)
    fat: float = Field(ge=0)
    bounding_box: BoundingBox
    needs_confirmation: bool = False


class MealAnalysisResponse(BaseModel):
    image_url: str
    confidence: float
    items: List[DetectedFood]
    totals: dict
    status: str


class ManualAdjustment(BaseModel):
    food_name: str
    corrected_grams: float = Field(gt=0)


class SaveMealRequest(BaseModel):
    user_id: int
    image_url: str
    plate_size: Optional[str] = Field(default="medium", pattern="^(small|medium|large)$")
    manual_adjustments: List[ManualAdjustment] = []


class MealItemOut(BaseModel):
    food_name: str
    estimated_grams: float
    calories: float
    protein: float
    carbs: float
    fat: float
    confidence: float


class MealLogOut(BaseModel):
    id: int
    user_id: int
    image_url: str
    total_calories: float
    total_protein: float
    total_carbs: float
    total_fat: float
    confidence: float
    status: str
    created_at: datetime
    items: List[MealItemOut]

    class Config:
        from_attributes = True
