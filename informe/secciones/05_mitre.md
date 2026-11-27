# 5. Investigación de amenazas con MITRE ATT&CK for ICS (4.3 — 35 %)

Este capítulo traduce las comunicaciones del laboratorio a técnicas de MITRE ATT&CK for ICS. No se parte del catálogo de técnicas, sino de lo que el sistema hace: quién habla con el PLC, con qué funciones Modbus, cada cuánto y con qué protección. A partir de ese comportamiento se seleccionan cuatro técnicas principales —T0842, T0861, T0836 y T0830— y dos de apoyo —T0855/T1692.001 y T0831/T0832—, se documentan sus condiciones y evidencias, y se distingue de forma explícita entre vulnerabilidad observada, ataque técnicamente posible y ataque demostrado.

## 5.1. Método de selección

La línea base (`01_baseline_20261127.pcapng`) muestra un diálogo periódico, aproximadamente cada segundo, entre el HMI (`172.28.0.11`) y el PLC (`172.28.0.10`) por el puerto TCP 502. El HMI lee los *holding registers* 0–3 con FC3, los *input registers* 0–1 con FC4, la entrada discreta 0 con FC2 y las bobinas 0–1 con FC1. No hay autenticación, cifrado ni código de integridad: los valores de nivel, temperatura, consigna, velocidad, caudal y presión viajan en claro y son legibles en cualquier captura.

De ese comportamiento se derivan cinco preguntas que guían la selección:

1. ¿Qué puede obtener un adversario que solo escucha? **T0842 Network Sniffing**.
2. ¿Qué puede deducir leyendo direcciones y correlacionando valores? **T0861 Point & Tag Identification**.
3. ¿Qué gana si se coloca entre HMI y PLC? **T0830 Adversary-in-the-Middle**.
4. ¿Qué puede modificar con una escritura directa? **T0836 Modify Parameter**.
5. ¿Qué efecto tiene esa modificación sobre el proceso? **T0831 Manipulation of Control** y **T0832 Manipulation of View**.

Se descartaron inicialmente las técnicas que no dejan una evidencia clara en este montaje o que exigirían alterar el laboratorio de forma desproporcionada. T0814 *Denial of Service* queda como trabajo futuro: un flood al puerto 502 es fácil de lanzar, pero su efecto —pérdida de comunicación— no aporta al análisis de integridad del proceso que ocupa el bloque 4.4, y podría dejar el entorno inestable durante la recogida de evidencias.

Cada técnica se contrastó con la página oficial de MITRE ATT&CK for ICS, se relacionó con una función y una dirección Modbus concretas, y se clasificó según el nivel de demostración alcanzado (§5.8). Para T0861 se desarrolló un script propio, `laboratorio/scan_recon.py`, que automatiza el sondeo de Unit IDs y la lectura secuencial del mapa de registros.

Las capturas citadas en este capítulo se realizaron el 27/11/2026 y los nombres de archivo incluyen esa fecha.

## 5.2. Técnicas seleccionadas

| ID | Técnica | Táctica | Relación con el escenario | Nivel | Evidencia |
|---|---|---|---|---|---|
| T0842 | Network Sniffing | Discovery | Modbus/TCP en texto claro; captura en el PLC y *sidecar* del HMI | Demostrada | `01_baseline_20261127.pcapng`, frames 1–9 |
| T0861 | Point & Tag Identification | Collection | Sondeo de Unit IDs y lectura secuencial de HR 0–11; inferencia del mapa | Demostrada/parcial | `02_reconocimiento_20261127.pcapng`, frames 300–369 y 398; `scan_recon.py` |
| T0830 | Adversary-in-the-Middle | Collection | ARP spoofing o proxy TCP entre HMI y PLC | Posible (no reproducida) | No se generó PCAP; ver §5.6 |
| T0836 | Modify Parameter | Impair Process Control | Escritura FC6 de la consigna de nivel (HR 2) | Demostrada | `03_escritura_setpoint_20261127.pcapng`, frames 284–291, 954 y 959 |
| T0855 / T1692.001 | Unauthorized Command Message / Unauthorized Message: Command Message | Impair Process Control (y Evasion) | Escritura FC5 de marcha de bomba (CO 0) | Demostrada (apoyo) | `03_escritura_setpoint_20261127.pcapng`, frames 288–289 |
| T0831 | Manipulation of Control | Impact | Efecto de T0836/T0855 sobre nivel y bomba | Consecuencia | Nivel > 100 % (frame 954); `LS-101 = 1` (frame 959) |
| T0832 | Manipulation of View | Impact | Reescritura de respuestas FC3 mediante MITM | Posible | No reproducida |

