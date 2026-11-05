# Planificación del Equipo — AI Assistant Insurance

Equipo de 4 personas · Proyecto Agentic RAG  
Referencia de arquitectura: [`AI-ASSISTANT-INSURANCE-Agentic-RAG-Architecture.md`](AI-ASSISTANT-INSURANCE-Agentic-RAG-Architecture.md)

---

## Roles del equipo

| Persona | Rol | Área principal |
|---|---|---|
| **P1** | RAG Engineer | Pipeline de ingestión, embeddings, retrieval híbrido y datos sintéticos |
| **P2** | Agent Engineer | Agentes LangGraph, orquestador, tools y memoria |
| **P3** | Security Engineer | Guardrails, validadores, modelo de amenazas y controles |
| **P4** | Evaluation & API Engineer | FastAPI, evaluación RAGAS, datasets y entregables académicos |

> Los roles son orientativos. En un equipo pequeño cada persona puede contribuir fuera de su área principal.

---

## Dependencias entre módulos

```
[P1] Datos sintéticos ──────────────────────────────────────────────────────────┐
[P1] RAG Pipeline (ingestión + vectorstore) ────────────────────────────────────┤
                                                                                  ↓
[P2] Policy Assistant Agent ──── depende de ──── RAG Pipeline (P1)             [P4] Evaluación RAG
[P2] Claims Classifier Agent                                                     ↑
[P2] Ticket Manager Agent                                                        │
[P2] Orchestrator (LangGraph) ── depende de ──── todos los agentes (P2)        │
[P2] Memory / Workflow State                                                     │
        │                                                                        │
        └──────── [P3] Guardrails se integran sobre los agentes (P2) ───────────┘
                                                                                  │
[P4] FastAPI ──── depende de ──── Orchestrator (P2) + Guardrails (P3) ─────────┘
[P4] Datasets de evaluación ─── dependen de ─── RAG (P1) + Agentes (P2)
```

---

## Historias de usuario

### HU-01 — Reportar un incidente en lenguaje natural

> **Como** asegurado, **quiero** describir un accidente con mis palabras **para que** el sistema identifique el tipo de siniestro y recopile los datos necesarios.

**Criterios de aceptación:**
- El sistema clasifica el reclamo con categoría y nivel de confianza
- Si faltan datos obligatorios, pregunta por ellos
- Los datos extraídos se validan contra un esquema Pydantic

**Responsable:** P2 (agente) + P1 (datos sintéticos de reclamos)  
**Dependencias:** HU-04 (datos sintéticos)

---

### HU-02 — Consultar cobertura de una póliza

> **Como** asegurado, **quiero** preguntar qué cubre mi póliza en lenguaje natural **para que** el sistema me responda con evidencia del documento y cite la fuente.

**Criterios de aceptación:**
- La respuesta incluye el nombre del documento, sección y página cuando están disponibles
- Si no hay evidencia suficiente, el sistema se abstiene explícitamente
- La respuesta no inventa coberturas ausentes del documento

**Responsable:** P1 (RAG) + P2 (Policy Assistant Agent)  
**Dependencias:** HU-05 (pipeline RAG), HU-04 (documentos sintéticos de pólizas)

---

### HU-03 — Registrar un reclamo como ticket

> **Como** asegurado, **quiero** que el sistema registre mi reclamo como ticket **para que** pueda hacer seguimiento con un identificador único.

**Criterios de aceptación:**
- El ticket solo se crea después de confirmación explícita del usuario
- El sistema devuelve un `ticket_id` y estado inicial
- El usuario puede consultar el ticket por su ID en sesiones posteriores
- No se crean tickets duplicados para el mismo incidente

**Responsable:** P2 (Ticket Agent + Orchestrator)  
**Dependencias:** HU-01 (clasificación), HU-08 (memoria de sesión)

---

### HU-04 — Datos sintéticos del dominio

> **Como** desarrollador, **quiero** un conjunto de datos ficticios coherentes **para que** el sistema pueda demostrar todas sus capacidades sin datos reales.

