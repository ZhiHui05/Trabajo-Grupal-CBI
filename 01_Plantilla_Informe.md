# Plantilla de informe — Trabajo en Grupo de Ciberseguridad Industrial

> **Instrucciones de uso.** Copia este archivo, renómbralo como `Informe_Grupo_CBI.md` y sustituye los textos entre corchetes. No dejes placeholders en la entrega. Las notas en blockquote son recordatorios; elimínalas antes de exportar a PDF. Ajusta la extensión si el profesor fija un máximo.

---

## Portada

**Ciberseguridad Industrial — Curso 2026/27**

**Análisis de ciberseguridad de comunicaciones industriales**

**Escenario:** [Modbus/TCP — control de nivel de un depósito]

**Grupo:** [nombre del grupo]

**Integrantes:**
- [Nombre y apellidos]
- [Nombre y apellidos]
- [Nombre y apellidos]
- [Nombre y apellidos]

**Profesor:** José Vera Pérez

**Fecha:** [DD/MM/AAAA]

---

## Resumen ejecutivo

> Máximo una página. Escríbelo al final, cuando el resto esté cerrado.

[Contexto: una o dos frases sobre la ciberseguridad de las comunicaciones industriales y el objetivo del trabajo.]

[Escenario: protocolo, proceso, componentes principales y red.]

[Metodología: despliegue, captura, análisis, MITRE, impacto y controles.]

**Hallazgos principales:**

- [Hallazgo 1: por ejemplo, el tráfico Modbus/TCP viaja en claro y no hay autenticación.]
- [Hallazgo 2: cualquier host con acceso al puerto 502 puede leer variables.]
- [Hallazgo 3: se demostró una escritura FC6 no autorizada que modificó la consigna.]
- [Hallazgo 4: la amenaza prioritaria es T0836 por su impacto físico.]
- [Hallazgo 5: las medidas prioritarias son segmentación, allowlist, IDS y SIS independiente.]

**Riesgo prioritario:** [resumen en 2–3 líneas.]

**Recomendaciones:** [3–4 medidas concretas.]

**Limitaciones:** [proceso simulado, ausencia de SIS real, alcance del laboratorio.]

---

## Índice

> Genera el índice automáticamente al exportar a PDF.

1. Introducción y objetivos
2. Descripción del escenario industrial
3. Despliegue del laboratorio
4. Análisis del tráfico
5. Investigación de amenazas con MITRE ATT&CK for ICS
6. Análisis del impacto sobre el proceso
7. Detección y protección
8. Actividad voluntaria: incidente real
9. Conclusiones
10. Referencias
Anexos

---

## Abreviaturas

| Sigla | Significado |
|---|---|
| PLC | Programmable Logic Controller |
| HMI | Human-Machine Interface |
| SCADA | Supervisory Control and Data Acquisition |
| SIS | Safety Instrumented System |
| OT | Operational Technology |
| IT | Information Technology |
| FC | Function Code |
| HR | Holding Register |
| IR | Input Register |
| CO | Coil |
| DI | Discrete Input |
| MITM | Adversary-in-the-Middle |
| IDS/IPS | Intrusion Detection/Prevention System |
| DPI | Deep Packet Inspection |
| MFA | Multi-Factor Authentication |
| SL-T | Security Level Target |
| FR | Foundational Requirement |

---

# 1. Introducción y objetivos

## 1.1. Contexto

[Describe brevemente el papel de los protocolos industriales y el riesgo de las comunicaciones sin protección. No generalices en exceso; enfoca hacia el protocolo elegido.]

## 1.2. Objetivo

[Objetivo general del trabajo, en una o dos frases.]

## 1.3. Objetivos específicos

1. [Comprender el protocolo y su uso en el proceso.]
2. [Desplegar el laboratorio virtualizado.]
3. [Capturar e interpretar el tráfico.]
4. [Identificar debilidades y vectores de ataque.]
5. [Relacionar las amenazas con MITRE ATT&CK for ICS.]
6. [Analizar el impacto y proponer medidas.]

## 1.4. Alcance y límites

- **Incluido:** [protocolo, proceso, red, capturas, análisis, técnicas, impacto, controles.]
- **Excluido:** [PLC físico, SIS real, red de planta, auditoría formal IEC 62443, pruebas de carga, etc.]
- **Supuestos:** [red aislada, proceso simulado, versiones fijadas.]

## 1.5. Metodología