**Nota de versión.** ATT&CK for ICS ha reestructurado parte del catálogo. La técnica clásica T0855 *Unauthorized Command Message* aparece en la versión consultada como **T1692.001 — Unauthorized Message: Command Message**, con las tácticas *Evasion* e *Impair Process Control*. En este trabajo se mantiene T0855 como referencia histórica y se indica su correspondencia. Todas las fuentes se consultaron el 27/11/2026.

## 5.3. Ficha T0842 — Network Sniffing

| Campo | Contenido |
|---|---|
| **ID / nombre** | T0842 · Network Sniffing |
| **Táctica** | Discovery |
| **Descripción** | El adversario captura tráfico de la red industrial para obtener topología, direcciones, protocolos y valores del proceso. En Modbus/TCP no necesita romper ningún cifrado: las peticiones y respuestas se leen directamente. |
| **Condiciones** | Acceso a la red o a un punto de captura (interfaz en modo promiscuo, SPAN/mirror o *host* comprometido); tráfico sin cifrar; capacidad de ejecutar `tcpdump` o Wireshark; conocer la interfaz y el filtro adecuado. |
| **Relación con el escenario** | El PLC (`172.28.0.10`) y el HMI (`172.28.0.11`) se comunican por `eth0` en la red `ics_net` con Modbus/TCP. La captura realizada en el PLC ve todas las peticiones y respuestas porque todo el tráfico termina en él. El servicio `capture`, que comparte el *namespace* del HMI, solo ve la perspectiva del HMI y no el tráfico del atacante. |
| **Evidencias** | PCAP `01_baseline_20261127.pcapng`, frames 1–9: sesión TCP hacia el puerto 502, peticiones FC3/FC4/FC2/FC1 y respuestas con nivel, temperatura, consigna, velocidad, caudal y presión en claro. La captura contiene 46 ciclos de sondeo idénticos y ninguna escritura. Ausencia de TLS o de cualquier campo de autenticación en la PDU. |
| **Consecuencias** | Pérdida de confidencialidad: el adversario obtiene el mapa de variables, las consignas y el comportamiento del lazo. Es un habilitador directo de T0861, T0836 y T0830. |
| **Demostración** | `docker compose exec plc tcpdump -i eth0 -s 0 -w /app/captures/01_baseline_20261127.pcapng 'tcp port 502'`, con el HMI en modo monitor durante 45 s (460 paquetes). El análisis en Wireshark con el filtro `modbus` permite identificar las peticiones FC3/FC4 y los valores de proceso (frames 1–9). |
| **Limitaciones** | La captura en el PLC es un punto de observación privilegiado, no la posición de un atacante externo. En una red *bridge* de Docker el tráfico *unicast* no se difunde a todos los contenedores; para afirmar *sniffing* externo habría que demostrarlo con ARP spoofing, un proxy o un puerto espejo, y eso se trata en T0830. |
| **Fuente** | MITRE ATT&CK for ICS, *T0842 Network Sniffing*, consultado el 27/11/2026, https://attack.mitre.org/techniques/T0842/ |

## 5.4. Ficha T0861 — Point & Tag Identification

