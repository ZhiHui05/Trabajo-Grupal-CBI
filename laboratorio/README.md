# Laboratorio Modbus/TCP — Ciberseguridad Industrial

Laboratorio mínimo, reproducible y **deliberadamente inseguro** para el trabajo en grupo de Ciberseguridad Industrial (curso 2026/27).

> **Uso exclusivamente académico y en red aislada.** No ejecutes los scripts de ataque contra equipos que no sean tuyos o sobre los que no tengas autorización expresa.

## Contenido

| Archivo | Función |
|---|---|
| `compose.yml` | Define PLC, HMI, captura y atacante en una red Docker aislada. |
| `Dockerfile` | Imagen común con Python, PyModbus, tcpdump y utilidades de red. |
| `plc_server.py` | PLC virtual Modbus/TCP con simulación de nivel, temperatura, bomba y alarmas. |
| `hmi_client.py` | HMI/SCADA que consulta variables y, opcionalmente, escribe consignas y comandos. |
| `attack_write.py` | Cliente Modbus que escribe una consigna y/o fuerza la bomba (demostración de escritura no autorizada). |
| `scan_recon.py` | Reconocimiento Modbus/TCP (T0861): sondea Unit IDs, lee el mapa de registros y genera CSV/Markdown. |
| `capture.sh` | Ayuda para capturar tráfico con tcpdump dentro de un contenedor (PLC o `capture`). |
| `wireshark_filters.txt` | Filtros y columnas recomendadas para Wireshark. |

## Requisitos

- Docker Desktop (Windows/macOS) o Docker Engine + Compose (Linux), o Podman con `podman compose`.
- Wireshark instalado en el equipo anfitrión (para analizar los PCAP).
- 2 GB de RAM libre y unos 500 MB de disco.
- En Windows, Docker Desktop con backend WSL2.

## Arranque rápido

```bash
cd laboratorio
docker compose up -d --build
docker compose ps
docker compose logs -f plc
```

En otra terminal:

```bash
docker compose logs -f hmi
```

El HMI arranca en modo monitor. Para generar tráfico de escritura (consigna y bomba), ejecuta un segundo proceso **dentro del mismo contenedor HMI**; así el sidecar de captura ve también sus escrituras:

```bash
docker compose exec hmi python hmi_client.py --host plc --operate
```

Deténlo con `Ctrl+C` cuando termines la captura. Para el experimento de ataque, déjalo parado y usa solo el HMI en modo monitor.

## Capturar tráfico

La captura más completa se hace **en el contenedor del PLC**: ve todas las peticiones y respuestas de todos los clientes (HMI y atacante), porque todo el tráfico pasa por él.

```bash
docker compose exec plc tcpdump -i eth0 -s 0 -w /app/captures/01_baseline.pcapng 'tcp port 502'
# Detener con Ctrl+C
```

También existe el servicio `capture`, que comparte el namespace del HMI y sirve para ver la perspectiva del HMI. **No ve el tráfico del atacante** (es otro contenedor y otro namespace), así que no lo uses como única fuente para la escritura no autorizada.

Los PCAP quedan en `laboratorio/captures/` (Git los ignora). Copia a `evidencias/pcaps/` los que cites en la memoria y regístralos en `evidencias/MANIFEST.md`.

## Reconocimiento (T0861)

Objetivo: demostrar cómo un cliente **sin credenciales** identifica el PLC, el Unit ID accesible y el mapa de registros (T0861, *Point & Tag Identification*). El script solo **lee**: no escribe coils ni registros.

Deja la captura en marcha en el contenedor del PLC, en otra terminal:

```bash
docker compose exec plc tcpdump -i eth0 -s 0 -w /app/captures/02_reconocimiento.pcapng 'tcp port 502'
```

Ejecuta el reconocimiento desde el contenedor atacante:

```bash
docker compose exec attacker python scan_recon.py --host plc
```

Qué hace:

- Comprueba que `502/tcp` está abierto y mide la latencia de conexión.
- Sondea los Unit IDs indicados en `--units` (por defecto `0-5,247`) leyendo HR 0 en cada uno.
- Con el primer Unit ID que responde, lee HR 0–11 **una a una** (pausa `--delay`, 0,15 s por defecto) y después CO 0–1, DI 0 e IR 0–1.
- Consulta HR 32 (`--probe-addr`) para forzar la excepción 0x02 (Illegal Data Address) y delimitar el bloque de direcciones válido.
- Genera en `--out-dir` (`.` por defecto) un `recon_<host>_<AAAAMMDD_HHMMSS>.csv` (UTF-8 con BOM, separador `;`) y un `.md` con la misma tabla.

> El contenedor `attacker` monta `./:/app`, así que `.` es `laboratorio/` en el host y los ficheros aparecen ahí directamente. Si prefieres dejarlos junto a los PCAP, usa `--out-dir /app/captures`; el `.gitignore` ya excluye `recon_*.csv` y `recon_*.md`.

