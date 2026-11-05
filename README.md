# AI Assistant Insurance — Agentic RAG

Asistente inteligente para el sector seguros construido sobre una arquitectura **Agentic RAG** con LangChain y LangGraph.  
Combina recuperación híbrida de documentos de pólizas, agentes especializados con herramientas, y memoria persistente entre sesiones.

> Proyecto académico · Universidad  
> Arquitectura completa: [`AI-ASSISTANT-INSURANCE-Agentic-RAG-Architecture.md`](AI-ASSISTANT-INSURANCE-Agentic-RAG-Architecture.md)  
> Documentación: [`docs/index.md`](docs/index.md)  
> Plan de trabajo en equipo: [`PLANIFICACION-EQUIPO.md`](PLANIFICACION-EQUIPO.md)

---

## ¿Qué hace este sistema?

| Capacidad | Descripción |
|---|---|
| **RAG Híbrido** | Recupera contexto de pólizas, coberturas y normativa usando BM25 + embeddings densos |
| **Agentes con herramientas** | Orchestrator → Claims Classifier → Policy Assistant → Ticket Agent, cada uno con tools Python |
| **Memoria entre sesiones** | Estado de conversación y workflow persistidos por `session_id` en SQLite |
| **Seguridad / Guardrails** | Validación de I/O, detección de prompt injection, anonimización de PII en logs |

---

## Estructura del proyecto

```
AI-ASSISTANT-INSURANCE/
│
├── README.md                              ← este archivo
├── pyproject.toml                         ← configuración del proyecto (uv)
├── requirements.txt                       ← dependencias exportadas
├── .env.example                           ← plantilla de variables de entorno
├── AI-ASSISTANT-INSURANCE-Agentic-RAG-Architecture.md  ← diseño completo
├── PLANIFICACION-EQUIPO.md                ← historias de usuario y plan de 4 personas
│
├── docs/                                  ← documentación y entregables académicos
│   ├── index.md                           ← portada
│   ├── ficha.md                           ← entregable 1 — ficha del proyecto
│   ├── arquitectura.md                    ← entregable 2 — diagrama Mermaid
│   ├── modelo-de-amenazas.md              ← entregable 3 — threat model
│   ├── priorizacion.md                    ← entregable 4 — priorización de controles
│   ├── controles.md                       ← entregable 5 — controles implementados
│   ├── evaluacion.md                      ← entregable 6 — evaluación del sistema
│   └── regulatorio.md                     ← entregable 7 — marco regulatorio
│
├── src/                                   ← código fuente del producto
│   ├── config/                            ← settings y variables centralizadas
│   ├── schemas/                           ← modelos Pydantic (Claim, Policy, Ticket)
│   │
│   ├── rag/                               ← pipeline RAG completo
│   │   ├── data_ingestion/                ← carga de PDFs, DOCX y Markdown
│   │   ├── embeddings/                    ← modelo de embeddings
│   │   ├── vectorstore/                   ← conexión ChromaDB
│   │   └── retrieval/                     ← retrieval híbrido (dense + BM25)
│   │
│   ├── agents/                            ← agentes LangGraph
│   │   ├── orchestrator.py                ← agente orquestador principal
│   │   ├── claims_classifier.py           ← clasifica y extrae entidades del reclamo
│   │   ├── policy_assistant.py            ← responde consultas con RAG + citas
│   │   └── ticket_manager.py              ← crea y consulta tickets con confirmación
│   │
│   ├── tools/                             ← herramientas que invocan los agentes
│   │   ├── claims_tools.py                ← classify_claim, extract_entities, validate_policy
│   │   ├── policy_tools.py                ← search_policy_documents, get_policy_metadata
│   │   └── ticket_tools.py                ← create_ticket, get_ticket_status, escalate
│   │
│   ├── chains/                            ← chains LangChain reutilizables
│   ├── prompts/                           ← templates de prompts centralizados
│   │
│   ├── memory/                            ← memoria y estado de sesión
│   │   ├── session_store.py               ← historial de conversación por session_id
│   │   └── workflow_state.py              ← estado del flujo agentic (SQLite)
│   │
│   ├── services/                          ← lógica de negocio desacoplada de los agentes
│   │   ├── policy_service.py
│   │   └── ticket_service.py
│   │
│   ├── mcp_servers/                       ← servidores MCP (segunda iteración)
│   │   ├── policy_server.py               ← MCP: search_policy, get_policy_details
│   │   └── ticket_server.py               ← MCP: create_ticket, get_ticket, escalate
│   │
│   ├── security/                          ← seguridad del sistema
│   │   ├── guardrails/                    ← validación de I/O, filtros de salida
│   │   └── validators/                    ← validadores de entrada, anti-injection
│   │
│   └── api/                               ← capa API con FastAPI
│       └── main.py
│
├── data/
│   ├── raw/                               ← documentos originales (NO datos reales)
│   │   ├── policies/                      ← PDFs/DOCX de pólizas sintéticas
│   │   └── procedures/                    ← manuales de reclamos y matrices de requisitos
│   ├── processed/                         ← documentos chunkeados y normalizados
│   ├── synthetic/                         ← JSON con clientes, pólizas, reclamos y tickets ficticios
│   └── vectorstore/                       ← índice ChromaDB persistido
│
├── evaluation/
│   ├── catalog/                           ← ataques y consultas legítimas (CSV / JSONL)
│   ├── results/                           ← JSON y gráficos de cada corrida (versionados)
│   └── notebooks/                         ← correr_evaluacion.ipynb (abre en Colab)
│
├── logs/
│   └── attack_runs/                       ← muestra de registros de corridas de ataque
│
├── tests/
│   ├── unit/                              ← tests por módulo
│   └── integration/                       ← tests end-to-end del flujo agentic
│
├── scripts/                               ← utilidades de ingesta e indexado
└── .github/
    └── workflows/                         ← CI/CD pipelines
```

