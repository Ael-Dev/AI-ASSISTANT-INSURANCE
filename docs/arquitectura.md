# Entregable 2 — Arquitectura del Sistema

> El diagrama completo y la descripción detallada están en  
> [`AI-ASSISTANT-INSURANCE-Agentic-RAG-Architecture.md`](../AI-ASSISTANT-INSURANCE-Agentic-RAG-Architecture.md)  
> Este documento es el entregable académico resumido.

---

## Descripción general

El sistema implementa una arquitectura **Agentic RAG multiagente** con un orquestador central (LangGraph) que enruta solicitudes a agentes especializados. Cada agente tiene acceso a herramientas Python específicas y comparten un estado de conversación persistido.

## Componentes principales

| Componente | Tecnología | Responsabilidad |
|---|---|---|
| Orchestrator Agent | LangGraph | Detecta intención, enruta y coordina el flujo |
| Claims Classifier Agent | LangChain + Pydantic | Clasifica siniestros y extrae entidades |
| Policy Assistant Agent | LangChain + ChromaDB | Responde consultas con RAG + citas |
| Ticket Management Agent | LangChain + SQLite | Crea y consulta tickets con confirmación |
| Policy RAG Pipeline | BM25 + Embeddings | Recuperación híbrida de documentos |
| Memory Store | SQLite / Redis | Estado de sesión y workflow |
| Guardrails | Presidio + validators | Seguridad de I/O |
| API | FastAPI | Capa de acceso al sistema |

## Diagrama de arquitectura

```mermaid
flowchart TB
    U["Usuario / Asegurado"] --> UI["Chat UI / API"]
    UI --> ORCH["Orchestrator Agent\n(LangGraph)"]
    ORCH <--> STATE[("Conversation State\nSQLite / Redis")]

    ORCH --> ROUTE{"Intención detectada"}
    ROUTE -->|"Reportar incidente"| CLASS["Claims Classifier Agent"]
    ROUTE -->|"Consultar póliza"| POLICY["Policy Assistant Agent"]
    ROUTE -->|"Registrar / consultar ticket"| TICKET["Ticket Management Agent"]

    CLASS --> POLICY
    POLICY --> TICKET

    POLICY --> RETR["Policy RAG Pipeline\nDense + BM25"]
    RETR --> VDB[("ChromaDB")]
    RETR --> DOCS[("Documentos\nPDF / DOCX / MD")]

    TICKET --> TDB[("Tickets DB\nSQLite")]
    TICKET --> CONSENT{"Confirmación\ndel usuario"}
    CONSENT -->|"Sí"| CREATE["Crear Ticket"]
    CONSENT -->|"No"| DRAFT["Mantener borrador"]

    ORCH <--> MEM[("Memory Store\nSesión + Workflow")]
    ORCH --> GUARD["Guardrails / PII\nValidators"]
    GUARD --> OBS["Logs · LangSmith"]

    ORCH --> RESP["Response Composer"]
    RESP --> UI

    TICKET --> ESC{"¿Escalar?"}
    ESC -->|"Sí"| HUMAN["Cola de revisión\nhumana simulada"]
    ESC -->|"No"| RESP
```

## Flujo principal

```mermaid
sequenceDiagram
    actor User as Usuario
    participant O as Orchestrator
    participant C as Claims Classifier
    participant P as Policy Assistant
    participant T as Ticket Agent

    User->>O: Describe incidente
    O->>C: Clasificar y extraer entidades
    C-->>O: Categoría + campos extraídos
    O->>P: Consultar cobertura
    P-->>O: Respuesta con citas de póliza
    O-->>User: Explicación + preguntar si registrar
    User->>O: Confirma registro
    O->>T: Crear ticket
    T-->>O: ticket_id + estado
    O-->>User: Código de seguimiento
```

## Decisiones de diseño

- **Orquestador central** en lugar de agentes peer-to-peer sin control: permite auditar y trazar cada paso.
- **Un único RAG de pólizas** separado por metadatos: evita duplicación y facilita la evaluación.
- **SQLite para el MVP**: simple, sin infraestructura adicional; migrable a PostgreSQL en producción.
- **Confirmación explícita antes de crear tickets**: requisito de seguridad fundamental.
- **Human-in-the-loop**: casos ambiguos, alta incertidumbre o alto impacto escalan siempre.
