# Entregable 2: Arquitectura del Sistema

> Documento completo con diagramas y decisiones de diseño:  
> [`AI-ASSISTANT-INSURANCE-Agentic-RAG-Architecture.md`](https://github.com/Ael-Dev/AI-ASSISTANT-INSURANCE/blob/main/AI-ASSISTANT-INSURANCE-Agentic-RAG-Architecture.md)

---

## Descripción general

El sistema implementa una arquitectura **Agentic RAG** con un orquestador central (LangGraph) y dos agentes especializados, cada uno con su propia tool de acceso a datos:

| Agente | Tool | Fuente de datos |
|---|---|---|
| Support Agent | `crm_tool` | SQLite ← `AutoInsurance.csv` (CRM simulado) |
| Policy Agent | `rag_tool` | ChromaDB ← 3 PDFs operativos (RAG híbrido) |
| Orchestrator | `get_session_state` | SQLite (memoria de sesión) |

---

## Diagrama A: Arquitectura funcional

Vista limpia del sistema sin controles de seguridad. Para entender el flujo de datos.

```mermaid
flowchart TB
    U(["👤 Usuario / Cliente\n(ej: BU79786)"])
    UI["Chat UI / CLI"]
    ORCH["Orchestrator Agent\n(LangGraph)"]
    STATE[("Session State\nSQLite")]
    ROUTE{"¿Intención?"}

    SUPP["Support Agent"]
    POL["Policy Agent"]

    CRM_T["crm_tool\nTool Calling → SQL"]
    RAG_T["rag_tool\nTool Calling → ChromaDB"]

    SQLITE[("CRM Simulado\nAutoInsurance.csv → SQLite")]
    CHROMA[("Vector Store\nChromaDB")]
    PDFS[("PDFs Operativos\n3 docs Apex Shield")]

    MEM[("Memory\nHistorial por session_id")]
    RESP["Response Composer"]

    U --> UI
    UI --> ORCH
    ORCH <--> STATE
    ORCH <--> MEM
    ORCH --> ROUTE

    ROUTE -->|"Consulta cliente / póliza"| SUPP
    ROUTE -->|"Consulta cobertura / procedimiento"| POL
    ROUTE -->|"Consulta combinada"| SUPP & POL

    SUPP --> CRM_T
    CRM_T --> SQLITE

    POL --> RAG_T
    RAG_T --> CHROMA
    CHROMA -.->|"indexado"| PDFS

    SUPP --> RESP
    POL --> RESP
    RESP --> UI
    UI --> U
```

---

## Diagrama B: Arquitectura con controles de seguridad

Misma arquitectura con los puntos de riesgo y controles marcados en **rojo**.

```mermaid
flowchart TB
    U(["👤 Usuario / Cliente"])
    UI["Chat UI / CLI"]

    IV["🔴 Input Validator\nanti-injection · límite tokens\nverificación customer_id"]

    ORCH["Orchestrator Agent\n(LangGraph)"]
    STATE[("Session State\nSQLite")]
    ROUTE{"¿Intención?"}

    SUPP["Support Agent"]
    POL["Policy Agent"]

    CRM_T["crm_tool\nTool Calling → SQL"]
    RAG_T["rag_tool\nTool Calling → ChromaDB"]

    OWN["🔴 Ownership Check\nvalidar customer_id\nde sesión vs BD"]

    CTX["🔴 Context Injection Risk\nfragmentos RAG tratados\ncomo datos, no instrucciones"]

    SQLITE[("CRM Simulado\nAutoInsurance.csv → SQLite")]
    CHROMA[("Vector Store\nChromaDB")]
    PDFS[("PDFs Operativos\n3 docs Apex Shield")]

    MEM[("Memory\nHistorial por session_id")]

    OF["🔴 Output Filter / DLP\nenmascarar PII\nno revelar datos de otros clientes"]

    LOG["🔴 Logs + Trazas\nlogs estructurados locales · sin PII\nsin API keys"]

    RESP["Response Composer"]
    HIT["🔴 Human-in-the-loop\nescalamiento si\nbaja confianza / caso ambiguo"]

    U --> UI
    UI --> IV
    IV -->|"✅ pasa"| ORCH
    IV -->|"❌ rechazada"| UI

    ORCH <--> STATE
    ORCH <--> MEM
    ORCH --> ROUTE

    ROUTE -->|"Consulta cliente"| SUPP
    ROUTE -->|"Consulta cobertura"| POL
    ROUTE -->|"Combinada"| SUPP & POL

    SUPP --> OWN
    OWN -->|"✅ autorizado"| CRM_T
    OWN -->|"❌ denegado"| RESP
    CRM_T --> SQLITE

    POL --> CTX
    CTX --> RAG_T
    RAG_T --> CHROMA
    CHROMA -.->|"indexado"| PDFS

    SUPP --> OF
    POL --> OF
    OF --> RESP
    RESP --> UI
    UI --> U

    OF --> LOG
    ORCH --> LOG
    ORCH --> HIT

    style IV fill:#c0392b,color:#fff,stroke:#922b21
    style OWN fill:#c0392b,color:#fff,stroke:#922b21
    style CTX fill:#c0392b,color:#fff,stroke:#922b21
    style OF fill:#c0392b,color:#fff,stroke:#922b21
    style LOG fill:#c0392b,color:#fff,stroke:#922b21
    style HIT fill:#c0392b,color:#fff,stroke:#922b21
```

---

## Puntos de control de seguridad

| Nodo | Amenaza que mitiga | Módulo |
|---|---|---|
| Input Validator | Prompt injection, DoS por tokens, customer_id inválido | `src/security/validators/input_validator.py` |
| Ownership Check | Acceso a datos de otro cliente | `src/tools/crm_tool.py` |
| Context Injection Risk | Prompt injection via fragmentos RAG | `src/rag/retriever.py` + estructura de prompt |
| Output Filter / DLP | PII en respuesta, datos cruzados, alucinaciones | `src/security/guardrails/output_filter.py` |
| Logs sin PII | Privacidad en trazas y logs | `src/config/settings.py` + logs estructurados locales |
| Human-in-the-loop | Decisiones automáticas en casos ambiguos | `src/agents/orchestrator.py` |

Ver análisis completo en [`modelo-de-amenazas.md`](modelo-de-amenazas.md) y [`controles.md`](controles.md).

---

## Decisiones de diseño clave

- **Dos tools concretas** (`crm_tool` + `rag_tool`) en lugar de múltiples agentes complejos: simple, trazable y suficiente para el scope del proyecto.
- **SQLite como CRM**: el CSV de Kaggle se carga una vez. Las consultas SQL son deterministas, verificables y no dependen del LLM.
- **EnsembleRetriever**: combina búsqueda semántica (dense) + keyword (BM25) para mejor recall sin infraestructura adicional.
- **Ownership check en el backend**: la validación de pertenencia de recursos nunca la hace el LLM.
- **Separación datos/instrucciones**: fragmentos RAG siempre en sección `[CONTEXT]` delimitada, nunca mezclados con instrucciones del sistema.