| Campo | Contenido |
|---|---|
| **ID / nombre** | T0861 · Point & Tag Identification |
| **Táctica** | Collection |
| **Descripción** | El adversario recopila información sobre los dispositivos y sus puntos o *tags* para identificar componentes, funciones y variables del sistema de control. En Modbus no hay nombres simbólicos: la identificación se consigue leyendo direcciones y correlacionando sus valores con el comportamiento del proceso. |
| **Condiciones** | Conectividad al puerto 502; ausencia de autenticación y de autorización por dirección; conocimiento previo mínimo del protocolo; capacidad de observar el patrón de *polling* del HMI o de leer secuencialmente el mapa de registros. |
| **Relación con el escenario** | El HMI consulta cada segundo HR 0–3 en bloque (`start=0`, `count=4`). Un cliente no autorizado puede recorrer esas mismas direcciones una a una, comprobar qué Unit ID responde y deducir el significado de cada valor: HR 0 se mueve lentamente y coincide con el nivel; HR 2 permanece en 60 y actúa como consigna; HR 3 vale 1450 y se corresponde con las rpm; CO 0 enciende la bomba. |
| **Evidencias** | PCAP `02_reconocimiento_20261127.pcapng`, frames 300–369 y 398: peticiones FC3 individuales (`count=1`) desde `172.28.0.66` a direcciones consecutivas 0–11, sondeo de Unit IDs y excepción `0x02` (*Illegal Data Address*) al consultar HR 32. El PLC responde en el Unit ID 1; los Unit IDs 0, 2–5 y 247 devuelven `0x0B` (*Gateway Target Failed to Respond*) en los frames 302–315. La diferencia con el patrón del HMI —bloques de 4 cada segundo frente a 12 lecturas unitarias consecutivas— es en sí misma una señal detectable. |
| **Consecuencias** | El adversario obtiene el mapa de variables y las consignas, y puede elegir la escritura de mayor efecto (T0836) sin prueba y error. Pérdida de confidencialidad y reducción del coste de un ataque posterior. |
| **Demostración** | `docker compose exec attacker python scan_recon.py --host plc`, con captura simultánea en el PLC. El script comprueba el puerto, sondea los Unit IDs 0–5 y 247, lee HR 0–11 una a una, consulta CO 0–1, DI 0 e IR 0–1, y fuerza una dirección fuera del bloque para provocar la excepción. Con `--raw` omite el mapa conocido y muestra solo direcciones y valores crudos. Genera un CSV y una tabla Markdown con el resultado. |
| **Limitaciones** | Los nombres `LT-101`, `SP-101`, etc. son una interpretación a partir del mapa documentado en `laboratorio/README.md`, no información que transporte el protocolo. Por eso la técnica se demuestra de forma **parcial**: el script descubre el Unit ID, el bloque de direcciones válido y el patrón de lectura, pero la asignación de nombres se apoya en ese mapa; una inferencia ciega exigiría correlacionar los valores sin documentación previa. El bloque de *holding registers* tiene 32 posiciones, por lo que HR 4–11 responden 0 y las direcciones inválidas aparecen por encima de 31. |
| **Fuente** | MITRE ATT&CK for ICS, *T0861 Point & Tag Identification*, consultado el 27/11/2026, https://attack.mitre.org/techniques/T0861/ |

### Mapa de registros identificado

Salida de ejemplo de `scan_recon.py` (ejecución del 27/11/2026). Los valores de nivel y temperatura varían con el proceso; la correspondencia dirección–variable es la que se deduce del patrón de *polling* y de la escala.

| FC | Dirección | Referencia | Variable identificada | Valor de ejemplo | Interpretación |
|---:|---:|---|---|---:|---|
| 3 | HR 0 | 40001 | `LT-101` Nivel | 161 | 16,1 % (valor / 10) |
| 3 | HR 1 | 40002 | `TT-101` Temperatura | 248 | 24,8 °C (valor / 10) |
| 3 | HR 2 | 40003 | `SP-101` Consigna de nivel | 60 | 60 % (sin escala) |
| 3 | HR 3 | 40004 | `PV-101` Consigna de velocidad | 1450 | 1450 rpm (sin escala) |
| 3 | HR 4–11 | 40005–40012 | Sin asignar | 0 | Direcciones válidas del bloque, sin variable asignada |
| 1 | CO 0 | 00001 | `P-101` Marcha de bomba | 0 | Bomba parada |
| 1 | CO 1 | 00002 | `RESET` Reset de alarma | 0 | Sin reset pendiente |
| 2 | DI 0 | 10001 | `LS-101` Nivel alto | 0 | Nivel por debajo del 90 % |
| 4 | IR 0 | 30001 | `FT-101` Caudal | 0 | 0,0 L/min (valor / 10) |
| 4 | IR 1 | 30002 | `PT-101` Presión | 0 | 0,0 bar (valor / 10) |
| 3 | HR 32 | 40033 | Fuera de mapa | — | Excepción `0x02` (*Illegal Data Address*) |

