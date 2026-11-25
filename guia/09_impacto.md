# 9. Análisis de impacto sobre el proceso

> Este bloque vale el 25 %. No basta con decir “el atacante puede cambiar la consigna”: hay que explicar qué pasa físicamente, en qué condiciones y por qué es la amenaza prioritaria.

## 9.1. Amenaza seleccionada

**T0836 — Modify Parameter, aplicada a la consigna de nivel (`SP-101`, HR 2).**

Justificación inicial:

- Es **sencilla de ejecutar**: una petición FC6 desde cualquier host con conectividad.
- Tiene **efecto físico directo**: cambia el comportamiento de la bomba y el nivel.
- Afecta a **seguridad, medio ambiente y disponibilidad**, no solo a confidencialidad.
- Es **repetible** y difícil de distinguir de una operación legítima sin monitorización.
- Se relaciona con un incidente real fácil de investigar (Oldsmar, 2021; FrostyGoop, 2024).

## 9.2. Narrativa del ataque

1. **Acceso inicial:** el atacante obtiene conectividad a la red OT, por ejemplo mediante una estación de ingeniería comprometida, una VPN con credenciales débiles o un equipo de mantenimiento conectado a la red.
2. **Reconocimiento:** escanea el puerto 502 y lee HR 0–11. Observa que el HMI consulta HR 0–3 cada segundo y deduce que HR 2 es una consigna y CO 0 es la bomba (T0861).
3. **Recolección:** captura tráfico para confirmar el mapa y los valores normales (T0842).
4. **Acción:** envía FC6 con HR 2 = 95 y FC5 con CO 0 = ON. El PLC acepta ambas porque no hay autenticación (T0836/T0855).
5. **Efecto:** la bomba llena el depósito por encima del 90 %; se activa LS-101 y la alarma del HMI. Si el atacante además manipula las respuestas FC3 (MITM), el HMI puede seguir mostrando un nivel normal (T0832).
6. **Consecuencia:** el depósito desborda; hay vertido, parada de proceso, posible daño a la bomba y riesgo para las personas.

## 9.3. Condiciones necesarias

| Condición | ¿Se da en el laboratorio? | ¿Se daría en una planta real? |
|---|---|---|
| Conectividad al puerto 502 | Sí | Sí, si no hay segmentación |
| Conocimiento del mapa de registros | Sí, por lectura | Sí, por documentación o sniffing |
| Ausencia de autenticación | Sí | Frecuente en Modbus/TCP clásico |
| Capacidad de escritura | Sí | Depende de la lógica y permisos del PLC |
| Ausencia de SIS independiente | Sí | No debería, pero hay plantas sin SIS o con SIS mal segmentado |
| Operador no alertado | Posible con MITM | Posible si no hay alarmas independientes |

## 9.4. Consecuencias por dimensión

| Dimensión | Efecto | Ejemplo concreto |
|---|---|---|
| **Seguridad de las personas** | Vertido de líquido, superficies resbaladizas, exposición química | Desbordamiento de un depósito de producto |
| **Medio ambiente** | Derrame, contaminación de suelo o agua | Vertido de agua con producto químico |
| **Disponibilidad** | Parada de la planta, pérdida de suministro | Bomba parada o proceso detenido |
| **Integridad** | Consigna y nivel falseados | El operador ve 60 % cuando el nivel real es 95 % |
| **Calidad** | Producto fuera de especificación | Dosificación incorrecta |
| **Equipos** | Cavitación, sobrepresión, desgaste | Bomba a 3000 rpm con válvula cerrada |
| **Económico** | Pérdida de producto, reparaciones, multas | Limpieza, sustitución de bomba, sanciones |
| **Cumplimiento y reputación** | Incidente notificable, pérdida de confianza | Notificación a la autoridad ambiental |

## 9.5. Matriz de riesgo

Escala de probabilidad (P) e impacto (I) de 1 a 5:

| P \ I | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|
| **5** | 5 | 10 | 15 | 20 | 25 |
| **4** | 4 | 8 | 12 | 16 | 20 |
| **3** | 3 | 6 | 9 | 12 | 15 |
| **2** | 2 | 4 | 6 | 8 | 10 |
| **1** | 1 | 2 | 3 | 4 | 5 |

Criterio orientativo: 1–4 bajo, 5–9 medio, 10–15 alto, 16–25 crítico.

| ID | Escenario | Amenaza | Activos | P | I | R | Prioridad |
|---|---|---|---|---:|---:|---:|---|
| S1 | Consigna a 95 % + bomba ON | T0836/T0855 | PLC, bomba, depósito | 4 | 5 | **20** | **Crítica** |
| S2 | MITM oculta el nivel real | T0830/T0832 | HMI, PLC | 3 | 5 | 15 | Alta |
| S3 | Flood al puerto 502 | T0814 | PLC, HMI | 4 | 4 | 16 | Alta |
| S4 | Sniffing y reconocimiento | T0842/T0861 | Red OT | 5 | 3 | 15 | Alta (habilitador) |
| S5 | Parada forzada de bomba | T0855 | Bomba, proceso | 4 | 4 | 16 | Alta |

## 9.6. Por qué S1 es la amenaza prioritaria

- **Mayor impacto:** combina seguridad física, medio ambiente y disponibilidad.
- **Mayor facilidad:** no requiere malware ni explotar una vulnerabilidad de memoria; basta un cliente Modbus.
- **Mayor probabilidad:** la red del laboratorio es plana y el protocolo no autentica.
- **Mayor dificultad de detección:** una escritura FC6 es indistinguible de una operación legítima si no se monitoriza la identidad y el rango.
- **Mayor valor didáctico:** conecta protocolo, proceso, MITRE, impacto y medidas de protección.

S2 y S5 también son graves, pero requieren más condiciones (posicionamiento de red o conocimiento del comando). S3 es alta en disponibilidad, pero suele ser más visible y recuperable. S4 no causa daño directo, pero habilita a las demás; por eso se mantiene en prioridad alta como habilitador.

## 9.7. Riesgo residual después de las medidas

| Escenario | Riesgo inicial | Medidas principales | Riesgo residual |
|---|---|---|---|
| S1 | 20 (crítico) | Segmentación, allowlist FC6, IDS, SIS independiente | 6–8 (medio) |
| S2 | 15 (alto) | TLS/VPN, autenticación mutua, monitorización de ARP | 5–6 (medio) |
| S3 | 16 (alto) | Rate limiting, firewall, redundancia | 6–8 (medio) |
| S4 | 15 (alto) | Cifrado, segmentación, control de acceso a capturas | 4–6 (bajo-medio) |
| S5 | 16 (alto) | Allowlist FC5, autenticación, SIS | 6–8 (medio) |

Explica que el riesgo no se elimina: se reduce y se acepta, se transfiere o se mantiene bajo vigilancia. En IEC 62443, esto se relaciona con el riesgo residual y la validación de las medidas.

## 9.8. Limitaciones del análisis

- Proceso simulado, sin dinámica real ni consecuencias físicas reales.
- Sin SIS independiente; en una planta real, el impacto podría ser menor.
- Sin requisitos de tiempo real ni redundancia.
- Los valores de P e I son una estimación cualitativa del grupo, no una auditoría formal.
- El análisis se basa en un único escenario; no cubre toda la superficie de ataque.

Declarar las limitaciones suma rigor. No las escondas.