[Describe las fases: definición del escenario, despliegue, captura, análisis, MITRE, impacto, controles y validación.]

## 1.6. Organización del grupo

[Breve reparto de roles. El detalle puede ir en un anexo.]

---

# 2. Descripción del escenario industrial (4.1 — 15 %)

## 2.1. Proceso

[Describe el proceso: depósito, bomba, sensor de nivel, temperatura, HMI. Explica qué representa cada variable y qué se controla.]

## 2.2. Actores y funciones

| Actor | Implementación | Función | Dirección |
|---|---|---|---|
| PLC virtual | [PyModbus] | [Control y simulación] | [172.28.0.10:502] |
| HMI/SCADA | [Python] | [Supervisión y mando] | [172.28.0.11] |
| Captura | [tcpdump] | [Captura de tráfico] | [Comparte HMI] |
| Atacante | [PyModbus] | [Pruebas de escritura] | [172.28.0.66] |

## 2.3. Protocolo de comunicación

[Explica Modbus/TCP: cliente/servidor, puerto 502, MBAP, PDU, function codes, big-endian, ausencia de autenticación/cifrado, Unit ID, excepciones. Incluye una figura o tabla.]

## 2.4. Variables de proceso

| Variable | Tag | Dirección | Tipo | FC | Escala | Origen | Significado |
|---|---|---|---|---|---|---|---|
| Nivel | LT-101 | HR 0 (40001) | uint16 | 3 | /10 % | PLC | [ ] |
| Temperatura | TT-101 | HR 1 (40002) | uint16 | 3 | /10 °C | PLC | [ ] |
| Consigna | SP-101 | HR 2 (40003) | uint16 | 3/6 | % | HMI | [ ] |
| Velocidad | PV-101 | HR 3 (40004) | uint16 | 3/6 | rpm | HMI | [ ] |
| Bomba | P-101 | CO 0 (00001) | bool | 1/5 | 0/1 | HMI | [ ] |
| Nivel alto | LS-101 | DI 0 (10001) | bool | 2 | 0/1 | PLC | [ ] |
| Caudal | FT-101 | IR 0 (30001) | uint16 | 4 | /10 L/min | PLC | [ ] |
| Presión | PT-101 | IR 1 (30002) | uint16 | 4 | /10 bar | PLC | [ ] |

## 2.5. Operaciones

| Operación | Origen → Destino | FC | Frecuencia | Descripción |
|---|---|---|---|---|
| [Lectura de nivel] | [HMI → PLC] | [3] | [1 s] | [ ] |
| [Lectura de caudal] | [HMI → PLC] | [4] | [1 s] | [ ] |
| [Cambio de consigna] | [HMI → PLC] | [6] | [Manual] | [ ] |
| [Marcha de bomba] | [HMI → PLC] | [5] | [Según nivel] | [ ] |

## 2.6. Arquitectura y comunicaciones

[Incluye el diagrama. Debe mostrar PLC, HMI, captura/atacante, red y puertos. Explica el flujo de las operaciones principales.]

**Figura 1.** Arquitectura del laboratorio. [Fuente: elaboración propia.]

## 2.7. Uso en una planta industrial real

[Explica cómo se trasladaría el escenario a una planta de agua, química, alimentación, etc. Menciona PLC, HMI, historian, red OT, acceso remoto y SIS.]

## 2.8. Supuestos y limitaciones del escenario

- [Proceso simulado.]
- [Sin SIS independiente.]
- [Red plana aislada.]
- [Sin requisitos de tiempo real.]

---

# 3. Despliegue del laboratorio (4.2 — 25 %)

## 3.1. Herramientas y versiones

| Herramienta | Versión | Uso |
|---|---|---|
| Docker/Podman | [ ] | [Contenedores] |
| Python | [3.12] | [Scripts] |
| PyModbus | [3.7.4] | [PLC/HMI] |
| Wireshark | [4.x] | [Análisis] |
| tcpdump | [4.99+] | [Captura] |
| [Opcional] | [ ] | [ ] |

## 3.2. Topología y direccionamiento

| Host | IP | Puerto | Función |
|---|---|---|---|
| PLC | 172.28.0.10 | 502/TCP | [ ] |
| HMI | 172.28.0.11 | Efímero | [ ] |
| Captura | Comparte HMI | — | [ ] |
| Atacante | 172.28.0.66 | Efímero | [ ] |

**Figura 2.** Topología de red. [Fuente: elaboración propia.]

