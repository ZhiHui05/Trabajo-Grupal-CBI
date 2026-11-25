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