La tabla demuestra el resultado de T0861: con el sondeo de Unit IDs, 17 lecturas del mapa (12 HR + 2 CO + 1 DI + 2 IR) y una sonda de dirección inválida se identifica el mapa de variables sin credenciales y sin acceso al proyecto del PLC. La asignación de nombres se contrasta con el mapa documentado en `laboratorio/README.md`.

## 5.5. Ficha T0836 — Modify Parameter

| Campo | Contenido |
|---|---|
| **ID / nombre** | T0836 · Modify Parameter |
| **Táctica** | Impair Process Control |
| **Descripción** | El adversario modifica parámetros del sistema de control —consignas, umbrales, ganancias o límites de alarma— para alterar el comportamiento del proceso sin necesidad de sustituir el programa del controlador. |
| **Condiciones** | Capacidad de escritura en el controlador; conocimiento de la dirección del parámetro (HR 2); ausencia de autenticación y de autorización; conectividad al puerto 502; que el HMI no revierta la escritura de forma inmediata. |
| **Relación con el escenario** | La consigna de nivel está en HR 2 (40003) y se escribe con FC6. `attack_write.py` la cambia de 60 % a 95 % y, en la misma ejecución, fuerza la bomba con FC5 sobre CO 0. El PLC acepta la escritura porque no distingue entre el HMI y cualquier otro cliente. |
| **Evidencias** | PCAP `03_escritura_setpoint_20261127.pcapng`, frames 284–291, 954 y 959: petición FC6 con `HR2 = 95` desde `172.28.0.66` (frame 284), respuesta FC6 que repite la escritura (frame 286), petición FC5 con `CO0 = 1` (frame 288) y su respuesta (frame 289). En la consulta FC3 posterior del HMI, el valor de consigna ya es 95 (frame 291); el nivel sube hasta el 105 % (frame 954) y `LS-101` pasa a 1 (frame 959). |
| **Consecuencias** | Desbordamiento del depósito, vertido, cavitación o parada de la bomba, pérdida de calidad y riesgo para personas y medio ambiente. La consecuencia no es solo de confidencialidad: afecta a la integridad y a la seguridad del proceso. |
| **Demostración** | Con el HMI en modo monitor: `docker compose exec attacker python attack_write.py --host plc --setpoint 95 --pump on --read`. La ejecución escribe `HR2 = 95` y `CO0 = 1`; las lecturas posteriores del HMI muestran el cambio de consigna, la bomba en marcha, la subida del nivel hasta el 105 % y `NivelAlto=SI` (frames 284–291, 954 y 959). Restauración posterior con `--setpoint 60 --pump off`. |
| **Limitaciones** | El proceso es simulado y no incluye un SIS independiente ni enclavamientos de seguridad. En una instalación real, un SIS o un límite de consigna en el PLC podría reducir el impacto; esa discusión corresponde a las medidas de protección (capítulo 7). |
| **Fuente** | MITRE ATT&CK for ICS, *T0836 Modify Parameter*, consultado el 27/11/2026, https://attack.mitre.org/techniques/T0836/ |

## 5.6. Ficha T0830 — Adversary-in-the-Middle

