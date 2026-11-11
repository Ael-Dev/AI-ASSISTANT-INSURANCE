# Entregable 1: Ficha del Proyecto

## Datos generales

| Campo | Valor |
|---|---|
| **Nombre del proyecto** | AI Assistant Insurance. Agentic RAG |
| **Curso** | _(completar)_ |
| **Universidad** | _(completar)_ |
| **Fecha de inicio** | _(completar)_ |
| **Fecha de entrega** | _(completar)_ |
| **Repositorio** | https://github.com/Ael-Dev/AI-ASSISTANT-INSURANCE |

## Equipo

| Integrante | Rol principal | GitHub |
|---|---|---|
| _(Nombre 1)_ | RAG + Ingesta de datos | _(usuario)_ |
| _(Nombre 2)_ | Agentes + Orquestación | _(usuario)_ |
| _(Nombre 3)_ | Seguridad + Guardrails | _(usuario)_ |
| _(Nombre 4)_ | Evaluación + API | _(usuario)_ |

## Objetivo del proyecto

Construir un prototipo funcional de asistente inteligente para el sector seguros que demuestre:

1. **Recuperación**: consulta de documentos de pólizas mediante RAG híbrido con citas verificables.
2. **Agentes con herramientas**: clasificación de reclamos, gestión de tickets y escalamiento a revisión humana.
3. **Memoria entre sesiones**: estado de flujo y conversación persistido por `session_id`.
4. **Seguridad**: guardrails de entrada/salida, anonimización de PII y trazabilidad.

## Alcance del prototipo

**Incluido:**
- Clasificación de reclamos de auto y hogar en lenguaje natural
- Respuestas a consultas de póliza con evidencia citada y abstención controlada
- Creación y consulta de tickets con confirmación explícita del usuario
- Escalamiento simulado a revisión humana
- Evaluación con dataset sintético

**Excluido:**
- Aprobación o rechazo real de indemnizaciones
- Cálculo de pagos definitivos
- Integración con sistemas reales de aseguradoras
- Datos personales reales

## Cronograma

| Semana | Actividad |
|---|---|
| 1 | Datos sintéticos, estructura del proyecto y RAG base |
| 2 | Agentes: clasificador y policy assistant |
| 3 | Ticket agent, orquestador y memoria |
| 4 | Seguridad, guardrails y evaluación |
| 5 | API, integración final y presentación |
