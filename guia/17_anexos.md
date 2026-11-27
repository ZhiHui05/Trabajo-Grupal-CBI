# 17. Anexos

## Anexo A — Referencia rápida de Modbus

**Function codes habituales**

| FC (hex) | Nombre | Uso |
|---|---|---|
| 0x01 | Read Coils | Leer salidas digitales |
| 0x02 | Read Discrete Inputs | Leer entradas digitales |
| 0x03 | Read Holding Registers | Leer registros de retención |
| 0x04 | Read Input Registers | Leer registros de entrada |
| 0x05 | Write Single Coil | Escribir una salida digital |
| 0x06 | Write Single Register | Escribir un registro |
| 0x0F | Write Multiple Coils | Escribir varias salidas |
| 0x10 | Write Multiple Registers | Escribir varios registros |
| 0x17 | Read/Write Multiple Registers | Leer y escribir en una transacción |
| 0x2B | Encapsulated Interface Transport | Interfaz encapsulada (MEI) |

**Códigos de excepción**

| Código | Nombre | Significado |
|---|---|---|
| 0x01 | Illegal Function | Función no soportada |
| 0x02 | Illegal Data Address | Dirección no válida |
| 0x03 | Illegal Data Value | Valor no válido |
| 0x04 | Server Device Failure | Fallo del dispositivo |
| 0x05 | Acknowledge | Petición aceptada, procesando |
| 0x06 | Server Device Busy | Dispositivo ocupado |
| 0x08 | Memory Parity Error | Error de paridad |
| 0x0A | Gateway Path Unavailable | Pasarela no disponible |
| 0x0B | Gateway Target Device Failed to Respond | Destino no responde |

**Convención de direcciones**

| Tipo | Notación tradicional | Dirección cero-based |
|---|---|---|
| Coils | 00001–09999 | 0–9998 |
| Discrete inputs | 10001–19999 | 0–9998 |
| Input registers | 30001–39999 | 0–9998 |
| Holding registers | 40001–49999 | 0–9998 |

En el código se usa `zero_mode=True`; por eso HR 0 = 40001. Si se usa `zero_mode=False`, hay que sumar 1. Documenta la convención para evitar errores.

**Puertos**

- Modbus/TCP: 502/TCP.
- Modbus/TCP Security (TLS): 802/TCP.
- Modbus RTU sobre TCP: 502/TCP (no confundir con RTU serie).

## Anexo B — Filtros de Wireshark

Archivo completo: `laboratorio/wireshark_filters.txt`.

Filtros imprescindibles:

```text
tcp.port == 502
modbus
modbus.func_code == 3
modbus.func_code == 6
modbus.func_code == 5
modbus.func_code == 16
modbus.exception_code
ip.addr == 172.28.0.10 && ip.addr == 172.28.0.11
modbus.func_code == 5 || modbus.func_code == 6 || modbus.func_code == 15 || modbus.func_code == 16
arp
```

Columnas recomendadas:

```text
frame.number
frame.time_relative
ip.src
ip.dst
tcp.srcport
tcp.dstport
modbus.func_code
modbus.reference_num
modbus.word_cnt
modbus.regval_uint16
modbus.bitval
modbus.write_reference_num
modbus.exception_code
```

## Anexo C — Plantillas de tablas

**Participantes**

| Rol | Hostname | IP | MAC | Puerto | Protocolo | Función |
|---|---|---|---|---|---|---|

**Operaciones**

| Nº | Frame | Tiempo rel. | Origen | Destino | FC | Operación | Dirección | Valor | Interpretación |
|---|---|---|---|---|---|---|---|---|---|

**Variables**

| Variable | Dirección | Tipo | FC | Valor observado | Unidad | Significado |
|---|---|---|---|---|---|---|

**Mecanismos de seguridad**

| Mecanismo | ¿Presente? | Evidencia | Consecuencia |
|---|---|---|---|

**Técnicas MITRE**

| ID | Técnica | Táctica | Condiciones | Evidencia | Consecuencia | Nivel |
|---|---|---|---|---|---|---|

**Riesgo**

