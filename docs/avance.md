# Avance del proyecto

Estado de la implementación por etapas del plan.

| Etapa | Contenido | Estado |
|---|---|---|
| 1 Fundación | Configuración, esquemas, ingesta de CRM y base de conocimiento | Implementada en la rama feature/p1-foundation |
| 2 RAG y CRM | Retriever híbrido y rag_tool implementados. Falta CRM y memoria de sesión | En progreso |
| 3 Agentes y seguridad | Policy agent implementado. Faltan orquestador, validadores y evaluación | En progreso |
| 4 Integración | Prueba de punta a punta y demo | Pendiente |

## Etapa 1 Fundación

### Modelos intercambiables

Cada rol tiene su propio modelo y se cambia solo por variables de entorno. Los roles son llm, judge y embedding.

| Proveedor | Chat | Embeddings |
|---|---|---|
| ollama | Si | Si |
| openrouter | Si | Si |
| google_genai | Si | Si |
| xai | Si | No |
| anthropic | Si | No |

```bash
# Local
LLM_PROVIDER=ollama
LLM_NAME=qwen3:8b

# De pago
LLM_PROVIDER=anthropic
LLM_NAME=claude-sonnet-5-5
```

### Flujo de ingesta

Son dos scripts independientes. index_crm.py carga SQLite e index_knowledge_base.py construye los embeddings.

```mermaid
flowchart LR
    CSV[AutoInsurance.csv] --> VAL[Validación Pydantic] --> SQL[(SQLite CRM)]
    PDF[PDFs Apex Shield] --> MD[MarkItDown a Markdown] --> CH[Chunks] --> EMB[Embeddings] --> VEC[(LanceDB)]
```

### Cómo ejecutarlo

```bash
uv sync
cp .env.example .env
ollama pull bge-m3
uv run python scripts/index_crm.py
uv run python scripts/index_knowledge_base.py
uv run pytest
```

### Resultados de la primera ejecución

| Medida | Valor |
|---|---|
| Clientes cargados en SQLite | 9133 |
| Filas descartadas por validación | 2 |
| PDFs convertidos a Markdown | 3 |
| Chunks indexados en LanceDB | 132 |
| Pruebas automáticas | 6 aprobadas |

## Etapa 2 RAG

La base vectorial es LanceDB, local y sin servidor. Todo vive en las carpetas originales del proyecto.

| Archivo | Función |
|---|---|
| src/rag/ingest.py | Chunking y carga en LanceDB |
| src/rag/retriever.py | EnsembleRetriever con búsqueda semántica y BM25 |
| src/rag/reranker.py | Reranker local que ordena los candidatos |
| src/tools/rag_tool.py | Tool que devuelve fragmentos con la fuente para citar |

```mermaid
flowchart LR
    Q[Pregunta] --> D[Semántica LanceDB]
    Q --> B[BM25]
    D --> E[EnsembleRetriever]
    B --> E
    E --> R[Reranker]
    R --> T[rag_tool con citas]
```

Los pesos y la cantidad de fragmentos se cambian con DENSE_WEIGHT y BM25_WEIGHT. Los candidatos antes del reranking se definen con RETRIEVAL_CANDIDATES_K y los que se devuelven después con RERANK_TOP_K.

Reranker: jina-reranker-v2-base-multilingual, local, con 4 hilos de CPU para no competir con el LLM. Se eligió frente a bge-reranker-v2-m3 porque acertó igual en las pruebas y fue el doble de rápido.

Chunking: los títulos de los PDFs se recuperan como encabezados para que cada pregunta o subsección quede completa en un fragmento.

Nota técnica: la librería langchain-lancedb sobrescribe el metadato source, por eso el nombre del documento se guarda como document_name.

## Agente de políticas

| Archivo | Función |
|---|---|
| src/prompts/system_prompts.py | Prompt con secciones XML, separado del código |
| src/agents/policy_agent.py | Agente creado con create_agent de LangChain |
| scripts/ask_agent.py | Prueba del agente por terminal |

Separación de canales:

- El system prompt lleva solo reglas y formato.
- El usuario envía solo la pregunta.
- Los fragmentos llegan como resultado de la tool dentro de etiquetas source con id, document y section.
- El contenido de cada fragmento se escapa para que no pueda cerrar la etiqueta ni inyectar instrucciones.
- El prompt indica que lo que está dentro de source son datos no confiables.
