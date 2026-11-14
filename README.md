# AI Assistant Insurance: Agentic RAG

Asistente de soporte para una aseguradora de autos, construido como prototipo académico sobre arquitectura **Agentic RAG** con LangChain y LangGraph.

> Proyecto académico · Curso de Ciberseguridad en IA
> Diseño del sistema: [`AI-ASSISTANT-INSURANCE-Agentic-RAG-Architecture.md`](AI-ASSISTANT-INSURANCE-Agentic-RAG-Architecture.md)
> Documentación: [`docs/index.md`](docs/index.md)

---

## ¿Qué hace?

Un usuario puede simular ser un cliente (ej. `BU79786`) y preguntarle al asistente sobre su póliza. El sistema combina dos fuentes de datos:

| Fuente | Tipo | Uso |
|---|---|---|
| `AutoInsurance.csv` (Kaggle) | Datos estructurados. CSV cargado en SQLite | CRM simulado: consultar póliza, quejas abiertas, cobertura y tipo de vehículo por `Customer ID` |
| PDFs operativos (Apex Shield Insurance) | Datos no estructurados. Indexados en LanceDB | RAG: responder preguntas sobre procesos, coberturas y procedimientos de reclamos |

El agente decide qué fuente consultar según la pregunta, usando **Tool Calling**.

---

## Capacidades del sistema

| Componente | Descripción |
|---|---|
| **RAG Híbrido** | Recuperación de FAQs y manuales operativos via dense search + BM25 |
| **Tool Calling sobre SQLite** | El agente consulta el CRM simulado (`AutoInsurance.csv`) para datos del cliente en tiempo real |
| **Agentes especializados** | Orchestrator, Policy Agent y Support Agent orquestados con LangGraph |
| **Memoria de sesión** | Estado de la conversación persistido por `session_id` |
| **Guardrails** | Validación de entrada/salida, control de acceso por cliente, anonimización de PII en logs |

---

## Datos

```
data/
├── raw/                          ← documentos PDF fuente del RAG
│   ├── Manual Completo de Manejo de Reclamaciones y FAQ...pdf
│   ├── Manual Operativo de Políticas y Procedimientos...pdf
│   └── Tabla de Costos y Procedimientos Operativos...pdf
│
└── synthetic/
    └── structured/
        └── AutoInsurance.csv     ← dataset Kaggle. CRM simulado (9.134 registros)
```

**`AutoInsurance.csv`: columnas clave que usa el agente:**

| Campo | Descripción |
|---|---|
| `Customer` | ID del cliente (ej. `BU79786`) |
| `Policy Type` / `Policy` | Tipo y nivel de póliza |
| `Coverage` | Cobertura (Basic / Extended / Premium) |
| `Number of Open Complaints` | Quejas activas del cliente |
| `Total Claim Amount` | Monto total de reclamos |
| `Vehicle Class` / `Vehicle Size` | Tipo de vehículo asegurado |
| `Customer Lifetime Value` | Valor del cliente |

---

## Estado

| Etapa | Estado |
|---|---|
| 1 Fundación: configuración, esquemas, ingesta | Hecha |
| 2 RAG con reranker | Hecha |
| 2 CRM tool y memoria de sesión | Pendiente |
| 3 Agentes, prompts, FastAPI y seguridad | Pendiente |
| 4 Integración y demo | Pendiente |

---

## Estructura del proyecto

Ver el detalle en la sección 11 del [documento de arquitectura](AI-ASSISTANT-INSURANCE-Agentic-RAG-Architecture.md). Resumen:

```
src/config/     ← settings y fábrica de modelos
src/schemas/    ← esquemas Pydantic
src/rag/        ← conversión, chunking, retriever y reranker
src/tools/      ← crm_loader y rag_tool
scripts/        ← ingesta y pruebas por terminal
tests/          ← pruebas automáticas
docs/           ← documentación publicada con MkDocs
```

---

## Instalación y ejecución local

Requisitos: Python 3.12 o superior, [uv](https://docs.astral.sh/uv/) y [Ollama](https://ollama.com)

```bash
# 1. Dependencias
uv sync

# 2. Variables de entorno
cp .env.example .env

# 3. Modelo de embeddings local
ollama pull bge-m3

# 4. Ingesta: CSV a SQLite y PDFs a LanceDB
uv run python scripts/index_documents.py

# 5. Probar el RAG y el CRM
uv run python scripts/ask_rag.py "¿Cuánto cuesta la grúa por kilómetro adicional?"
uv run python scripts/query_crm.py BU79786

# 6. Pruebas
uv run pytest

# 7. Documentación local
uv run --group docs mkdocs serve
```

---

## Variables de entorno

Los modelos se cambian solo con variables. Proveedores: `ollama`, `openrouter`, `google_genai`, `xai`, `anthropic`. Embeddings admite `ollama`, `google_genai` y `openrouter`.

| Variable | Descripción |
|---|---|
| `LLM_PROVIDER`, `LLM_NAME` | Modelo principal |
| `JUDGE_PROVIDER`, `JUDGE_NAME` | Modelo juez |
| `EMBEDDING_PROVIDER`, `EMBEDDING_NAME` | Modelo de embeddings |
| `CHUNK_SIZE`, `CHUNK_OVERLAP` | Tamaño y solape de los chunks. Reindexar al cambiarlos |
| `RETRIEVAL_CANDIDATES_K` | Candidatos por método antes del reranking |
| `RERANK_TOP_K` | Fragmentos devueltos después del reranking |
| `RERANK_ENABLED`, `RERANK_MODEL_NAME`, `RERANK_THREADS` | Configuración del reranker |
| `DENSE_WEIGHT`, `BM25_WEIGHT` | Peso de cada método de búsqueda |
| `OLLAMA_BASE_URL` | Dirección del servidor Ollama |
| `OPENROUTER_API_KEY`, `GOOGLE_API_KEY`, `XAI_API_KEY`, `ANTHROPIC_API_KEY` | Llave del proveedor que se use |

---

## Stack tecnológico

| Capa | Tecnología |
|---|---|
| Orquestación | LangGraph |
| Framework LLM | LangChain |
| LLM y juez | Intercambiable: Ollama, OpenRouter, Gemini, Grok o Claude |
| Embeddings | Ollama con bge-m3 |
| Reranker | jina-reranker-v2-base-multilingual con fastembed |
| Vector store | LanceDB |
| CRM | SQLite cargado desde `AutoInsurance.csv` |
| Conversión de PDF | MarkItDown |
| Retrieval híbrido | Dense + BM25 con EnsembleRetriever |
| API | FastAPI (pendiente) |
| Guardrails | Presidio y validators propios (pendiente) |
| Gestor de paquetes | uv |

---

## Nota sobre los datos

Los PDFs en `data/raw/` son documentos **sintéticos** de una aseguradora ficticia (*Apex Shield Insurance*).
El CSV `AutoInsurance.csv` es el [Auto Insurance Dataset de Kaggle](https://www.kaggle.com/), usado como CRM simulado. No contiene datos personales reales.