| Opción | Por defecto | Uso |
|---|---|---|
| `--host` | `plc` | Host o IP del PLC. |
| `--port` | `502` | Puerto TCP de Modbus. |
| `--units` | `0-5,247` | Unit IDs a sondear (admite rangos y listas). |
| `--hr-count` | `12` | Holding registers a leer desde HR 0. |
| `--delay` | `0.15` | Pausa entre lecturas (s) para que el sondeo se vea en el PCAP. |
| `--probe-addr` | `32` | HR fuera del mapa para forzar la excepción. |
| `--timeout` | `1.5` | Timeout de conexión y de respuesta (s). |
| `--out-dir` | `.` | Directorio donde dejar el CSV y el Markdown. |
| `--raw` | desactivado | No usa el mapa conocido: muestra solo direcciones y valores crudos. |

Resultado esperado:

- Solo responde el Unit ID **1**; el resto devuelve excepción 0x0B (Gateway Target Failed to Respond).
- HR 0–3 corresponden a nivel, temperatura, consigna de nivel y consigna de velocidad, con la escala del [mapa de registros](#mapa-de-registros).
- HR 4–11 responden 0: el bloque tiene 32 posiciones y solo se usan las cuatro primeras.
- HR 32 devuelve excepción 0x02 (Illegal Data Address).
- El patrón es distinto al del HMI, que lee bloques de 4 registros cada segundo: aquí son lecturas individuales de 1 registro espaciadas ~0,15 s.

> **Nota:** los nombres de variable (`LT-101`, `TT-101`, etc.) son inferidos a partir del mapa del laboratorio. Modbus solo transporta direcciones y valores crudos; el significado se deduce del contexto y de la documentación del proceso.

## Provocar una escritura no autorizada

> Para que el HMI no revierta la escritura, no dejes en marcha el proceso `hmi_client.py --operate`; el servicio `hmi` por defecto solo monitoriza.

Con el PLC y el HMI en marcha:

```bash
docker compose exec attacker python attack_write.py --host plc --setpoint 95 --pump on
```

Observa en los logs del HMI cómo cambia la consigna y cómo sube el nivel. Para restaurar:

```bash
docker compose exec attacker python attack_write.py --host plc --setpoint 60 --pump off
```

## Parar y limpiar

```bash
docker compose down
```

## Mapa de registros

| Variable | Dirección | Tipo | FC | Escala | Quién escribe |
|---|---|---|---|---|---|
| `LT-101` Nivel | HR 0 (40001) | uint16 | 3 | valor/10 % | PLC |
| `TT-101` Temperatura | HR 1 (40002) | uint16 | 3 | valor/10 °C | PLC |
| `SP-101` Consigna de nivel | HR 2 (40003) | uint16 | 3/6 | % (0–100) | HMI / atacante |
| `PV-101` Consigna de velocidad | HR 3 (40004) | uint16 | 3/6 | rpm | HMI / atacante |
| `P-101` Marcha bomba | CO 0 (00001) | bool | 1/5 | 0/1 | HMI / atacante |
| `RESET` Reset alarma | CO 1 (00002) | bool | 1/5 | 0/1 | HMI |
| `LS-101` Nivel alto | DI 0 (10001) | bool | 2 | 0/1 | PLC |
| `FT-101` Caudal | IR 0 (30001) | uint16 | 4 | valor/10 L/min | PLC |
| `PT-101` Presión | IR 1 (30002) | uint16 | 4 | valor/10 bar | PLC |

## Problemas frecuentes

| Síntoma | Causa probable | Solución |
|---|---|---|
| `port is already allocated` | Puerto 502 ocupado en el host | El `compose.yml` no publica 502; si descomentaste `ports`, cambia a `1502:502`. |
| El HMI no conecta | PLC aún no listo | Espera al healthcheck o revisa `docker compose logs plc`. |
| `tcpdump: permission denied` | Faltan capacidades | El PLC y el servicio `capture` ya incluyen `NET_RAW`; no lo ejecutes en otro contenedor sin capacidades. |
| No aparece tráfico en el PCAP | Interfaz incorrecta | Ejecuta `ip addr` dentro del contenedor y usa la interfaz correcta (`eth0`). |
| El sidecar `capture` deja de capturar | Se reinició o recreó el HMI y cambió su namespace | `docker compose restart capture`. |
| ARP spoofing no funciona | Limitación de la red bridge de Docker | Usa un proxy TCP, máquinas virtuales o documenta la técnica como “técnicamente posible” y no como demostrada. |
| Error de versión de PyModbus | Versión distinta a la fijada | Usa `pymodbus==3.7.4` (incluido en `requirements.txt`). |

## Nota sobre el alcance

Este laboratorio reproduce un proceso muy simplificado. No incluye un Safety Instrumented System (SIS) independiente, PLC real, red industrial real ni requisitos de tiempo real. Por tanto, los resultados sirven para **comprender y demostrar** debilidades del protocolo y justificar medidas, no para certificar una instalación real.
