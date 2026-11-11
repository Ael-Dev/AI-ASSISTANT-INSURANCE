# Entregable 7: Marco Regulatorio

## Alcance

Este documento identifica el marco regulatorio aplicable al prototipo, considerando:
- El sector seguros como dominio de aplicación
- El uso de sistemas de IA generativa
- El tratamiento de datos personales (aunque el prototipo usa datos sintéticos)

---

## Regulación de IA

### EU AI Act (2024, aplicación gradual hasta 2026)

El sistema califica como **sistema de IA de alto riesgo** si se desplegara en producción real, dado que:
- Participa en la gestión de reclamaciones de seguros (Anexo III del EU AI Act)
- Puede influir en decisiones con impacto financiero sobre los asegurados

**Obligaciones aplicables en producción:**
- Documentación técnica completa del sistema
- Sistema de gestión de riesgos continuo
- Datos de entrenamiento y evaluación documentados
- Supervisión humana obligatoria
- Registro en la base de datos de la UE

> El prototipo académico no está sujeto a estas obligaciones, pero el diseño las contempla (human-in-the-loop, trazabilidad, abstención).

### NIST AI RMF (Marco de Gestión de Riesgos de IA)

Funciones aplicadas en el diseño:
- **Govern**: política de no tomar decisiones contractuales; scope limitado
- **Map**: identificación de riesgos en modelo de amenazas
- **Measure**: métricas de evaluación definidas
- **Manage**: controles de guardrails y escalamiento

---

## Regulación de protección de datos

### GDPR (Reglamento General de Protección de Datos: UE)

Principios aplicados al diseño, aunque el prototipo usa datos sintéticos:
- **Minimización**: el sistema solicita solo los datos necesarios
- **Limitación de propósito**: los datos de reclamos se usan solo para ese reclamo
- **Exactitud**: abstención cuando la información no es verificable
- **Integridad y confidencialidad**: anonimización de PII en logs

### Ley Peruana de Protección de Datos Personales (Ley 29733)

Aplicable si el sistema se desplegara en Perú:
- Requiere consentimiento informado para el tratamiento de datos
- Obliga a medidas de seguridad técnica y organizacional
- El titular tiene derecho de acceso, rectificación y cancelación

---

## Regulación del sector seguros

### SBS (Superintendencia de Banca, Seguros y AFP: Perú)

Aspectos relevantes para un sistema como este en producción:
- Las respuestas del asistente no pueden constituir asesoría de seguros sin licencia
- La determinación de cobertura requiere intervención de un ajustador certificado
- Los registros de reclamos deben conservarse según los plazos establecidos

**Diseño del prototipo:** el sistema incluye disclaimers explícitos indicando que sus respuestas son orientativas y no determinan cobertura.

---

## Implicaciones para el diseño del prototipo

| Requisito regulatorio | Cómo se aborda en el prototipo |
|---|---|
| Supervisión humana | Human-in-the-loop para casos de alta incertidumbre |
| Trazabilidad de decisiones | logs estructurados locales + logs estructurados |
| No-decisiones contractuales | Disclaimers en respuestas; scope limitado a orientación |
| Protección de PII | Presidio + datos sintéticos en el prototipo |
| Consentimiento para tickets | Confirmación explícita obligatoria antes de `create_ticket` |
| Abstención ante incertidumbre | `check_evidence_sufficiency` + respuesta de abstención |

---

## Referencias

- [EU AI Act](https://artificialintelligenceact.eu/)
- [NIST AI RMF 1.0](https://airc.nist.gov/RMF)
- [Ley 29733. Perú](https://www.leyes.congreso.gob.pe/Documentos/Leyes/29733.pdf)
- [SBS. Circular de Seguros](https://www.sbs.gob.pe/regulacion/seguros)
- [OWASP Top 10 LLM 2025](https://owasp.org/www-project-top-10-for-large-language-model-applications/)
