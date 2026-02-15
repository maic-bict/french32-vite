# french32-vite

Ejemplo de implementación de un módulo de nutrición por fotografía para una app fitness de hipertrofia/recomposición.

## Estructura

- `backend/app/main.py`: API FastAPI con endpoints de análisis y guardado.
- `backend/app/ml_pipeline.py`: pipeline de visión (detección/segmentación/estimación de gramos, versión ejemplo).
- `backend/app/nutrition.py`: cálculo de macros por 100g.
- `backend/app/models.py`: modelo de datos SQLAlchemy.
- `docs/nutrition-module-architecture.md`: arquitectura, flujo, JSON ejemplo y estrategia de mejora.

## Ejecutar (demo)

```bash
pip install fastapi uvicorn sqlalchemy pydantic opencv-python numpy
uvicorn backend.app.main:app --reload
```

> Nota: el motor ML actual es un placeholder para mostrar la arquitectura; en producción conecta YOLOv8 + segmentación real.
