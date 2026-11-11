# Entregable 4: Priorización de Controles

> Ver amenazas en [`modelo-de-amenazas.md`](modelo-de-amenazas.md)  
> Ver implementación en [`controles.md`](controles.md)

## Criterios

1. **Riesgo residual**. amenazas de mayor riesgo se abordan primero
2. **Esfuerzo de implementación**. bajo esfuerzo + alto impacto tiene prioridad
3. **Obligatoriedad funcional**. algunos controles son requisito para que el sistema sea demostrable de forma segura

---

## Matriz de priorización

| # | Control | Amenaza | Riesgo | Esfuerzo | Prioridad |
|---|---|---|---|---|---|
| C1 | Input Validator | A1 Injection directa + A6 DoS | Crítico | Bajo | **P1** |
| C2 | Ownership Check en `crm_tool` | A3 Acceso no autorizado | Alto | Bajo | **P1** |
| C3 | Separación datos/instrucciones en prompt | A2 Injection via RAG | Alto | Bajo | **P1** |
| C7 | Abstención RAG (score mínimo) | A5 Alucinación | Alto | Bajo | **P1** |
| C4 | Output Filter / DLP (Presidio) | A4 PII en respuesta | Medio | Medio | **P2** |
| C5 | Logs sin PII (logs estructurados locales config) | A4 PII en logs | Medio | Bajo | **P2** |
| C6 | Human-in-the-loop (regla determinista) | A5 casos ambiguos | Alto | Medio | **P2** |

---

## P1: Obligatorio para el MVP

Estos controles son necesarios para que el sistema pueda demostrarse sin exponer datos ni ejecutar acciones no previstas:

- **C1**. Validar tokens y patrones de injection antes de que el mensaje llegue al LLM
- **C2**. `crm_tool` verifica `customer_id` de sesión antes de ejecutar SQL
- **C3**. Los PDFs recuperados van en sección `[CONTEXT]` delimitada, no como instrucciones
- **C7**. Si el retriever no encuentra evidencia suficiente, el Policy Agent se abstiene

## P2: Implementar antes de la entrega final

- **C4**. Presidio filtra PII en la respuesta final antes de entregar al usuario
- **C5**. logs estructurados locales configurado para excluir campos sensibles de las trazas
- **C6**. Reglas deterministas de escalamiento en el Orchestrator
