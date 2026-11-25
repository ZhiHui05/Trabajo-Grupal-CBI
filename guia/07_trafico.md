# 7. Análisis del tráfico

> Esta sección es el corazón del bloque 4.2. La idea no es enseñar Wireshark, sino demostrar que se entiende qué viaja por la red y qué implica para el proceso.

## 7.1. Tabla de participantes

Incluye una tabla como esta, completada con tus datos reales:

| Rol | Hostname | IP | MAC | Puerto | Protocolo | Función |
|---|---|---|---|---|---|---|
| PLC | `plc` | 172.28.0.10 | `02:42:ac:1c:00:0a` | 502/TCP | Modbus/TCP | Servidor de datos y lógica |
| HMI | `hmi` | 172.28.0.11 | `02:42:ac:1c:00:0b` | Efímero | Modbus/TCP | Cliente, supervisión y mando |
| Captura principal | `plc` (tcpdump) | 172.28.0.10 | — | — | — | Captura de todo el tráfico del PLC (HMI y atacante) |
| Captura HMI (opcional) | `capture` | Comparte HMI | — | — | — | Vista del HMI; no ve al atacante |
| Atacante | `attacker` | 172.28.0.66 | `02:42:ac:1c:00:42` | Efímero | Modbus/TCP | Lectura/escritura no autorizada |

Las MAC de Docker pueden variar; si las incluyes, cópialas de la captura real, no las inventes.

## 7.2. Anatomía de un mensaje Modbus/TCP

Un mensaje Modbus/TCP tiene dos partes:

```text
┌──────────────────────── MBAP header (7 bytes) ────────────────────────┐
│ Transaction ID (2) │ Protocol ID (2) │ Length (2) │ Unit ID (1)        │
├────────────────────────────────────────────────────────────────────────┤
│ Function Code (1) │ Data (N bytes)                                     │
└────────────────────────────── PDU ─────────────────────────────────────┘
```

| Campo | Tamaño | Ejemplo | Interpretación |
|---|---:|---|---|
| Transaction ID | 2 bytes | `00 01` | Identificador de la transacción; el servidor lo devuelve en la respuesta |
| Protocol ID | 2 bytes | `00 00` | 0 para Modbus |
| Length | 2 bytes | `00 06` | Número de bytes que siguen: Unit ID + PDU |
| Unit ID | 1 byte | `01` | Identificador del esclavo; no es autenticación |
| Function Code | 1 byte | `03` | Operación solicitada |
| Data | N bytes | `00 00 00 04` | Dirección inicial y cantidad, o valores |

Los valores de 16 bits se codifican en **big-endian**: `00 7B` = 123.

## 7.3. Operaciones representativas

> Los bytes siguientes son ejemplos coherentes con el laboratorio. Sustitúyelos por los de tu captura real y referencia los frames exactos.

### Operación A — El HMI lee nivel, temperatura, consigna y velocidad (FC3)

**Contexto:** el HMI consulta cada segundo los registros de retención 0–3.

**Filtro Wireshark:** `modbus.func_code == 3 && ip.src == 172.28.0.11`

**Petición:**

```text
00 01 00 00 00 06 01 03 00 00 00 04
```

| Campo | Bytes | Valor | Interpretación |
|---|---|---|---|
| Transaction ID | `00 01` | 1 | Transacción 1 |
| Protocol ID | `00 00` | 0 | Modbus |
| Length | `00 06` | 6 | Unit ID + PDU |
| Unit ID | `01` | 1 | PLC |
| Function Code | `03` | 3 | Leer holding registers |
| Start Address | `00 00` | 0 | HR 0 (40001) |
| Quantity | `00 04` | 4 | HR 0–3 |

**Respuesta:**

```text
00 01 00 00 00 0B 01 03 08 00 7B 00 FA 00 3C 05 AA
```

| Campo | Bytes | Valor | Interpretación |
|---|---|---|---|
| Transaction ID | `00 01` | 1 | Coincide con la petición |
| Protocol ID | `00 00` | 0 | Modbus |
| Length | `00 0B` | 11 | Unit ID + PDU |
| Unit ID | `01` | 1 | PLC |
| Function Code | `03` | 3 | Leer holding registers |
| Byte Count | `08` | 8 | 4 registros × 2 bytes |
| HR 0 | `00 7B` | 123 | Nivel = 12,3 % |
| HR 1 | `00 FA` | 250 | Temperatura = 25,0 °C |
| HR 2 | `00 3C` | 60 | Consigna = 60 % |
| HR 3 | `05 AA` | 1450 | Velocidad = 1450 rpm |