## 3.3. Configuración del entorno

[Explica el `compose.yml`: servicios, red, volúmenes, healthcheck, capacidades. Incluye el archivo completo en el anexo y aquí solo los fragmentos relevantes.]

```yaml
# Fragmento relevante del compose.yml
[ ]
```

## 3.4. Procedimiento de despliegue

1. [Clonar el repositorio.]
2. [Ejecutar `docker compose up -d --build`.]
3. [Comprobar `docker compose ps`.]
4. [Revisar logs del PLC y del HMI.]
5. [Verificar conectividad y captura.]

## 3.5. Problemas encontrados y soluciones

| Problema | Causa | Solución |
|---|---|---|
| [ ] | [ ] | [ ] |

## 3.6. Reproducibilidad

- [ ] Versiones fijadas.
- [ ] Comandos documentados.
- [ ] Sin rutas absolutas.
- [ ] Prueba desde una copia limpia.
- [ ] PCAP de ejemplo incluido.

---

# 4. Análisis del tráfico (4.2 — 25 %)

## 4.1. Método de captura

[Explica dónde se capturó, con qué comando, durante cuánto tiempo y en qué condiciones. Si se usó un sidecar, explica por qué y qué limitación tiene.]

```bash
[comando de captura]
```

## 4.2. Participantes

| Rol | IP | MAC | Puerto | Protocolo |
|---|---|---|---|---|
| [PLC] | [172.28.0.10] | [ ] | [502] | [Modbus/TCP] |
| [HMI] | [172.28.0.11] | [ ] | [ ] | [Modbus/TCP] |
| [Atacante] | [172.28.0.66] | [ ] | [ ] | [Modbus/TCP] |

## 4.3. Operaciones representativas

### 4.3.1. Operación A — [Lectura de nivel y temperatura (FC3)]

[Contexto, filtro, frames, bytes, interpretación, implicación de seguridad.]

| Campo | Bytes | Valor | Interpretación |
|---|---|---|---|
| Transaction ID | [ ] | [ ] | [ ] |
| Protocol ID | [ ] | [ ] | [ ] |
| Length | [ ] | [ ] | [ ] |
| Unit ID | [ ] | [ ] | [ ] |
| Function Code | [ ] | [ ] | [ ] |
| Dirección | [ ] | [ ] | [ ] |
| Cantidad/valor | [ ] | [ ] | [ ] |

**Figura 3.** [Captura de Wireshark o flujo de la operación.] [Fuente: elaboración propia.]

### 4.3.2. Operación B — [Cambio de consigna (FC6)]

[Contexto, filtro, frames, bytes, interpretación.]

### 4.3.3. Operación C — [Escritura no autorizada (FC6 + FC5)]

[Contexto, frames, diferencia de IP, interpretación, efecto en el proceso.]

## 4.4. Variables observadas

| Variable | Dirección | Valor observado | Unidad | Interpretación |
|---|---|---|---|---|
| [Nivel] | [HR 0] | [ ] | [%] | [ ] |
| [Temperatura] | [HR 1] | [ ] | [°C] | [ ] |
| [Consigna] | [HR 2] | [ ] | [%] | [ ] |
| [Bomba] | [CO 0] | [ ] | [0/1] | [ ] |

## 4.5. Mecanismos de seguridad

| Mecanismo | ¿Presente? | Evidencia | Consecuencia |
|---|---|---|---|
| Autenticación | [No] | [ ] | [ ] |
| Autorización | [No] | [ ] | [ ] |
| Cifrado | [No] | [ ] | [ ] |
| Integridad | [No] | [ ] | [ ] |
| Replay | [No] | [ ] | [ ] |
| Auditoría | [No] | [ ] | [ ] |
| Segmentación | [No] | [ ] | [ ] |

## 4.6. Interpretación

[Qué puede hacer un atacante con esta visibilidad. Relaciona con las propiedades de seguridad y con el proceso.]

## 4.7. Limitaciones

- [Punto de captura.]
- [Red plana.]
- [Proceso simulado.]
- [Tráfico de laboratorio, no de planta.]

---

# 5. Investigación de amenazas con MITRE ATT&CK for ICS (4.3 — 35 %)

## 5.1. Método de selección

[Explica cómo se pasó de las comunicaciones observadas a las técnicas. No empieces por la lista de MITRE; empieza por el comportamiento.]

## 5.2. Técnicas seleccionadas

