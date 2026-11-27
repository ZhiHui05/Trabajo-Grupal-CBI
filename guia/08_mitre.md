# 8. MITRE ATT&CK for ICS

> Este bloque vale el 35 %. No es una lista de técnicas: es un análisis de cómo un adversario real se movería contra el escenario.

## 8.1. Método de trabajo

1. **Define el objetivo del adversario:** reconocer, recolectar, posicionarse, modificar, denegar.
2. **Identifica el comportamiento observable:** una lectura masiva, una escritura FC6, un ARP duplicado, un flood.
3. **Busca la técnica oficial** en MITRE ATT&CK for ICS y lee su página.
4. **Documenta las condiciones** que deben darse.
5. **Relaciona la técnica con el protocolo y la arquitectura** del laboratorio.
6. **Identifica evidencias** en el PCAP o en los logs.
7. **Analiza consecuencias** sobre el proceso.
8. **Declara el nivel de demostración:** observada, posible o demostrada.

## 8.2. Selección de técnicas

| ID | Técnica | Táctica | Relación con el escenario | Nivel en el trabajo |
|---|---|---|---|---|
| T0842 | Network Sniffing | Discovery | Captura del tráfico Modbus/TCP en texto claro | Demostrada |
| T0861 | Point & Tag Identification | Collection | Lectura de registros y inferencia del mapa de variables | Demostrada/parcial |
| T0830 | Adversary-in-the-Middle | Collection | ARP spoofing o proxy entre HMI y PLC | Posible o demostrada según el montaje |
| T0836 | Modify Parameter | Impair Process Control | Escritura FC6 de la consigna de nivel | Demostrada |
| T0855 | Unauthorized Command Message | Impair Process Control | Escritura FC5 de marcha de bomba | Demostrada |
| T0814 | Denial of Service | Inhibit Response Function | Flood TCP al puerto 502 | Opcional |
| T0831 | Manipulation of Control | Impact | Cambio del comportamiento físico tras la escritura | Consecuencia |
| T0832 | Manipulation of View | Impact | Modificación de respuestas FC3 para ocultar el nivel | Posible |

> **No confundas la táctica de ATT&CK con el “impacto” del enunciado.** En la versión actual de ATT&CK for ICS, T0842 es *Discovery*, T0861 es *Collection*, T0836 es *Impair Process Control* y T0814 es *Inhibit Response Function*. El bloque 4.4 del trabajo analiza el impacto sobre el proceso; la táctica *Impact* de ATT&CK es otra cosa (T0831 y T0832 sí pertenecen a ella). Cita la táctica correcta o, si prefieres simplificar, indica solo la técnica y su relación con el escenario.

> **Nota de versión (2026).** ATT&CK for ICS ha reestructurado algunas técnicas. La antigua T0855 *Unauthorized Command Message* aparece en la versión actual como **T1692.001 — Unauthorized Message: Command Message** (tácticas *Evasion* e *Impair Process Control*). El enunciado y muchos informes siguen usando T0855; si la citas, añade la correspondencia con T1692.001 y la fecha de consulta. Comprueba siempre la página oficial antes de entregar.

**Recomendación:** desarrollar en profundidad **T0842, T0861, T0836 y T0830**. Con cuatro técnicas bien hechas se cubre de sobra el mínimo de dos y se demuestra amplitud. T0855, T0814 y T0832 pueden mencionarse como apoyo o como trabajo futuro.

## 8.3. Fichas detalladas

### Ficha T0842 — Network Sniffing

| Campo | Contenido |
|---|---|
| **ID / nombre** | T0842 · Network Sniffing |
| **Táctica** | Discovery |
| **Descripción** | El adversario captura tráfico de red para obtener información del entorno industrial: topología, direcciones, protocolos, valores de proceso, consignas o material de autenticación. |
| **Condiciones** | Acceso a la red o a un punto de captura; interfaz en modo promiscuo, SPAN/mirror o compromiso de un host; tráfico sin cifrar; capacidad de ejecutar tcpdump/Wireshark. |
| **Relación con el escenario** | Modbus/TCP viaja en texto claro por el puerto 502. En el laboratorio, la captura en el PLC ve todas las peticiones y respuestas; el sidecar del HMI solo ve la vista del HMI. Un atacante externo necesitaría ARP spoofing, un puerto espejo o comprometer un host. |
| **Evidencias** | PCAP con peticiones y respuestas FC3/FC4/FC6; presencia de un host no inventariado; interfaz en promiscuo; ARP anómalo; aumento de tráfico. |
| **Consecuencias** | Pérdida de confidencialidad; el atacante obtiene el mapa de registros y las consignas; habilita T0861, T0836 y T0830. |
| **Demostración** | Captura con `docker compose exec plc tcpdump -i eth0 -s 0 -w ... 'tcp port 502'`; se muestran los valores de nivel, temperatura y consigna. |
| **Limitaciones** | La captura en el PLC es un punto de observación privilegiado, no un atacante externo. En una red bridge de Docker, el tráfico unicast no se difunde a todos los contenedores. Si se afirma sniffing externo, debe demostrarse con ARP spoofing, un proxy o un mirror. |
| **Fuente** | MITRE ATT&CK for ICS, T0842, consultado el [fecha], https://attack.mitre.org/techniques/T0842/ |

