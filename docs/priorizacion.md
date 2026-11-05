# Entregable 4 — Priorización de Controles

## Criterios de priorización

Los controles se priorizan según tres criterios combinados:

1. **Riesgo residual** (del modelo de amenazas): amenazas de mayor riesgo se abordan primero.
2. **Esfuerzo de implementación**: controles de bajo esfuerzo y alto impacto tienen prioridad.
3. **Obligatoriedad funcional**: algunos controles son requisito para que el sistema funcione correctamente (ej. confirmación antes de crear ticket).

---

## Matriz de priorización

| # | Control | Amenaza que mitiga | Riesgo | Esfuerzo | Prioridad | Estado |
|---|---|---|---|---|---|---|
| C1 | Separación datos/instrucciones en prompts | A1 Prompt injection | Crítico | Bajo | **P1** | Pendiente |
| C2 | Validación backend de ownership de recursos | A2 Acceso no autorizado | Alto | Bajo | **P1** | Pendiente |
| C3 | Estado `awaiting_confirmation` antes de escribir | A4 Tickets sin consentimiento | Alto | Bajo | **P1** | Pendiente |
| C4 | Verificación de evidencia antes de responder | A5 Alucinación | Alto | Medio | **P1** | Pendiente |
| C5 | Anonimización PII con Presidio antes de logs | A3 PII en logs | Medio | Medio | **P2** | Pendiente |
| C6 | Límite de tokens por request + rate limiting | A6 DoS por contexto | Bajo | Bajo | **P2** | Pendiente |
| C7 | Validación de esquema de salida del LLM (Pydantic) | A1, A4 | Alto | Bajo | **P1** | Pendiente |
| C8 | Human-in-the-loop para casos de alta incertidumbre | A5 | Alto | Medio | **P2** | Pendiente |
| C9 | Trazabilidad completa con LangSmith | Todos | Transversal | Bajo | **P1** | Pendiente |
| C10 | Abstención explícita cuando falta evidencia RAG | A5 | Alto | Bajo | **P1** | Pendiente |

---

## Controles P1 — Implementar en el MVP

Estos controles son obligatorios para considerar el sistema seguro para una demostración:

- **C1** — Prompts con secciones claramente delimitadas (`<system>`, `<retrieved_context>`, `<user_input>`)
- **C2** — Toda función de tool valida que `policy_id` / `ticket_id` pertenece al `customer_id` de la sesión
- **C3** — El workflow nunca ejecuta `create_ticket` sin pasar por el estado `awaiting_confirmation`
- **C4** — La función `check_evidence_sufficiency` se ejecuta antes de cada respuesta de cobertura
- **C7** — Todos los outputs del LLM se parsean con modelos Pydantic; errores de parsing generan abstención
- **C9** — LangSmith activo desde el inicio; cada ejecución genera una traza rastreable
- **C10** — Si el retriever devuelve menos de N fragmentos relevantes, el agente se abstiene

## Controles P2 — Implementar antes de la entrega final

- **C5** — Presidio ejecuta anonimización sobre el objeto de log antes de escribirlo
- **C6** — Middleware FastAPI rechaza requests que superen `MAX_INPUT_TOKENS`
- **C8** — Reglas deterministas de escalamiento: confianza < umbral → cola humana

---

## Notas

- La priorización asume un entorno de demostración con datos sintéticos. Un despliegue real requeriría análisis adicional de autenticación, cifrado en tránsito y cumplimiento regulatorio.
- Ver [`controles.md`](controles.md) para la implementación detallada de cada control.
