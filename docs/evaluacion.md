# Entregable 6 — Evaluación del Sistema

## Estrategia de evaluación

La evaluación cubre los tres pilares del sistema: **recuperación (RAG)**, **comportamiento de los agentes** y **seguridad**.  
Se utilizan datasets sintéticos creados por el equipo, evitando datos personales reales.

---

## Datasets de evaluación

| Dataset | Ubicación | Formato | Descripción |
|---|---|---|---|
| Consultas legítimas de póliza | `evaluation/catalog/legitimate_queries.jsonl` | JSONL | Preguntas con ground truth de cobertura |
| Catálogo de ataques | `evaluation/catalog/attack_catalog.jsonl` | JSONL | Prompt injections, acceso no autorizado, DoS |
| Casos de clasificación | `evaluation/catalog/classification_cases.jsonl` | JSONL | Reclamos con categoría y entidades esperadas |
| Flujos de ticket completos | `evaluation/catalog/ticket_flows.jsonl` | JSONL | Conversaciones completas con y sin confirmación |

---

## Métricas por componente

### RAG — Recuperación

| Métrica | Descripción | Herramienta |
|---|---|---|
| Recall@5 | ¿Se recupera la cláusula relevante entre los top-5? | Evaluación manual / RAGAS |
| MRR (Mean Reciprocal Rank) | Posición promedio del fragmento correcto | RAGAS |
| Faithfulness | ¿La respuesta se apoya en los fragmentos recuperados? | RAGAS |
| Citation precision | ¿La cita realmente respalda la afirmación? | Evaluación manual |
| Abstention rate | ¿El sistema se abstiene cuando no hay evidencia? | Test cases sintéticos |

### Clasificación de reclamos

| Métrica | Descripción |
|---|---|
| Macro-F1 | Calidad por categoría, incluso clases minoritarias |
| Accuracy por campo extraído | Fecha, lugar, producto, descripción |
| Tasa de campos faltantes detectados | ¿Se identifican correctamente los datos incompletos? |

### Seguridad

| Métrica | Descripción |
|---|---|
| Tasa de prompt injection bloqueados | % de ataques del catálogo que el sistema rechaza |
| Tasa de acciones no autorizadas | % de tickets creados sin confirmación explícita |
| Tasa de PII en logs | PII detectada en los logs de prueba |
| Falsos positivos de abstención | % de consultas legítimas respondidas con abstención incorrecta |

### Sistema

| Métrica | Descripción |
|---|---|
| Latencia p50 / p95 | Tiempo de respuesta en percentiles |
| Tasa de errores | % de requests con error 5xx |
| Tool success rate | % de invocaciones de tools con resultado válido |

---

## Cómo correr la evaluación

```bash
# Evaluación completa desde línea de comandos
python evaluation/notebooks/correr_evaluacion.py

# O abrir en Google Colab:
# evaluation/notebooks/evaluacion_colab.ipynb → "Open in Colab"
```

Los resultados se guardan en `evaluation/results/` con timestamp de la corrida.

---

## Estructura de resultados

```
evaluation/results/
├── 2026-11-04_retrieval_eval.json
├── 2026-11-04_classification_eval.json
├── 2026-11-04_security_eval.json
├── figures/
│   ├── retrieval_recall_at_k.png
│   ├── confusion_matrix_claims.png
│   └── attack_block_rate.png
└── summary_2026-11-04.md
```

---

## Criterios de aprobación del MVP

| Componente | Umbral mínimo |
|---|---|
| Recall@5 (RAG) | ≥ 0.80 |
| Faithfulness (RAG) | ≥ 0.75 |
| Macro-F1 (clasificación) | ≥ 0.70 |
| Tasa de injection bloqueados | ≥ 0.90 |
| Tickets sin confirmación | 0 (tolerancia cero) |