| Campo | Contenido |
|---|---|
| **ID / nombre** | T0830 · Adversary-in-the-Middle |
| **Táctica** | Collection |
| **Descripción** | El adversario se posiciona entre dos o más dispositivos para interceptar, modificar o reenviar el tráfico. En una red industrial sin autenticación mutua, el intermediario puede alterar las respuestas que recibe el operador. |
| **Condiciones** | Misma red o segmento que HMI y PLC; capacidad de ARP o DNS spoofing, *rogue gateway* o control de un nodo intermedio; `ip_forward` activo; tráfico sin cifrar ni autenticación mutua. |
| **Relación con el escenario** | HMI y PLC confían en la red. Un ARP spoofing desde `172.28.0.66` permitiría hacerse pasar por el PLC ante el HMI y por el HMI ante el PLC, observar todo el diálogo y reescribir respuestas FC3 para que el HMI muestre un nivel normal mientras el depósito se llena (T0832). |
| **Evidencias esperadas** | No se generó PCAP en esta entrega. Si se reprodujera: respuestas ARP no solicitadas o duplicadas, cambio de la MAC asociada a `172.28.0.10` o `172.28.0.11`, latencia anómala y tráfico que pasa por un *host* no inventariado. En el proceso, discrepancia entre el valor del HMI y el del PLC. |
| **Consecuencias** | Manipulación de la vista y del control, comandos falsos, datos falsos al operador, pérdida de integridad y de confidencialidad, y retraso en la respuesta ante una emergencia. |
| **Demostración** | No se reprodujo en el laboratorio. Se valoró un montaje con `arpspoof`/`bettercap` y *forwarding* en el contenedor `attacker`, pero no llegó a completarse: la red *bridge* de Docker Desktop aísla o filtra el ARP. Se clasifica como **ataque técnicamente posible**, no demostrado. |
| **Limitaciones** | El resultado depende del entorno de virtualización: en Docker Desktop el ARP no se propaga entre contenedores de la red *bridge*, por lo que la interceptación no se completó. No se afirma una demostración que no se tiene; la técnica se justifica por el protocolo, la arquitectura y las herramientas disponibles, y queda como trabajo futuro sobre máquinas virtuales o un *switch* con SPAN. |
| **Fuente** | MITRE ATT&CK for ICS, *T0830 Adversary-in-the-Middle*, consultado el 27/11/2026, https://attack.mitre.org/techniques/T0830/ |

## 5.7. Cadena de ataque

| Fase | Técnica | Acción del atacante | Evidencia en el laboratorio |
|---|---|---|---|
| Reconocimiento | T0861 | Sondear Unit IDs y leer HR 0–11 para deducir variables | `02_reconocimiento`, frames 300–369 y 398; salida de `scan_recon.py` |
| Recolección | T0842 | Capturar el diálogo HMI–PLC en texto claro | `01_baseline`, frames 1–9 |
| Posicionamiento | T0830 | ARP spoofing o proxy entre HMI y PLC | No reproducido; se documenta como posible |
| Acción | T0836 / T0855 | Escribir la consigna (FC6) y arrancar la bomba (FC5) | `03_escritura_setpoint`, frames 284–291 |
| Efecto sobre el control | T0831 | Cambia el proceso | Nivel 105 % (frame 954), `LS-101 = 1` (frame 959), `NivelAlto=SI` |
| Ocultación | T0832 | Oculta el cambio al operador | No reproducido; exigiría MITM y reescritura de respuestas FC3 |
| Impacto | — | Desbordamiento, parada o vertido (consecuencia potencial) | Logs del PLC/HMI y estado del proceso |

![Figura 4 — Cadena de ataque](figuras/fig_4_cadena_ataque.png)

**Figura 4.** Cadena de ataque. [Fuente: elaboración propia.]

La Figura 4 resume la secuencia; las técnicas no son independientes: se encadenan. T0842 y T0861 reducen la incertidumbre del adversario; T0830 le permitiría sostenerse en el tiempo; T0836 y T0855 producen la acción; T0831 y T0832 describen el efecto. Esta secuencia es la que justifica que la amenaza prioritaria del bloque 4.4 sea la manipulación de la consigna y no una técnica aislada.