**Qué demuestra:** el proceso se puede leer sin credenciales y los valores viajan en claro. Un atacante que vea este tráfico conoce el estado completo del depósito.

### Operación B — El HMI cambia la consigna (FC6)

**Contexto:** el operador fija la consigna en 60 %.

**Filtro:** `modbus.func_code == 6 && ip.src == 172.28.0.11`

**Petición:**

```text
00 02 00 00 00 06 01 06 00 02 00 3C
```

| Campo | Bytes | Valor | Interpretación |
|---|---|---|---|
| Transaction ID | `00 02` | 2 | Transacción 2 |
| Length | `00 06` | 6 | Unit ID + PDU |
| Unit ID | `01` | 1 | PLC |
| Function Code | `06` | 6 | Escribir un registro |
| Address | `00 02` | 2 | HR 2 (40003) |
| Value | `00 3C` | 60 | Nueva consigna = 60 % |

**Respuesta:** el servidor repite la petición si la escritura es correcta:

```text
00 02 00 00 00 06 01 06 00 02 00 3C
```

**Qué demuestra:** una escritura es una petición más; no hay challenge-response, ni credencial, ni firma. Si el paquete llega, se ejecuta.

### Operación C — El HMI arranca la bomba (FC5)

**Petición:**

```text
00 03 00 00 00 06 01 05 00 00 FF 00
```

| Campo | Bytes | Valor | Interpretación |
|---|---|---|---|
| Transaction ID | `00 03` | 3 | Transacción 3 |
| Function Code | `05` | 5 | Escribir un coil |
| Address | `00 00` | 0 | CO 0 (00001) |
| Value | `FF 00` | ON | Bomba en marcha |

**Respuesta:** `00 03 00 00 00 06 01 05 00 00 FF 00`.

**Qué demuestra:** el mismo canal que lee datos también manda órdenes físicas. No hay separación entre lectura y escritura ni control de rol.

### Operación D — Escritura no autorizada desde el atacante (FC6 + FC5)

**Contexto:** el contenedor atacante, sin credenciales, escribe la consigna en 95 % y fuerza la bomba.

**Filtro:** `modbus.func_code == 6 || modbus.func_code == 5`

**Petición FC6:**

```text
00 10 00 00 00 06 01 06 00 02 00 5F
```

| Campo | Bytes | Valor | Interpretación |
|---|---|---|---|
| Transaction ID | `00 10` | 16 | Transacción del atacante |
| Unit ID | `01` | 1 | PLC |
| Function Code | `06` | 6 | Escribir un registro |
| Address | `00 02` | 2 | HR 2 (40003) |
| Value | `00 5F` | 95 | Consigna = 95 % |

**Petición FC5:**

```text
00 11 00 00 00 06 01 05 00 00 FF 00
```

**Respuesta del PLC:** ambas escrituras se confirman; el PLC no distingue al atacante del HMI.

**Qué demuestra:** la única condición para escribir es tener conectividad al puerto 502 y conocer la dirección. No hay autenticación, autorización ni integridad. La IP de origen es distinta a la del HMI (`172.28.0.66` frente a `172.28.0.11`), y aun así la escritura se acepta.

### Operación E — Respuesta de excepción (opcional)

Si se lee una dirección no válida, el PLC responde con el bit 0x80:

```text
00 20 00 00 00 03 01 83 02
```

| Campo | Valor | Interpretación |
|---|---|---|
| Function Code | `83` | 0x03 + 0x80: error en FC3 |
| Exception Code | `02` | Illegal Data Address |

**Qué demuestra:** el servidor valida direcciones, pero no identidades. Una excepción no es un control de seguridad.

## 7.4. Variables observadas

