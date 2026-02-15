from dataclasses import dataclass


@dataclass
class MacroProfile:
    calories: float
    protein: float
    carbs: float
    fat: float


# Tabla interna por 100g (puede sustituirse con USDA API o BD propia)
NUTRITION_TABLE = {
    "chicken_breast": MacroProfile(165, 31.0, 0.0, 3.6),
    "white_rice": MacroProfile(130, 2.7, 28.0, 0.3),
    "broccoli": MacroProfile(35, 2.4, 7.2, 0.4),
}


def macros_for_food(food_name: str, grams: float) -> MacroProfile:
    base = NUTRITION_TABLE.get(food_name)
    if not base:
        # fallback genérico
        base = MacroProfile(100, 5.0, 10.0, 3.0)

    ratio = grams / 100.0
    return MacroProfile(
        calories=round(base.calories * ratio, 2),
        protein=round(base.protein * ratio, 2),
        carbs=round(base.carbs * ratio, 2),
        fat=round(base.fat * ratio, 2),
    )