**Matiz terminológico.** Las fases de la tabla son una simplificación didáctica, no las tácticas oficiales de ATT&CK. T0861 pertenece a *Collection* y T0842 a *Discovery*, aunque aquí se presenten como “reconocimiento” y “recolección” en sentido amplio. En las fichas se usa siempre la táctica oficial.

## 5.8. Vulnerabilidad observada, ataque posible y ataque demostrado

| Nivel | Ejemplo en este trabajo | Cómo se justifica |
|---|---|---|
| **Vulnerabilidad observada** | Modbus/TCP no autentica ni cifra; el puerto 502 es accesible desde `172.28.0.66`; el PLC acepta lecturas y escrituras de cualquier cliente | `01_baseline` muestra PDUs sin credenciales y valores en claro; `02_reconocimiento` registra las lecturas desde `172.28.0.66` y `03_escritura_setpoint` las escrituras FC6/FC5 aceptadas |
| **Ataque técnicamente posible** | MITM con ARP spoofing para modificar respuestas FC3; *replay* de comandos; DoS con flood al puerto 502 | Se apoya en el protocolo, la arquitectura plana y herramientas conocidas, aunque no se haya reproducido en Docker. Se documentan condiciones y evidencias esperadas |
| **Ataque demostrado** | Escritura FC6 de la consigna de 60 % a 95 % y FC5 de la bomba desde `172.28.0.66`, con el nivel por encima del 100 % | `03_escritura_setpoint`, frames 284–291, 954 y 959; respuesta favorable del PLC; cambio observable en las lecturas del HMI y `NivelAlto=SI` |

La distinción es relevante para no atribuir al laboratorio resultados que no se obtuvieron. T0842, T0836 y T0855 se demuestran con captura; T0861 de forma parcial (Unit ID, bloque de direcciones y patrón de lectura, con nombres contrastados); T0831 es la consecuencia observada; T0830 y T0832 quedan como posibles y así se declaran.

## 5.9. Limitaciones

- **T0830 no se reprodujo.** La red *bridge* de Docker Desktop aísla o filtra el ARP, por lo que el *spoofing* no se completó. Se describe como técnicamente posible, con sus condiciones y evidencias esperadas.
- **Punto de captura privilegiado.** La captura en el PLC ve todo el tráfico por construcción; no equivale a la posición de un atacante externo. El *sidecar* del HMI solo ofrece la vista del HMI.
- **Proceso simulado.** No hay PLC físico, red industrial real, requisitos de tiempo real ni SIS independiente; las consecuencias se analizan sobre el modelo, no sobre una planta.
- **Semántica de los tags.** Los nombres `LT-101`, `SP-101`, etc. son una interpretación del mapa documentado en `laboratorio/README.md`. Modbus solo transporta direcciones y valores; por eso T0861 se clasifica como parcial.
- **Versión de ATT&CK.** El catálogo se consultó el 27/11/2026. T0855 se cita con su correspondencia actual T1692.001; si el profesor exige una única nomenclatura, debe mantenerse la de la versión consultada.

## 5.10. Fuentes consultadas

- MITRE ATT&CK for ICS, *T0842 Network Sniffing*, consultado el 27/11/2026, https://attack.mitre.org/techniques/T0842/
- MITRE ATT&CK for ICS, *T0861 Point & Tag Identification*, consultado el 27/11/2026, https://attack.mitre.org/techniques/T0861/
- MITRE ATT&CK for ICS, *T0836 Modify Parameter*, consultado el 27/11/2026, https://attack.mitre.org/techniques/T0836/
- MITRE ATT&CK for ICS, *T0830 Adversary-in-the-Middle*, consultado el 27/11/2026, https://attack.mitre.org/techniques/T0830/
- MITRE ATT&CK for ICS, *T1692.001 Unauthorized Message: Command Message*, consultado el 27/11/2026, https://attack.mitre.org/techniques/T1692/001/
- MITRE ATT&CK for ICS, *T0831 Manipulation of Control* y *T0832 Manipulation of View*, consultado el 27/11/2026, https://attack.mitre.org/techniques/T0831/ y https://attack.mitre.org/techniques/T0832/