### Ficha T0861 — Point & Tag Identification

| Campo | Contenido |
|---|---|
| **ID / nombre** | T0861 · Point & Tag Identification |
| **Táctica** | Collection |
| **Descripción** | El adversario recopila información sobre los dispositivos y sus puntos/tags para identificar componentes, funciones y variables del sistema de control. |
| **Condiciones** | Acceso a la red o a documentación del proyecto; capacidad de consultar el PLC/HMI; ausencia de autenticación; nombres de tags o mapa de registros accesible. |
| **Relación con el escenario** | Modbus no transporta nombres de tags, pero el patrón de polling del HMI revela qué direcciones se usan. El atacante puede leer HR 0–11 y correlacionar los valores con el comportamiento del proceso. |
| **Evidencias** | Lecturas secuenciales de direcciones; escaneo de Unit IDs; peticiones a funciones no usadas; acceso a archivos de proyecto del HMI; picos de lectura. |
| **Consecuencias** | Conocimiento del proceso y de las variables críticas; permite seleccionar la consigna o el comando más efectivo; pérdida de confidencialidad. |
| **Demostración** | Script de lectura de HR 0–11; tabla de direcciones, valores y correlación con nivel/temperatura/consigna/velocidad. |
| **Limitaciones** | Los nombres `LT-101`, `SP-101`, etc. son una interpretación nuestra; el protocolo solo tiene direcciones. Hay que decirlo para no atribuir al protocolo una semántica que no tiene. |
| **Fuente** | MITRE ATT&CK for ICS, T0861, consultado el [fecha], https://attack.mitre.org/techniques/T0861/ |

### Ficha T0830 — Adversary-in-the-Middle

| Campo | Contenido |
|---|---|
| **ID / nombre** | T0830 · Adversary-in-the-Middle |
| **Táctica** | Collection |
| **Descripción** | El adversario se posiciona entre dos o más dispositivos para interceptar, modificar o reenviar tráfico. |
| **Condiciones** | Misma red o segmento; capacidad de ARP/DNS spoofing, rogue gateway o control de un nodo intermedio; tráfico sin cifrar ni autenticación mutua; IP forwarding. |
| **Relación con el escenario** | HMI y PLC confían en la red. Un ARP spoofing permite al atacante hacerse pasar por el PLC ante el HMI (y viceversa), ver todo el tráfico y modificar respuestas FC3 para ocultar el nivel. |
| **Evidencias** | Respuestas ARP no solicitadas o duplicadas; cambio de MAC asociada a una IP; latencia anómala; tráfico que pasa por un host no inventariado; discrepancias entre HMI y PLC. |
| **Consecuencias** | Manipulación de la vista y del control; comandos falsos; datos falsos al operador; pérdida de integridad y confidencialidad; impacto en seguridad. |
| **Demostración** | ARP spoofing con `arpspoof`/`bettercap` y captura en el atacante; o proxy TCP entre HMI y PLC. Si no se reproduce en Docker, se documenta como técnicamente posible. |
| **Limitaciones** | Docker Desktop puede filtrar ARP; el resultado depende del entorno. No afirmar una demostración que no se tiene. |
| **Fuente** | MITRE ATT&CK for ICS, T0830, consultado el [fecha], https://attack.mitre.org/techniques/T0830/ |

### Ficha T0836 — Modify Parameter

