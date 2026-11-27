# 12. Estructura y redacción del informe

## 12.1. Extensión orientativa

| Parte | Páginas orientativas | Notas |
|---|---:|---|
| Portada, índice, abreviaturas | 2–3 | No cuentan como contenido técnico |
| Resumen ejecutivo | 1 | Se escribe al final |
| 1. Introducción y objetivos | 1–2 | Contexto, alcance, metodología |
| 2. Escenario (4.1) | 3–4 | Proceso, actores, protocolo, variables, arquitectura |
| 3. Despliegue (4.2) | 3–4 | Herramientas, red, compose, reproducibilidad |
| 4. Análisis de tráfico (4.2) | 3–4 | Evidencias, frames, interpretación |
| 5. MITRE ATT&CK for ICS (4.3) | 7–9 | Fichas y cadena de ataque |
| 6. Impacto (4.4) | 5–6 | Narrativa, condiciones, consecuencias, riesgo |
| 7. Detección y protección | 2–3 | Zonas, medidas, validación |
| 8. Incidente real (voluntario) | 1 | Máximo una página |
| 9. Conclusiones | 1 | Hallazgos y limitaciones |
| Referencias | 1–2 | Estilo consistente |
| Anexos | 3–5 | Código, tablas, PCAP, filtros |
| **Total** | **26–34** | Ajustar si el profesor fija un máximo |

Si hay límite de páginas, prioriza 4.3 y 4.4 y mueve código, tablas extensas y capturas secundarias al anexo. No recortes la interpretación.

## 12.2. Contenido de cada sección

**Resumen ejecutivo (1 página)**

- Contexto y objetivo.
- Escenario y protocolo.
- Metodología.
- Hallazgos principales (4–5 bullets).
- Amenaza prioritaria y riesgo.
- Recomendaciones (3–4 bullets).
- Limitaciones.

**1. Introducción y objetivos**

- Contexto de la ciberseguridad industrial.
- Objetivo del trabajo.
- Alcance y límites.
- Metodología (despliegue, captura, MITRE, impacto, controles).
- Organización del grupo (breve; el detalle va en anexo).

**2. Descripción del escenario (4.1)**

- Proceso y propósito.
- Actores y funciones.
- Protocolo y características.
- Variables y operaciones.
- Arquitectura y comunicaciones.
- Uso en una planta real.
- Supuestos.

**3. Despliegue (4.2)**

- Herramientas y versiones.
- Topología y direccionamiento.
- `compose.yml` y decisiones de diseño.
- Pasos de despliegue.
- Problemas encontrados y soluciones.
- Reproducibilidad.

**4. Análisis de tráfico (4.2)**

- Método de captura y punto de observación.
- Participantes, IP y puertos.
- Operaciones representativas.
- Variables observadas.
- Mecanismos de seguridad ausentes/presentes.
- Interpretación y limitaciones.

**5. MITRE ATT&CK for ICS (4.3)**

- Método de selección.
- Fichas de técnicas.
- Cadena de ataque.
- Diferenciación vulnerabilidad/posible/demostrado.
- Limitaciones.

**6. Impacto (4.4)**

- Amenaza seleccionada y justificación.
- Narrativa del ataque.
- Condiciones.
- Consecuencias por dimensión.
- Matriz de riesgo.
- Priorización.
- Riesgo residual.
- Limitaciones.

**7. Detección y protección**

- Zonas y conductos.
- SL-T.
- Medidas por FR.
- Detección.
- Validación.
- Recomendaciones.

**8. Incidente real (voluntario)**

- Contexto, cronología, vector, consecuencias, relación, lecciones, fuentes.

**9. Conclusiones**

- Qué se aprendió.
- Qué se demostró.
- Qué no se pudo demostrar.
- Medidas prioritarias.
- Trabajo futuro.

## 12.3. Plantilla de resumen ejecutivo

