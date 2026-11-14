# Entregable 6: Evaluación del Sistema

## Estrategia

La evaluación cubre tres dimensiones: **recuperación RAG**, **consulta al CRM** y **seguridad**.  
Todos los datasets son sintéticos; no se usan datos personales reales.

---

## Datasets

| Dataset | Ubicación | Formato | Descripción |
|---|---|---|---|
| Consultas legítimas de cobertura | `evaluation/catalog/legitimate_queries.jsonl` | JSONL | Preguntas con ground truth de cobertura en los PDFs |
| Consultas legítimas de CRM | `evaluation/catalog/crm_queries.jsonl` | JSONL | Preguntas de cliente con respuesta esperada desde `AutoInsurance.csv` |
| Catálogo de ataques | `evaluation/catalog/attack_catalog.jsonl` | JSONL | Injections, acceso no autorizado (`customer_id` de otro cliente), DoS |

---

## Métricas por componente

### RAG: Policy Agent

| Métrica | Descripción |
|---|---|
| Recall@5 | ¿El fragmento correcto aparece en los top-5? |
| Faithfulness (RAGAS) | ¿La respuesta se apoya en los fragmentos recuperados? |
| Citation precision | ¿La cita (documento y sección) es correcta? |
| Abstention rate | ¿El agente se abstiene cuando no hay evidencia? |

### CRM: Support Agent

| Métrica | Descripción |
|---|---|
| Field accuracy | ¿Los valores devueltos coinciden con los del CSV? |
| Ownership enforcement | ¿El sistema rechaza siempre consultas de `customer_id` ajeno? |

### Seguridad

| Métrica | Descripción |
|---|---|
| Injection block rate | % de ataques del catálogo rechazados por el Input Validator |
| Unauthorized access rate | % de intentos de acceso a datos de otro cliente que el sistema bloquea |
| PII in response rate | PII detectada en respuestas de salida |

---

## Cómo correr la evaluación

```bash
# Desde línea de comandos
python evaluation/notebooks/correr_evaluacion.py

# O abrir en Colab:
# evaluation/notebooks/evaluacion_colab.ipynb → "Open in Colab"
```

---

## Criterios de aprobación del MVP

| Componente | Umbral mínimo |
|---|---|
| Recall@5 (RAG) | ≥ 0.80 |
| Faithfulness (RAG) | ≥ 0.75 |
| Ownership enforcement | 100% (tolerancia cero) |
| Injection block rate | ≥ 0.90 |
| Abstention rate (sin evidencia) | ≥ 0.90 |
