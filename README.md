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

## Estructura del proyecto

```
AI-ASSISTANT-INSURANCE/
│
├── README.md
├── pyproject.toml                   ← configuración del proyecto (uv)
├── requirements.txt                 ← dependencias
├── .env.example                     ← plantilla de variables de entorno
├── AI-ASSISTANT-INSURANCE-Agentic-RAG-Architecture.md
│
├── docs/                            ← entregables académicos
│   ├── index.md
│   ├── ficha.md                     ← entregable 1
│   ├── arquitectura.md              ← entregable 2 (diagrama Mermaid)
│   ├── modelo-de-amenazas.md        ← entregable 3
│   ├── priorizacion.md              ← entregable 4
│   ├── controles.md                 ← entregable 5
│   ├── evaluacion.md                ← entregable 6
│   └── regulatorio.md               ← entregable 7
│
├── src/
│   ├── agents/
│   │   ├── orchestrator.py          ← grafo LangGraph principal
│   │   ├── policy_agent.py          ← responde sobre coberturas (usa rag_tool)
│   │   └── support_agent.py         ← consulta datos del cliente (usa crm_tool)
│   │
│   ├── tools/
│   │   ├── crm_tool.py              ← Tool Calling hacia SQLite (AutoInsurance.csv)
│   │   └── rag_tool.py              ← Tool Calling hacia LanceDB (PDFs)
│   │
│   ├── rag/
│   │   ├── ingest.py                ← carga PDFs, genera chunks y los indexa en LanceDB
│   │   └── retriever.py             ← EnsembleRetriever: dense + BM25
│   │
│   ├── memory/
│   │   └── session.py               ← historial de conversación por session_id
│   │
│   ├── security/
│   │   ├── guardrails/
│   │   │   └── output_filter.py     ← filtra respuestas antes de entregar al usuario
│   │   └── validators/
│   │       └── input_validator.py   ← valida entrada, detecta injection, verifica customer_id
│   │
│   ├── schemas/
│   │   ├── customer.py              ← modelo Pydantic del cliente (campos del CSV)
│   │   └── query.py                 ← modelo de la consulta entrante
│   │
│   ├── prompts/
│   │   └── system_prompts.py        ← templates de prompts centralizados
│   │
│   └── config/
│       └── settings.py              ← variables de entorno y configuración global
│
├── data/
│   ├── raw/                         ← 3 PDFs sintéticos de Apex Shield Insurance
│   ├── synthetic/structured/
│   │   └── AutoInsurance.csv        ← dataset Kaggle. CRM simulado
│   └── vectorstore/                 ← índice LanceDB persistido (generado en runtime)
│
├── evaluation/
│   ├── catalog/                     ← consultas legítimas + ataques (JSONL)
│   ├── results/                     ← métricas y gráficos por corrida
│   └── notebooks/                   ← evaluacion_colab.ipynb
│
├── logs/
│   └── attack_runs/                 ← registros de corridas de seguridad
│
├── tests/                           ← tests del sistema
│
└── scripts/
    ├── index_documents.py           ← indexa los PDFs en LanceDB
    └── run_assistant.py             ← CLI interactivo del asistente
```

---

## Instalación y ejecución local

**Requisitos:** Python 3.11+ y [`uv`](https://docs.astral.sh/uv/)

```bash
# Instalar uv si no lo tienes
pip install uv
```

```bash
# 1. Clonar
git clone https://github.com/Ael-Dev/AI-ASSISTANT-INSURANCE.git
cd AI-ASSISTANT-INSURANCE

# 2. Entorno virtual
uv venv
source .venv/bin/activate        # Linux / macOS
# .venv\Scripts\activate         # Windows

# 3. Dependencias
uv pip install -r requirements.txt

# 4. Variables de entorno
cp .env.example .env
# Editar .env con tu OPENAI_API_KEY

# 5. Indexar PDFs en LanceDB (primera vez)
python scripts/index_documents.py

# 6. Correr el asistente (CLI)
python scripts/run_assistant.py

# 7. Evaluación
python evaluation/notebooks/correr_evaluacion.py

# 8. Tests
pytest tests/ -v
```

---

## Variables de entorno

| Variable | Descripción |
|---|---|
| `OPENAI_API_KEY` | API key del LLM |
| `OPENAI_MODEL` | Modelo (default: `gpt-4o-mini`) |
| `CHROMA_PERSIST_DIR` | Directorio del vector store (default: `./data/vectorstore`) |
| `SQLITE_DB_PATH` | Ruta de la BD SQLite con el CRM simulado |
| `MEMORY_BACKEND` | `sqlite` / `in_memory` |
| `LOG_LEVEL` | Nivel de logs (`INFO` / `DEBUG`) |

---

## Stack tecnológico

| Capa | Tecnología |
|---|---|
| Orquestación | LangGraph |
| Framework LLM | LangChain |
| LLM | OpenAI / modelo compatible |
| Embeddings | BGE-M3 o equivalente |
| Vector Store (RAG) | LanceDB |
| BD estructurada (CRM) | SQLite cargado desde `AutoInsurance.csv` |
| Retrieval híbrido | Dense + BM25 (EnsembleRetriever) |
| Memoria | SQLite + LangChain |
| Guardrails | Presidio + validators propios |
| Trazabilidad | Logs estructurados locales |
| Gestor de paquetes | uv |

---

## Nota sobre los datos

Los PDFs en `data/raw/` son documentos **sintéticos** de una aseguradora ficticia (*Apex Shield Insurance*).
El CSV `AutoInsurance.csv` es el [Auto Insurance Dataset de Kaggle](https://www.kaggle.com/), usado como CRM simulado. No contiene datos personales reales.