> Este trabajo analiza la ciberseguridad de un escenario de control de nivel basado en Modbus/TCP, desplegado con contenedores Docker. El sistema está formado por un PLC virtual, un HMI y un punto de captura en una red aislada. Se capturó tráfico normal y se ejecutaron pruebas de lectura y escritura no autorizadas. Los resultados muestran que Modbus/TCP no autentica ni cifra, por lo que cualquier host con conectividad al puerto 502 puede leer variables y modificar consignas. La amenaza prioritaria es la modificación de la consigna de nivel (T0836), que puede provocar un desbordamiento y afectar a la seguridad, el medio ambiente y la disponibilidad. Se proponen segmentación, allowlist de funciones, IDS, autenticación fuerte y un SIS independiente. Las limitaciones incluyen el carácter simulado del proceso y la ausencia de un SIS real.

## 12.4. Plantilla de conclusiones

> El laboratorio permitió comprobar que la ausencia de autenticación e integridad en Modbus/TCP no es una debilidad teórica: una escritura FC6 desde un host no autorizado fue aceptada y modificó el comportamiento del proceso. La captura y el análisis de frames permitieron identificar las variables y justificar la relación con T0842, T0861, T0836 y T0830. La amenaza más relevante es la manipulación de la consigna, por su facilidad y su impacto físico. Las medidas prioritarias son la segmentación, la allowlist de funciones y direcciones, la monitorización de escrituras y un SIS independiente. Como trabajo futuro, se propone implementar TLS, validar las reglas del IDS y ampliar el análisis a un PLC físico.

## 12.5. Figuras y tablas

Incluye como mínimo:

- Figura 1: arquitectura del laboratorio.
- Figura 2: topología de red y direcciones.
- Figura 3: flujo de una operación FC3.
- Figura 4: flujo de una escritura FC6 no autorizada.
- Figura 5: cadena de ataque MITRE.
- Figura 6: matriz de riesgo.
- Tabla 1: actores y funciones.
- Tabla 2: variables Modbus.
- Tabla 3: operaciones.
- Tabla 4: mecanismos de seguridad.
- Tabla 5: técnicas MITRE.
- Tabla 6: escenarios de riesgo.
- Tabla 7: medidas de protección.

Cada figura y tabla debe estar referenciada en el texto y tener título y fuente. No incluyas una figura que no se explique.

## 12.6. Estilo de redacción

- Usa **primera persona del plural** con moderación (“se desplegó”, “se observó”, “el grupo propone”).
- Define las siglas la primera vez: PLC, HMI, SCADA, SIS, IDS, DPI, MFA.
- Separa **hechos** (“el frame 128 contiene FC6”) de **interpretaciones** (“esto demuestra que no hay autorización”).
- Usa unidades y escalas coherentes.
- Evita adjetivos sin evidencia (“muy inseguro”, “crítico”) sin justificar.
- No copies párrafos de fuentes; sintetiza y cita.
- Revisa la ortografía y la concordancia.
- Mantén una terminología única: “consigna”, no “setpoint” y “set point” mezclados; “registro de retención”, no “holding register” y “registro” a la vez.

## 12.7. Formato

- Portada con título, asignatura, curso, grupo, integrantes, fecha.
- Índice con números de página.
- Numeración de páginas.
- Fuente legible (11–12 pt), interlineado 1,15, márgenes 2,5 cm.
- Figuras nítidas; no fotos borrosas de la pantalla.
- Código en monoespaciado; fragmentos largos al anexo.
- PCAP referenciados por nombre y frame.
- Hash SHA-256 de los PCAP.
- PDF con marcadores y tamaño razonable.

## 12.8. Si hay presentación oral

Prepara 6 diapositivas:

1. Problema y objetivo.
2. Escenario y arquitectura.
3. Metodología y herramientas.
4. Evidencia principal (PCAP, frame, escritura).
5. MITRE e impacto.
6. Medidas y conclusiones.

Ensayos de 5–8 minutos. Ten a mano el PCAP y un comando reproducible, pero no dependas de la red del aula.