| Variable | Dirección | Valor de ejemplo | Unidad | Cómo se interpreta |
|---|---|---:|---|---|
| Nivel | HR 0 | 123 | 12,3 % | Valor/10 |
| Temperatura | HR 1 | 250 | 25,0 °C | Valor/10 |
| Consigna | HR 2 | 60 | 60 % | Valor directo |
| Velocidad | HR 3 | 1450 | 1450 rpm | Valor directo |
| Bomba | CO 0 | 1 | ON | Booleano |
| Nivel alto | DI 0 | 0 | NO | Booleano |
| Caudal | IR 0 | 600 | 60,0 L/min | Valor/10 |
| Presión | IR 1 | 50 | 5,0 bar | Valor/10 |

Explica en el informe cómo se pasó de los bytes a la variable física y cómo se verificó (por ejemplo, comparando con la pantalla del HMI o con los logs del PLC).

## 7.5. Presencia o ausencia de mecanismos de seguridad

| Mecanismo | ¿Presente? | Evidencia | Consecuencia |
|---|---|---|---|
| Autenticación de cliente | **No** | Cualquier IP conecta y lee/escribe | Suplantación de HMI o PLC |
| Autorización por rol | **No** | El atacante puede escribir lo mismo que el HMI | Escritura no autorizada |
| Cifrado | **No** | Valores y direcciones en texto claro | Confidencialidad nula |
| Integridad de mensajes | **No** | Sin MAC ni firma; el paquete se puede modificar | Manipulación |
| Protección contra replay | **No** | Transaction ID no es un nonce seguro | Repetición de comandos |
| Auditoría en el protocolo | **No** | No hay identidad ni registro de autor | Falta de trazabilidad |
| Segmentación de red | **No** (laboratorio) | Red plana 172.28.0.0/24 | Movimiento lateral |
| Límite de conexiones/rate limiting | **No** | Sin protección ante floods | DoS |
| TLS/Modbus Security | **No** | Se usa Modbus/TCP clásico en 502 | Todas las anteriores |

**Matiz importante:** Modbus/TCP Security (TLS, puerto 802) existe y mitiga confidencialidad e integridad, pero no está desplegado en el laboratorio. No digas “Modbus no puede cifrarse”; di “la variante clásica que hemos desplegado no lo hace y es la más habitual”.

## 7.6. Interpretación: qué puede hacer un atacante con esta visibilidad

Con los datos anteriores, un atacante con acceso a la red puede:

1. **Leer** el nivel, la temperatura, la consigna, la velocidad, el caudal y la presión.
2. **Inferir** el mapa de registros a partir de las peticiones del HMI.
3. **Escribir** consignas y comandos de bomba.
4. **Repetir** una escritura capturada (replay), aunque el Transaction ID cambie.
5. **Suplantar** al HMI o al PLC si consigue posicionarse (ARP spoofing).
6. **Ocultar** el efecto al operador si modifica las respuestas (MITM).
7. **Denegar** el servicio con un flood o agotando conexiones.

Esto no es un fallo de configuración aislado: es consecuencia del diseño del protocolo. Por eso las medidas deben ser **compensatorias** (segmentación, detección, autenticación en capas superiores, SIS independiente).

## 7.7. Cómo presentar la evidencia en el informe

Para cada operación, usa esta estructura:

1. **Pregunta:** “¿Qué envía el HMI para leer el nivel?”
2. **Filtro:** el filtro de Wireshark utilizado.
3. **Tabla de frames:** número de frame, tiempo, origen, destino, función, dirección, valor.
4. **Bytes:** petición y respuesta.
5. **Interpretación:** qué significa cada campo.
6. **Implicación de seguridad:** qué propiedad se ve afectada.
7. **Limitación:** qué no se puede concluir con esa evidencia.

Evita:

- Pegar una captura de pantalla sin explicar los campos.
- Enseñar 20 paquetes idénticos; elige uno representativo y di que se repite.
- Mezclar frames de capturas distintas sin indicarlo.
- Referenciar “el paquete del ataque” sin número de frame.

## 7.8. Checklist del bloque 4.2

- [ ] IP, puertos y participantes documentados.
- [ ] Mensajes característicos del protocolo explicados.
- [ ] Al menos dos operaciones representativas, una de ellas con modificación de datos.
- [ ] Variables del proceso identificadas y escaladas.
- [ ] Autenticación, cifrado e integridad evaluados con evidencia.
- [ ] PCAP original incluido y frames referenciados.
- [ ] Comandos de captura y condiciones documentados.
- [ ] Limitaciones del laboratorio explicadas.
- [ ] Capturas de pantalla usadas solo como apoyo.