| Campo | Contenido |
|---|---|
| **ID / nombre** | T0836 · Modify Parameter |
| **Táctica** | Impair Process Control |
| **Descripción** | El adversario modifica parámetros del sistema de control (consignas, umbrales, ganancias PID, límites de alarma) para alterar el comportamiento del proceso. |
| **Condiciones** | Capacidad de escritura en el controlador; conocimiento de la dirección del parámetro; ausencia de autenticación/autorización; conectividad al puerto 502. |
| **Relación con el escenario** | La consigna de nivel está en HR 2 (40003) y se escribe con FC6. El atacante la cambia de 60 % a 95 % y fuerza la bomba con FC5. |
| **Evidencias** | Petición FC6 desde una IP distinta al HMI; cambio del valor de HR 2; subida del nivel; activación de LS-101; alarma en el HMI. |
| **Consecuencias** | Desbordamiento, vertido, cavitación, parada, pérdida de calidad, riesgo para personas y medio ambiente. |
| **Demostración** | `attack_write.py --setpoint 95 --pump on`; PCAP con FC6/FC5; logs del PLC/HMI; subida del nivel por encima del 90 %. |
| **Limitaciones** | El proceso es simulado y no hay SIS independiente. En una planta real, un SIS podría limitar el impacto; eso se analiza en las medidas de protección. |
| **Fuente** | MITRE ATT&CK for ICS, T0836, consultado el [fecha], https://attack.mitre.org/techniques/T0836/ |

### Fichas complementarias (opcionales)

**T0855 — Unauthorized Command Message**

| Campo | Contenido |
|---|---|
| **ID / nombre** | T0855 · Unauthorized Command Message |
| **Táctica** | Impair Process Control |
| **Descripción** | El adversario envía comandos no autorizados a activos del sistema de control para que ejecuten acciones fuera de su diseño previsto. |
| **Condiciones** | Acceso a la red, protocolo sin autenticación, conocimiento del comando y de la dirección. |
| **Relación** | FC5 sobre CO 0 arranca o para la bomba; FC6 sobre HR 3 cambia la velocidad. |
| **Evidencias** | FC5/FC6 desde una IP no autorizada; cambio de estado de la bomba; efecto en caudal/presión. |
| **Consecuencias** | Actuación no autorizada, desbordamiento, parada, daño mecánico. |
| **Demostración** | `attack_write.py --pump on`; comparación del estado de la bomba antes/después. |
| **Nota de versión** | En ATT&CK v19 (2026) se corresponde con T1692.001 *Unauthorized Message: Command Message*. Se mantiene T0855 como referencia histórica. |
| **Fuente** | https://attack.mitre.org/techniques/T1692/001/ (y legado https://attack.mitre.org/techniques/T0855/) |

**T0814 — Denial of Service**

| Campo | Contenido |
|---|---|
| **ID / nombre** | T0814 · Denial of Service |
| **Táctica** | Inhibit Response Function |
| **Descripción** | El adversario interrumpe la operación mediante flooding, agotamiento de recursos o paquetes malformados. |
| **Condiciones** | Acceso a la red, servicio expuesto, ausencia de rate limiting o protección. |
| **Relación** | Flood TCP al puerto 502; agotamiento de conexiones del PLC; timeouts del HMI. |
| **Evidencias** | Aumento de SYN; timeouts; alarmas de comunicación; caída de la respuesta del PLC. |
| **Consecuencias** | Pérdida de visibilidad y control; parada de producción; posible recuperación manual. |
| **Demostración** | Opcional, con límite de duración y solo en la red aislada. |
| **Fuente** | https://attack.mitre.org/techniques/T0814/ |

**T0831 — Manipulation of Control**

| Campo | Contenido |
|---|---|
| **ID / nombre** | T0831 · Manipulation of Control |
| **Táctica** | Impact |
| **Descripción** | El adversario manipula el proceso físico cambiando salidas del controlador o valores de sensores. |
| **Relación** | Es el efecto de T0836/T0855: la bomba y el nivel cambian. |
| **Evidencias** | Desviación del nivel, estado de la bomba, alarmas. |
| **Consecuencias** | Daño físico, vertido, parada, riesgo de seguridad. |
| **Fuente** | https://attack.mitre.org/techniques/T0831/ |

**T0832 — Manipulation of View**