| ID | Técnica | Táctica | Relación | Nivel |
|---|---|---|---|---|
| T0842 | Network Sniffing | Discovery | [ ] | [Demostrada] |
| T0861 | Point & Tag Identification | Collection | [ ] | [Demostrada/parcial] |
| T0830 | Adversary-in-the-Middle | Collection | [ ] | [Posible/demostrada] |
| T0836 | Modify Parameter | Impair Process Control | [ ] | [Demostrada] |

## 5.3. Ficha T0842 — Network Sniffing

| Campo | Contenido |
|---|---|
| ID / nombre | T0842 · Network Sniffing |
| Táctica | Discovery |
| Descripción | [ ] |
| Condiciones | [ ] |
| Relación con el escenario | [ ] |
| Evidencias | [ ] |
| Consecuencias | [ ] |
| Demostración | [ ] |
| Limitaciones | [ ] |
| Fuente | [ ] |

## 5.4. Ficha T0861 — Point & Tag Identification

| Campo | Contenido |
|---|---|
| ID / nombre | T0861 · Point & Tag Identification |
| Táctica | Collection |
| Descripción | [ ] |
| Condiciones | [ ] |
| Relación con el escenario | [ ] |
| Evidencias | [ ] |
| Consecuencias | [ ] |
| Demostración | [ ] |
| Limitaciones | [ ] |
| Fuente | [ ] |

## 5.5. Ficha T0836 — Modify Parameter

| Campo | Contenido |
|---|---|
| ID / nombre | T0836 · Modify Parameter |
| Táctica | Impair Process Control |
| Descripción | [ ] |
| Condiciones | [ ] |
| Relación con el escenario | [ ] |
| Evidencias | [ ] |
| Consecuencias | [ ] |
| Demostración | [ ] |
| Limitaciones | [ ] |
| Fuente | [ ] |

## 5.6. Ficha T0830 — Adversary-in-the-Middle

| Campo | Contenido |
|---|---|
| ID / nombre | T0830 · Adversary-in-the-Middle |
| Táctica | Collection |
| Descripción | [ ] |
| Condiciones | [ ] |
| Relación con el escenario | [ ] |
| Evidencias | [ ] |
| Consecuencias | [ ] |
| Demostración | [ ] |
| Limitaciones | [ ] |
| Fuente | [ ] |

## 5.7. Cadena de ataque

| Fase | Técnica | Acción | Evidencia |
|---|---|---|---|
| Reconocimiento | [T0861] | [ ] | [ ] |
| Recolección | [T0842] | [ ] | [ ] |
| Posicionamiento | [T0830] | [ ] | [ ] |
| Acción | [T0836] | [ ] | [ ] |
| Efecto | [T0831] | [ ] | [ ] |

**Figura 4.** Cadena de ataque. [Fuente: elaboración propia.]

## 5.8. Vulnerabilidad, ataque posible y ataque demostrado

| Nivel | Ejemplo | Justificación |
|---|---|---|
| Vulnerabilidad observada | [ ] | [ ] |
| Ataque técnicamente posible | [ ] | [ ] |
| Ataque demostrado | [ ] | [ ] |

## 5.9. Limitaciones

- [Técnicas no demostradas.]
- [Limitaciones de Docker/red.]
- [Versión de MITRE consultada.]

---

# 6. Análisis del impacto sobre el proceso (4.4 — 25 %)

## 6.1. Amenaza seleccionada y justificación

[Selecciona T0836 u otra. Explica por qué es la más relevante frente a las demás.]

## 6.2. Narrativa del ataque

1. [Acceso inicial.]
2. [Reconocimiento.]
3. [Recolección.]
4. [Acción.]
5. [Efecto.]
6. [Consecuencia.]

**Figura 5.** Escenario de ataque. [Fuente: elaboración propia.]

## 6.3. Condiciones necesarias

| Condición | ¿Se da en el laboratorio? | ¿Se daría en una planta real? |
|---|---|---|
| [Conectividad al puerto 502] | [ ] | [ ] |
| [Conocimiento del mapa] | [ ] | [ ] |
| [Ausencia de autenticación] | [ ] | [ ] |
| [Ausencia de SIS] | [ ] | [ ] |

## 6.4. Consecuencias

