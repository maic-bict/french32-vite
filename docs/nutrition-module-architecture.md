# Módulo de nutrición por foto (hipertrofia y recomposición)

## 1) Arquitectura completa

```text
[React/Flutter App]
  ├─ Cámara / subida de imagen
  ├─ Preview editable (gramos, borrar, agregar alimento)
  └─ API Client
          |
          v
[FastAPI Backend]
  ├─ /meals/analyze
  │   ├─ Preprocesado OpenCV
  │   ├─ Detección + clasificación (YOLOv8 Food)
  │   ├─ Segmentación por alimento
  │   ├─ Estimación de porción (área + tamaño plato + calibración)
  │   └─ Cálculo nutricional (tabla por 100g / USDA)
  ├─ /meals/save
  │   ├─ Recalcular con ajustes del usuario
  │   ├─ Persistir MealLog + MealItems
  │   └─ Guardar correcciones para aprendizaje personalizado
  └─ Auth + validaciones
          |
          v
[PostgreSQL/SQLite]
  ├─ users
  ├─ meal_logs
  ├─ meal_items
  └─ user_corrections
```

## 2) Flujo de datos

1. Usuario toma foto del plato.
2. Frontend envía imagen y `plate_size` (`small|medium|large`) a `/api/v1/meals/analyze`.
3. Backend detecta múltiples alimentos y devuelve confianza por objeto.
4. Si confianza `< 0.80`, marca `needs_confirmation=true` y exige validación humana.
5. Sistema estima gramos y macros por alimento.
6. Frontend presenta resumen editable.
7. Usuario confirma/edita y envía a `/api/v1/meals/save`.
8. Backend recalcula macros finales y guarda el registro.
9. Correcciones se almacenan para personalización futura.

## 3) Lógica de fallback y validaciones

- **Confianza baja**: no guardar automáticamente; solicitar confirmación.
- **Edición manual**: siempre permitida por alimento.
- **No persistencia sin confirmación**: estado intermedio `needs_user_confirmation`.
- **Trazabilidad**: guardar bbox, confianza y gramos corregidos.

## 4) Mejora progresiva del modelo

1. **Fase 1 (MVP)**: YOLOv8 + tabla nutricional interna por 100g.
2. **Fase 2**: Fine-tuning con dataset de platos reales de tus usuarios (anotación semiautomática).
3. **Fase 3**: Modelo de profundidad/volumen (MiDaS + calibración por plato) para gramos más precisos.
4. **Fase 4**: Aprendizaje personalizado por usuario:
   - Factor de corrección por alimento frecuente.
   - Priorización de platos históricos.
   - Predicción contextual según objetivo (`bulk`, `cut`, `maintenance`).
5. **Fase 5**: Active learning: muestras con baja confianza pasan a cola de re-etiquetado.

## 5) Respuesta JSON ejemplo

```json
{
  "image_url": "uploads/meal_2026_02_14.jpg",
  "confidence": 0.83,
  "status": "needs_user_confirmation",
  "items": [
    {
      "food_name": "chicken_breast",
      "confidence": 0.91,
      "estimated_grams": 140.0,
      "calories": 231.0,
      "protein": 43.4,
      "carbs": 0.0,
      "fat": 5.04,
      "needs_confirmation": false,
      "bounding_box": {"x": 56, "y": 110, "width": 190, "height": 170}
    },
    {
      "food_name": "broccoli",
      "confidence": 0.72,
      "estimated_grams": 60.0,
      "calories": 21.0,
      "protein": 1.44,
      "carbs": 4.32,
      "fat": 0.24,
      "needs_confirmation": true,
      "bounding_box": {"x": 160, "y": 290, "width": 120, "height": 95}
    }
  ],
  "totals": {
    "calories": 252.0,
    "protein": 44.84,
    "carbs": 4.32,
    "fat": 5.28
  }
}
```
