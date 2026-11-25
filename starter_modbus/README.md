# Laboratorio Modbus/TCP — Ciberseguridad Industrial

Laboratorio mínimo, reproducible y **deliberadamente inseguro** para el trabajo en grupo de Ciberseguridad Industrial (curso 2026/27).

> **Uso exclusivamente académico y en red aislada.** No ejecutes los scripts de ataque contra equipos que no sean tuyos o sobre los que no tengas autorización expresa.

## Contenido

| Archivo | Función |
|---|---|
| `plc/` | PLC: código, Compose y Dockerfile propios. |
| `hmi/` | HMI/SCADA: código, Compose y Dockerfile propios. |
| `capture/` | Captura: Compose, Dockerfile, utilidad tcpdump y directorio de PCAP propios. Comparte la red del PLC para observar su tráfico. |
| `attacker/` | Cliente de demostración: código, Compose y Dockerfile propios. |
| `requirements.txt` | Dependencia Python común de los módulos PLC, HMI y atacante. |
| `modbus_map.py` | Direcciones Modbus compartidas por PLC, HMI y atacante. |
| `plc/process_model.py` | Modelo aislado de la simulación del proceso. |
| `tests/` | Pruebas unitarias del modelo del proceso. |
| `cambios.md` | Historial de modificaciones respecto al proyecto inicial. |
| `PUESTA_EN_MARCHA.md` | Guía para iniciar cada contenedor por separado o todo el laboratorio. |
| `lab.ps1` | Automatiza el ciclo completo en Windows PowerShell. |
| `docker_composer` | Automatiza el ciclo completo en Linux/macOS o Podman. |
| `wireshark_filters.txt` | Filtros y columnas recomendadas para Wireshark. |

## Requisitos

- Docker Desktop (Windows/macOS) o Docker Engine + Compose (Linux), o Podman con `podman compose`.
- Wireshark instalado en el equipo anfitrión (para analizar los PCAP).
- 2 GB de RAM libre y unos 500 MB de disco.
- En Windows, Docker Desktop con backend WSL2.

Ejecuta las pruebas unitarias con Python 3.12:

```bash
python -m unittest discover -s tests -v
```

## Arranque rápido

```bash
cd starter_modbus
sh docker_composer up
sh docker_composer status
docker compose -f plc/compose.yml logs -f plc
```

Con Podman, usa `CONTAINER_CLI=podman sh docker_composer up`.

En Windows PowerShell:

```powershell
cd starter_modbus
.\lab.ps1 up
.\lab.ps1 status
docker compose -f plc/compose.yml logs -f plc
```

El script crea la red compartida `cbi-modbus-ics`; `clean` la elimina.
El arranque espera a que el PLC esté saludable antes de iniciar los demás módulos.
Cada módulo puede iniciarse o detenerse por separado con su archivo Compose, después de crear la red
y, para `capture`, de iniciar el PLC (comparte su namespace de red). Para un arranque individual,
crea la red con `docker network create --driver bridge --subnet 172.28.0.0/24 cbi-modbus-ics`.

Por ejemplo, para levantar solo el PLC:

```bash
docker compose -f plc/compose.yml up -d --build
```

Los otros módulos se pueden arrancar con `hmi/compose.yml`, `attacker/compose.yml` o
`capture/compose.yml` (este último requiere que `cbi-plc` ya esté en ejecución).
Las IP y la subred predeterminadas se pueden cambiar con `PLC_IP`, `HMI_IP`, `ATTACKER_IP` y
`NETWORK_SUBNET`; las IP deben pertenecer a la subred elegida. Ejemplo en PowerShell:

```powershell
$env:NETWORK_SUBNET = "172.29.0.0/24"
$env:PLC_IP = "172.29.0.10"
$env:HMI_IP = "172.29.0.11"
$env:ATTACKER_IP = "172.29.0.66"
.\lab.ps1 up
```

En Linux/macOS, antepón esas variables a `sh docker_composer up`. Si ya existe la red con otra
subred, elimina primero el laboratorio con `clean` y vuelve a levantarlo.