| ID | Escenario | Activo | Amenaza | P | I | R | Prioridad |
|---|---|---|---|---:|---:|---:|---|
| S1 | | | | | | | |

**Controles**

| Medida | FR | Amenaza | Implementación | Validación | Riesgo residual |
|---|---|---|---|---|---|

## Anexo D — Comandos del starter kit

```bash
# Arranque
cd laboratorio
docker compose up -d --build

# Logs
docker compose logs -f plc
docker compose logs -f hmi

# HMI en modo operación (genera FC5/FC6)
docker compose exec hmi python hmi_client.py --host plc --operate

# Captura en el PLC (ve HMI y atacante)
docker compose exec plc tcpdump -i eth0 -s 0 -w /app/captures/01_baseline.pcapng 'tcp port 502'

# Escritura no autorizada
docker compose exec attacker python attack_write.py --host plc --setpoint 95 --pump on --read

# Restauración
docker compose exec attacker python attack_write.py --host plc --setpoint 60 --pump off

# Parada
docker compose down
```

## Anexo E — Glosario

| Término | Definición |
|---|---|
| **PLC** | Controlador lógico programable; ejecuta la lógica de control. |
| **HMI** | Interfaz humano-máquina; permite supervisar y operar. |
| **SCADA** | Sistema de supervisión y adquisición de datos. |
| **SIS** | Sistema instrumentado de seguridad; independiente del control básico. |
| **Modbus/TCP** | Protocolo cliente/servidor sobre TCP, puerto 502. |
| **MBAP** | Cabecera Modbus de aplicación (Transaction ID, Protocol ID, Length, Unit ID). |
| **PDU** | Unidad de datos del protocolo (Function Code + datos). |
| **FC** | Function Code; tipo de operación Modbus. |
| **HR** | Holding Register; registro de retención (lectura/escritura). |
| **IR** | Input Register; registro de entrada (solo lectura). |
| **Coil** | Salida digital booleana. |
| **Discrete Input** | Entrada digital booleana. |
| **MITM** | Adversary-in-the-Middle; intermediario que intercepta o modifica. |
| **ARP spoofing** | Falsificación de respuestas ARP para redirigir tráfico. |
| **Sniffing** | Captura pasiva de tráfico. |
| **IDS/IPS** | Sistema de detección/prevención de intrusiones. |
| **DPI** | Deep Packet Inspection; inspección profunda de paquetes. |
| **MFA** | Autenticación multifactor. |
| **DMZ** | Zona desmilitarizada; separa redes. |
| **SL-T** | Security Level Target; nivel de seguridad objetivo. |
| **FR** | Foundational Requirement de IEC 62443. |
| **PCAP** | Formato de captura de paquetes. |

## Anexo F — Matriz de riesgo

| P \ I | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|
| **5** | 5 | 10 | 15 | 20 | 25 |
| **4** | 4 | 8 | 12 | 16 | 20 |
| **3** | 3 | 6 | 9 | 12 | 15 |
| **2** | 2 | 4 | 6 | 8 | 10 |
| **1** | 1 | 2 | 3 | 4 | 5 |

**Escala de probabilidad**

| Valor | Criterio |
|---:|---|
| 1 | Muy improbable; requiere condiciones excepcionales |
| 2 | Improbable; posible a largo plazo |
| 3 | Posible; puede ocurrir |
| 4 | Probable; ocurrirá con facilidad |
| 5 | Casi seguro; condiciones habituales |

**Escala de impacto**

| Valor | Criterio |
|---:|---|
| 1 | Insignificante; sin efecto apreciable |
| 2 | Menor; molestias o pérdida pequeña |
| 3 | Moderado; parada breve o pérdida limitada |
| 4 | Mayor; parada prolongada, daño o riesgo |
| 5 | Severo; seguridad de personas, medio ambiente o pérdida grave |

---

# Cierre

Un buen trabajo no es el que tiene el laboratorio más complejo, sino el que **demuestra con evidencia** que entiende el protocolo, el proceso y las consecuencias. Si el grupo se queda corto de tiempo, recorta adornos, no análisis. Y si algo no se pudo demostrar, dilo: la honestidad técnica también se evalúa.