**Criterios de aceptación:**
- `data/synthetic/policies.json` — mínimo 5 pólizas (2 auto, 2 hogar, 1 salud)
- `data/synthetic/claims.json` — mínimo 10 reclamos ficticios de distintos tipos
- `data/synthetic/tickets.json` — mínimo 5 tickets en distintos estados
- `data/synthetic/claim_categories.json` — catálogo completo con requisitos por categoría
- Documentos PDF/DOCX/MD sintéticos en `data/raw/policies/` y `data/raw/procedures/`
- Ningún dato real de personas; marcados claramente como `DEMO`

**Responsable:** P1  
**Dependencias:** ninguna (primer paso del proyecto)

---

### HU-05 — Pipeline RAG híbrido

> **Como** desarrollador, **quiero** un pipeline de ingestión e indexado que procese documentos de pólizas **para que** el retriever pueda recuperar fragmentos relevantes con citas.

**Criterios de aceptación:**
- Script `scripts/index_documents.py` procesa todos los documentos en `data/raw/`
- Chunking respeta secciones y cláusulas (sin partir una exclusión de su contexto)
- Cada chunk incluye metadatos: `document_id`, `section`, `page`, `product`, `version`
- EnsembleRetriever combina ChromaDB (dense) + BM25 (sparse)
- Recall@5 ≥ 0.80 sobre el dataset de evaluación de recuperación

**Responsable:** P1  
**Dependencias:** HU-04

---

### HU-06 — Orquestador multiagente con LangGraph

> **Como** desarrollador, **quiero** un orquestador central que enrute cada solicitud al agente correcto **para que** el flujo sea rastreable y recuperable.

**Criterios de aceptación:**
- El grafo LangGraph tiene nodos: `detect_intent` → `route` → `[classifier | policy | ticket]` → `compose_response`
- El estado del grafo persiste en SQLite entre pasos del mismo flujo
- Las rutas condicionales funcionan correctamente para los tres tipos de intención
- Todos los nodos están trazados en LangSmith

**Responsable:** P2  
**Dependencias:** HU-01, HU-02, HU-03, HU-08

---

### HU-07 — Escalamiento a revisión humana

> **Como** sistema, **quiero** derivar automáticamente los casos complejos o de alto riesgo **para que** no se tomen decisiones automáticas en situaciones ambiguas.

**Criterios de aceptación:**
- Escalamiento automático si confianza de clasificación < 0.6
- Escalamiento si el usuario menciona lesiones personales
- Escalamiento si hay contradicción entre versiones de póliza recuperadas
- La cola de escalamiento simulada (`data/synthetic/escalation_queue.json`) recibe el caso con contexto completo

**Responsable:** P2 (lógica del agente) + P3 (reglas de seguridad)  
**Dependencias:** HU-01, HU-06

---

### HU-08 — Memoria entre sesiones

> **Como** asegurado, **quiero** que el asistente recuerde el contexto de mi conversación **para que** no tenga que repetir información ya proporcionada.

**Criterios de aceptación:**
- El historial de conversación se persiste por `session_id` en SQLite
- El estado del workflow (campos recopilados, paso actual) se restaura correctamente al retomar una sesión
- Los datos sensibles no se guardan en memoria semántica

**Responsable:** P2  
**Dependencias:** ninguna (puede desarrollarse en paralelo)

---

### HU-09 — Guardrails de seguridad

> **Como** operador del sistema, **quiero** que las entradas y salidas pasen por controles de seguridad **para que** el sistema no ejecute acciones no autorizadas ni exponga información sensible.

**Criterios de aceptación:**
- Detección de patrones de prompt injection en la entrada del usuario
- Validación de ownership antes de ejecutar cualquier tool de lectura/escritura
- Anonimización de PII (Presidio) antes de escribir logs
- Límite de tokens por request configurado y activo
- Tasa de injection bloqueados ≥ 0.90 sobre el catálogo de ataques

**Responsable:** P3  
**Dependencias:** HU-05 (para injection via RAG), HU-06 (para validar tools)

---

### HU-10 — API REST con FastAPI

> **Como** desarrollador de frontend, **quiero** una API REST documentada **para que** se pueda integrar una interfaz de chat.

**Criterios de aceptación:**
- `POST /chat` recibe `{session_id, message}` y devuelve `{response, sources, ticket_id?}`
- `GET /tickets/{ticket_id}` consulta el estado de un ticket
- `GET /health` devuelve estado del sistema
- Documentación Swagger disponible en `/docs`
- Rate limiting activo