```bash
NETWORK_SUBNET=172.29.0.0/24 PLC_IP=172.29.0.10 HMI_IP=172.29.0.11 ATTACKER_IP=172.29.0.66 sh docker_composer up 
```

En otra terminal:

```bash
docker compose -f hmi/compose.yml logs -f hmi
```

El HMI arranca en modo monitor. Para generar tráfico de escritura (consigna y bomba), ejecuta un segundo proceso **dentro del mismo contenedor HMI**; el módulo de captura, conectado al namespace del PLC, también verá esas escrituras:

```bash
docker compose -f hmi/compose.yml exec hmi python -m hmi.hmi_client --host plc --operate
```

Deténlo con `Ctrl+C` cuando termines la captura. Para el experimento de ataque, déjalo parado y usa solo el HMI en modo monitor.

## Capturar tráfico

El módulo `capture` comparte el namespace de red del PLC: por eso ve todas las peticiones y respuestas de los clientes HMI y atacante.

```bash
docker compose -f capture/compose.yml exec capture sh /app/capture.sh /captures/01_baseline.pcapng
# Detener con Ctrl+C
```

Los PCAP quedan en `starter_modbus/capture/captures/`.
Para ver los paquetes en directo en Wireshark, sigue la sección de captura en directo de [PUESTA_EN_MARCHA.md](PUESTA_EN_MARCHA.md).

## Provocar una escritura no autorizada

> Para que el HMI no revierta la escritura, no dejes en marcha el proceso `hmi_client.py --operate`; el servicio `hmi` por defecto solo monitoriza.

Con el PLC y el HMI en marcha:

```bash
docker compose -f attacker/compose.yml exec attacker python -m attacker.attack_write --host plc --setpoint 95 --pump on
```

Observa en los logs del HMI cómo cambia la consigna y cómo sube el nivel. Para restaurar:

```bash
docker compose -f attacker/compose.yml exec attacker python -m attacker.attack_write --host plc --setpoint 60 --pump off
```

## Parar y limpiar

```bash
sh docker_composer down
sh docker_composer clean
```

En Windows PowerShell:

```powershell
.\lab.ps1 down
.\lab.ps1 clean
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
| `failed to create mountpoint ... read-only file system` | El montaje de un módulo sobre `/app` oculta la ruta del mapa compartido | Usa los Compose incluidos: montan cada módulo bajo `/app/<módulo>` y el mapa por separado. |
| `network cbi-modbus-ics not found` | La red compartida no fue creada | Ejecuta `sh docker_composer up` o `.\lab.ps1 up` para crearla. |
| El HMI no conecta | PLC aún no listo | Espera a que el módulo PLC esté activo y revisa `docker compose -f plc/compose.yml logs plc`. |
| `tcpdump: permission denied` | Faltan capacidades | El módulo `capture` incluye las capacidades necesarias (`NET_RAW` y `NET_ADMIN`). |
| No aparece tráfico en el PCAP | Interfaz incorrecta | Ejecuta `ip addr` dentro del contenedor y usa la interfaz correcta (`eth0`). |
| El módulo `capture` deja de capturar | Se reinició o recreó el PLC y cambió su namespace | `docker compose -f capture/compose.yml up -d --force-recreate capture`. |
| ARP spoofing no funciona | Limitación de la red bridge de Docker | Usa un proxy TCP, máquinas virtuales o documenta la técnica como “técnicamente posible” y no como demostrada. |
| Error de versión de PyModbus | Versión distinta a la fijada | Usa `pymodbus==3.7.4`, fijada en el `requirements.txt` común. |

## Nota sobre el alcance

Este laboratorio reproduce un proceso muy simplificado. No incluye un Safety Instrumented System (SIS) independiente, PLC real, red industrial real ni requisitos de tiempo real. Por tanto, los resultados sirven para **comprender y demostrar** debilidades del protocolo y justificar medidas, no para certificar una instalación real.
