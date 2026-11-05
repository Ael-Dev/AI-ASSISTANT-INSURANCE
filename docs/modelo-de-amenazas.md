# Entregable 3 — Modelo de Amenazas

## Metodología

Se utiliza **STRIDE** aplicado a los componentes del sistema Agentic RAG, complementado con el framework **OWASP Top 10 for LLM Applications (2025)**.

---

## Superficies de ataque identificadas

| Superficie | Descripción |
|---|---|
| Entrada del usuario (chat) | Texto libre sin estructura que el LLM procesa directamente |
| Documentos recuperados (RAG) | Fragmentos de pólizas que se inyectan en el contexto del LLM |
| Herramientas (tools) | Funciones Python invocadas por el agente con argumentos generados por el LLM |
| Capa de memoria | Estado de conversación persistido por sesión |
| API FastAPI | Endpoint de acceso externo |
| Logs y trazas | Registros que pueden contener PII o datos sensibles |

---

## Amenazas STRIDE

### A1 — Prompt Injection (LLM01)

| Campo | Detalle |
|---|---|
| **Descripción** | El usuario o un documento recuperado contiene instrucciones que manipulan el comportamiento del LLM |
| **Vector** | Entrada de usuario / fragmentos RAG inyectados en el prompt |
| **Impacto** | El agente ejecuta acciones no autorizadas, revela información interna o ignora guardrails |
| **Probabilidad** | Alta |
| **Severidad** | Crítica |
| **Control** | Separar datos de instrucciones; validar salida del LLM antes de ejecutar tools; nunca ejecutar instrucciones provenientes de documentos recuperados |

### A2 — Acceso no autorizado a datos de otros clientes

| Campo | Detalle |
|---|---|
| **Descripción** | Un usuario consulta tickets o pólizas que no le pertenecen manipulando el `policy_id` o `ticket_id` |
| **Vector** | Parámetros de tools generados por el LLM sin validación backend |
| **Impacto** | Exposición de datos de otros asegurados |
| **Probabilidad** | Media |
| **Severidad** | Alta |
| **Control** | Validar autorización en el backend, nunca confiar en el LLM para verificar pertenencia de recursos |

### A3 — Exposición de PII en logs

| Campo | Detalle |
|---|---|
| **Descripción** | Datos personales ficticios o reales quedan registrados en logs o trazas de LangSmith |
| **Vector** | Pipeline de logging sin anonimización |
| **Impacto** | Violación de privacidad; incumplimiento regulatorio |
| **Probabilidad** | Media |
| **Severidad** | Media |
| **Control** | Aplicar Presidio antes de escribir logs; excluir campos sensibles de las trazas |

### A4 — Creación de tickets sin consentimiento (Insecure Output Handling — LLM02)

| Campo | Detalle |
|---|---|
| **Descripción** | El agente ejecuta `create_ticket` sin esperar confirmación explícita del usuario |
| **Vector** | Flujo agentic sin estado de confirmación obligatorio |
| **Impacto** | Tickets creados en nombre del usuario sin su aprobación |
| **Probabilidad** | Media |
| **Severidad** | Alta |
| **Control** | Estado de workflow `awaiting_confirmation` obligatorio antes de cualquier acción de escritura |

### A5 — Alucinación de coberturas (Excessive Agency — LLM08)

| Campo | Detalle |
|---|---|
| **Descripción** | El LLM afirma que una cobertura existe cuando no hay evidencia en los documentos recuperados |
| **Vector** | Respuesta sin grounding verificado |
| **Impacto** | El usuario toma decisiones basadas en información incorrecta |
| **Probabilidad** | Media |
| **Severidad** | Alta |
| **Control** | Verificar `evidence_sufficiency` antes de responder; abstención explícita cuando falta evidencia |

### A6 — Denegación de servicio por contexto saturado

| Campo | Detalle |
|---|---|
| **Descripción** | Un usuario envía entradas muy largas o repetidas que saturan la ventana de contexto o generan costos excesivos |
| **Vector** | API sin límites de tokens ni rate limiting |
| **Impacto** | Degradación del servicio; costos elevados |
| **Probabilidad** | Baja–Media |
| **Severidad** | Media |
| **Control** | Límite de tokens por request (`MAX_INPUT_TOKENS`); rate limiting en FastAPI |

---

## Matriz de riesgo

| Amenaza | Probabilidad | Impacto | Riesgo | Prioridad |
|---|---|---|---|---|
| A1 — Prompt injection | Alta | Crítico | **Crítico** | 1 |
| A2 — Acceso no autorizado | Media | Alto | **Alto** | 2 |
| A4 — Tickets sin consentimiento | Media | Alto | **Alto** | 2 |
| A5 — Alucinación de coberturas | Media | Alto | **Alto** | 2 |
| A3 — PII en logs | Media | Medio | **Medio** | 3 |
| A6 — DoS por contexto | Baja | Medio | **Bajo** | 4 |

---

## Referencias

- [OWASP Top 10 for LLM Applications 2025](https://owasp.org/www-project-top-10-for-large-language-model-applications/)
- [NIST AI RMF](https://www.nist.gov/system/files/documents/2023/01/26/AI%20RMF%201.0.pdf)
- [Microsoft Threat Modeling AI/ML Systems](https://docs.microsoft.com/security/threat-modeling)