| Campo | Contenido |
|---|---|
| **ID / nombre** | T0832 · Manipulation of View |
| **Táctica** | Impact |
| **Descripción** | El adversario manipula la información que ve el operador para ocultar cambios o mostrar un estado falso. |
| **Relación** | Un MITM podría reescribir las respuestas FC3 para que el HMI muestre un nivel normal mientras el depósito se llena. |
| **Evidencias** | Discrepancia entre HMI y medidor local; datos incoherentes en el historian; tráfico manipulado. |
| **Consecuencias** | El operador no reacciona; se retrasa la respuesta; riesgo de desbordamiento. |
| **Fuente** | https://attack.mitre.org/techniques/T0832/ |

## 8.4. Cadena de ataque

| Fase | Técnica | Acción del atacante | Evidencia en el laboratorio |
|---|---|---|---|
| Reconocimiento | T0861 | Leer registros y deducir variables | PCAP de lecturas HR 0–11 |
| Recolección | T0842 | Capturar tráfico HMI–PLC | PCAP con FC3/FC6 |
| Posicionamiento | T0830 | ARP spoofing o proxy | ARP/PCAP, tablas ARP |
| Acción | T0836 / T0855 | Escribir consigna y arrancar bomba | FC6/FC5 desde 172.28.0.66 |
| Efecto | T0831 / T0832 | Cambia el proceso o se oculta | Nivel > 90 %, alarma, HMI |
| Impacto | — | Desbordamiento, parada, vertido | Logs, estado del proceso |

Esta tabla demuestra que las técnicas no son independientes: se encadenan. Es exactamente lo que pide el enunciado cuando habla de “relación con el protocolo o la arquitectura”.

> **Matiz:** las fases de la tabla son una simplificación didáctica del ataque, no las tácticas oficiales de ATT&CK. Por ejemplo, T0861 pertenece a *Collection* y T0842 a *Discovery*, aunque aquí se presenten como “reconocimiento” y “recolección” en sentido amplio. Si el profesor es estricto con la terminología, usa la táctica oficial en las fichas y reserva esta tabla para la narrativa.

## 8.5. Vulnerabilidad, ataque posible y ataque demostrado

| Nivel | Ejemplo en este trabajo | Cómo se justifica |
|---|---|---|
| **Vulnerabilidad observada** | Modbus/TCP no autentica ni cifra; el puerto 502 es accesible desde la red del laboratorio | Se ve en el PCAP y en la configuración |
| **Ataque técnicamente posible** | MITM con ARP spoofing para modificar respuestas FC3; replay de comandos; DoS | Se apoya en el protocolo y en herramientas conocidas, aunque no se haya reproducido |
| **Ataque demostrado** | Escritura FC6 de la consigna y FC5 de la bomba desde el atacante | PCAP, logs y cambio observable del proceso |

Incluye esta tabla en el informe. Es una forma directa de cumplir el requisito de diferenciación.

## 8.6. Plantilla de ficha para el informe

```text
Técnica: [ID] — [Nombre]
Táctica: [táctica]
Descripción: [qué hace el adversario, en 2–3 frases]
Condiciones: [qué necesita para tener éxito]
Relación con el escenario: [protocolo, arquitectura, variable o comunicación concreta]
Evidencias: [qué se vería en el PCAP, logs o proceso]
Consecuencias: [qué efecto tendría sobre disponibilidad, integridad, seguridad, calidad]
Demostración: [qué se hizo en el laboratorio y con qué resultado]
Limitaciones: [qué no se pudo demostrar y por qué]
Fuente: [URL de MITRE, fecha de consulta]
```

## 8.7. Errores típicos en este bloque

| Error | Corrección |
|---|---|
| Copiar la descripción de MITRE y nada más | Añadir condiciones, evidencias y consecuencias propias |
| Elegir técnicas que no tienen relación con el escenario | Partir de las comunicaciones observadas, no de una lista |
| Mezclar T0836 con T0831 | T0836 es la modificación del parámetro; T0831 es el efecto sobre el control |
| Decir “hemos demostrado MITM” sin captura | Distinguir demostrado / posible |
| No citar la versión o fecha de consulta | Añadir “consultado el DD/MM/AAAA” |
| Ignorar la táctica | Incluirla; ayuda a situar la técnica en la cadena |

## 8.8. Cómo citar MITRE

Ejemplo:

> MITRE ATT&CK for ICS, *T0836 Modify Parameter*, consultado el 15/11/2026, https://attack.mitre.org/techniques/T0836/.

Si el profesor pide un estilo concreto (APA, IEEE), adáptalo. Lo importante es que la fuente sea verificable y que la fecha de consulta esté clara.