---

## Instalación y ejecución local

### Requisitos

- Python 3.11+
- [`uv`](https://docs.astral.sh/uv/) — gestor de entornos y paquetes

```bash
# Instalar uv
pip install uv
```

### Pasos

```bash
# 1. Clonar
git clone https://github.com/Ael-Dev/AI-ASSISTANT-INSURANCE.git
cd AI-ASSISTANT-INSURANCE

# 2. Crear entorno virtual
uv venv
source .venv/bin/activate          # Linux / macOS
# .venv\Scripts\activate           # Windows

# 3. Instalar dependencias
uv pip install -r requirements.txt

# Dependencias de desarrollo (opcional)
uv pip install -r requirements-dev.txt

# 4. Configurar variables de entorno
cp .env.example .env
# Editar .env con tu OPENAI_API_KEY y LANGSMITH_API_KEY

# 5. Indexar documentos (primera vez)
python scripts/index_documents.py

# 6. Correr la API
uvicorn src.api.main:app --reload --port 8000

# 7. Modo CLI interactivo
python scripts/run_assistant.py

# 8. Correr evaluaciones
python evaluation/notebooks/correr_evaluacion.py

# 9. Tests
pytest tests/ -v
```

---

## Variables de entorno

| Variable | Descripción |
|---|---|
| `OPENAI_API_KEY` | API key del LLM |
| `OPENAI_MODEL` | Modelo a usar (default: `gpt-4o-mini`) |
| `LANGCHAIN_API_KEY` | LangSmith — trazabilidad |
| `LANGCHAIN_PROJECT` | Nombre del proyecto en LangSmith |
| `CHROMA_PERSIST_DIR` | Carpeta donde persiste el vector store |
| `MEMORY_BACKEND` | `sqlite` / `redis` / `in_memory` |

Ver `.env.example` para la lista completa.

---

## Stack tecnológico

| Capa | Tecnología |
|---|---|
| Orquestación de agentes | LangGraph |
| Framework LLM | LangChain |
| LLM | OpenAI GPT-4o-mini (o compatible) |
| Embeddings | `text-embedding-3-small` / BGE-M3 |
| Vector Store | ChromaDB |
| Retrieval híbrido | ChromaDB + BM25 (EnsembleRetriever) |
| Memoria | SQLite + LangChain ConversationSummaryBufferMemory |
| API | FastAPI |
| Guardrails / PII | Presidio + custom validators |
| Trazabilidad | LangSmith |
| Gestor de paquetes | uv |

---

## Datos sintéticos

**Ningún dato real de personas, pólizas o siniestros está incluido en este repositorio.**  
Todos los registros en `data/synthetic/` son ficticios y sirven únicamente para demostrar la arquitectura.

---

## Equipo

Proyecto de 4 personas — ver [`PLANIFICACION-EQUIPO.md`](PLANIFICACION-EQUIPO.md) para roles, historias de usuario y dependencias.

---

## Licencia

MIT