**Responsable:** P4  
**Dependencias:** HU-06 (orquestador), HU-09 (guardrails)

---

### HU-11 — Evaluación del sistema

> **Como** equipo, **queremos** medir el rendimiento del sistema con métricas objetivas **para que** podamos demostrar que cumple los criterios de aceptación.

**Criterios de aceptación:**
- Dataset de consultas legítimas con ground truth en `evaluation/catalog/`
- Catálogo de ataques en `evaluation/catalog/`
- Notebook `evaluation/notebooks/evaluacion_colab.ipynb` que se puede abrir y ejecutar en Colab
- Resultados en `evaluation/results/` con métricas de RAG, clasificación y seguridad
- Gráficos exportados (confusion matrix, recall@k, attack block rate)

**Responsable:** P4  
**Dependencias:** HU-05 (RAG), HU-01 (clasificador), HU-09 (seguridad)

---

### HU-12 — Documentación y entregables académicos

> **Como** equipo, **queremos** entregar los documentos académicos requeridos **para que** el proyecto cumpla con los requisitos del curso.

**Criterios de aceptación:**
- `docs/ficha.md` completo con datos del equipo
- `docs/arquitectura.md` con diagrama Mermaid actualizado
- `docs/modelo-de-amenazas.md` con al menos 5 amenazas STRIDE
- `docs/priorizacion.md` con matriz de riesgo
- `docs/controles.md` con implementación real referenciada
- `docs/evaluacion.md` con resultados de la corrida final
- `docs/regulatorio.md` con marco aplicable

**Responsable:** P4 (coordinación) + todos  
**Dependencias:** todos los módulos implementados

---

## Cronograma sugerido

```
Semana 1  ─── P1: HU-04 (datos sintéticos) + inicio HU-05
          ─── P2: HU-08 (memoria) + setup LangGraph
          ─── P3: HU-12 parcial (ficha, arquitectura, amenazas)
          ─── P4: Setup proyecto, .env, CI, estructura de evaluación

Semana 2  ─── P1: HU-05 completado (RAG pipeline + indexado)
          ─── P2: HU-01 (clasificador) + HU-03 (ticket agent)
          ─── P3: HU-09 inicio (validators + prompt injection)
          ─── P4: HU-11 datasets + HU-10 inicio API

Semana 3  ─── P1: Soporte a P2 + optimización retrieval
          ─── P2: HU-02 (policy assistant) + HU-06 (orquestador)
          ─── P3: HU-09 completo + HU-07 (escalamiento)
          ─── P4: HU-10 completo + inicio evaluación

Semana 4  ─── P1: Evaluación RAG + ajuste chunking
          ─── P2: HU-07 completo + integración final
          ─── P3: Tests de seguridad + HU-12 parcial
          ─── P4: HU-11 completo + HU-12 completo

Semana 5  ─── Todo el equipo: integración, demo, presentación
```

---

## Tablero de tareas resumido

| Historia | P1 | P2 | P3 | P4 | Estado |
|---|---|---|---|---|---|
| HU-04 Datos sintéticos | 🔵 Lead | | | | ⬜ |
| HU-05 RAG Pipeline | 🔵 Lead | | | | ⬜ |
| HU-01 Clasificador | | 🔵 Lead | | | ⬜ |
| HU-02 Policy Assistant | 🟡 Apoyo | 🔵 Lead | | | ⬜ |
| HU-03 Ticket Agent | | 🔵 Lead | | | ⬜ |
| HU-06 Orquestador | | 🔵 Lead | | | ⬜ |
| HU-07 Escalamiento | | 🔵 Lead | 🟡 Apoyo | | ⬜ |
| HU-08 Memoria | | 🔵 Lead | | | ⬜ |
| HU-09 Guardrails | | 🟡 Apoyo | 🔵 Lead | | ⬜ |
| HU-10 API FastAPI | | | | 🔵 Lead | ⬜ |
| HU-11 Evaluación | 🟡 Apoyo | | 🟡 Apoyo | 🔵 Lead | ⬜ |
| HU-12 Documentación | | | | 🔵 Lead | ⬜ |

🔵 Lead = responsable principal · 🟡 Apoyo = contribuye · ⬜ Pendiente · ✅ Completado