| Dimensión | Efecto | Ejemplo |
|---|---|---|
| Seguridad de las personas | [ ] | [ ] |
| Medio ambiente | [ ] | [ ] |
| Disponibilidad | [ ] | [ ] |
| Integridad | [ ] | [ ] |
| Calidad | [ ] | [ ] |
| Equipos | [ ] | [ ] |
| Económico | [ ] | [ ] |
| Cumplimiento/reputación | [ ] | [ ] |

## 6.5. Matriz de riesgo

| ID | Escenario | Activo | Amenaza | P | I | R | Prioridad |
|---|---|---|---|---:|---:|---:|---|
| S1 | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |
| S2 | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |
| S3 | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |

**Figura 6.** Matriz de riesgo. [Fuente: elaboración propia.]

## 6.6. Priorización

[Justifica por qué S1 es la prioridad. Compara con S2/S3. Usa probabilidad, impacto, facilidad y consecuencia.]

## 6.7. Riesgo residual

| Escenario | Riesgo inicial | Medidas | Riesgo residual |
|---|---:|---|---:|
| [S1] | [ ] | [ ] | [ ] |

## 6.8. Limitaciones

- [Proceso simulado.]
- [Sin SIS real.]
- [Escalas cualitativas.]
- [Un solo escenario.]

---

# 7. Detección y protección

## 7.1. Zonas y conductos

| Zona | Activos | Función | SL-T |
|---|---|---|---|
| [Z0] | [ ] | [ ] | [ ] |
| [Z1] | [ ] | [ ] | [ ] |

| Conducto | Origen → Destino | Protocolo | Puerto | Medida |
|---|---|---|---|---|
| [C1] | [HMI → PLC] | [Modbus/TCP] | [502] | [ ] |

## 7.2. Medidas de protección

| Medida | FR | Amenaza | Implementación | Validación |
|---|---|---|---|---|
| [Segmentación] | [FR5] | [T0836] | [ ] | [ ] |
| [Allowlist] | [FR5/FR2] | [T0836] | [ ] | [ ] |
| [IDS] | [FR6] | [T0836] | [ ] | [ ] |
| [SIS] | [FR7] | [T0831] | [ ] | [ ] |

## 7.3. Detección

| Detección | Fuente | Lógica | Técnica |
|---|---|---|---|
| [Escritura desde IP no autorizada] | [PCAP/IDS] | [FC6 y src != HMI] | [T0836] |
| [Cambio de ARP] | [IDS] | [MAC/IP] | [T0830] |

## 7.4. Validación

| Control | Antes | Después | Evidencia |
|---|---|---|---|
| [Firewall] | [ ] | [ ] | [ ] |
| [IDS] | [ ] | [ ] | [ ] |

## 7.5. Riesgo residual y recomendaciones

[Resume el riesgo que queda y las recomendaciones prioritarias.]

---

# 8. Actividad voluntaria: incidente real

> Máximo una página. Si no se realiza, elimina esta sección.

## 8.1. Contexto

[Organización, sector, proceso.]

## 8.2. Cronología

[Fechas y hitos.]

## 8.3. Vector y acción

[Cómo accedió el atacante, qué protocolo/herramienta usó, qué manipuló.]

## 8.4. Consecuencias

[Impacto real, respuesta, duración.]

## 8.5. Relación con el escenario

[Técnica MITRE, similitudes y diferencias.]

## 8.6. Lecciones

[3–5 medidas aplicables.]

## 8.7. Fuentes

- [Fuente 1]
- [Fuente 2]
- [Fuente 3]

---

# 9. Conclusiones

[Qué se aprendió, qué se demostró, qué no se pudo demostrar, medidas prioritarias y trabajo futuro.]

---

# 10. Referencias

> Usa un estilo consistente (APA, IEEE o el que pida el profesor). Incluye fecha de consulta en las URLs.

1. [ ] 
2. [ ] 
3. [ ] 

---

# Anexos

## Anexo A — `compose.yml`

```yaml
[ ]
```

## Anexo B — Scripts

```python
[ ]
```

## Anexo C — PCAP y frames

| Archivo | Descripción | Frames clave | SHA-256 |
|---|---|---|---|
| [01_baseline.pcapng] | [ ] | [ ] | [ ] |
| [03_escritura.pcapng] | [ ] | [ ] | [ ] |

## Anexo D — Tablas auxiliares

[Tablas de participantes, operaciones, variables, mecanismos, técnicas, riesgo y controles.]

---

## Nota final

> Antes de exportar: elimina las notas en blockquote, revisa que no queden corchetes, verifica los frames citados y comprueba que todas las figuras/tablas están referenciadas.
