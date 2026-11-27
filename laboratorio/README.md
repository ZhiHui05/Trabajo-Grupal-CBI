# Laboratorio Modbus/TCP — Ciberseguridad Industrial

Laboratorio mínimo, reproducible y **deliberadamente inseguro** para el trabajo en grupo de Ciberseguridad Industrial (curso 2026/27).

> **Uso exclusivamente académico y en red aislada.** No ejecutes los scripts de ataque contra equipos que no sean tuyos o sobre los que no tengas autorización expresa.

El laboratorio se puede levantar de dos formas:

- **Modo modular (recomendado):** un Compose y un Dockerfile por componente en `plc/`, `hmi/`, `capture/` y `attacker/`. Se gestiona con `lab.ps1` (Windows) o `docker_composer` (Linux/macOS).
- **Modo `compose.yml` único:** los cuatro servicios en un solo Compose con una imagen común (`Dockerfile` raíz) y los scripts de la raíz de `laboratorio/`. Es el que usa `scan_recon.py` (reconocimiento, T0861). Ver [Modo alternativo](#modo-alternativo-composeyml-único).

> **Ojo con la captura:** en el modo modular, `capture` comparte el namespace del **PLC** y ve todo el tráfico, incluido el del atacante. En el modo único, el servicio `capture` comparte el namespace del **HMI** y **no** ve el tráfico del atacante; allí la captura completa se hace en el contenedor del PLC. Indicad en la memoria qué modo y qué punto de captura se ha usado en cada PCAP.

## Contenido

| Archivo | Función |
|---|---|
| `plc/` | PLC: código, Compose y Dockerfile propios. |
| `hmi/` | HMI/SCADA: código, Compose y Dockerfile propios. |
| `capture/` | Captura: Compose, Dockerfile, utilidad tcpdump, captura en directo (`stream_capture.py`) y directorio de PCAP propios. Comparte la red del PLC para observar su tráfico. |
| `attacker/` | Cliente de demostración: código, Compose y Dockerfile propios. |
| `requirements.txt` | Dependencia Python común de los módulos PLC, HMI y atacante. |
| `modbus_map.py` | Direcciones Modbus compartidas por PLC, HMI y atacante. |
| `plc/process_model.py` | Modelo aislado de la simulación del proceso. |
| `tests/` | Pruebas unitarias del modelo del proceso y de la captura en directo. |
| `cambios.md` | Historial de modificaciones respecto al proyecto inicial. |
| `PUESTA_EN_MARCHA.md` | Guía para iniciar cada contenedor por separado o todo el laboratorio. |
| `lab.ps1` | Automatiza el ciclo completo en Windows PowerShell (modo modular). |
| `docker_composer` | Automatiza el ciclo completo en Linux/macOS o Podman (modo modular). |
| `wireshark_filters.txt` | Filtros y columnas recomendadas para Wireshark. |
| `compose.yml` | Modo único: PLC, HMI, captura y atacante en una red Docker aislada (`ics_net`). |
| `Dockerfile` | Modo único: imagen común con Python, PyModbus, tcpdump y utilidades de red. |
| `plc_server.py`, `hmi_client.py`, `attack_write.py`, `capture.sh` | Modo único: versiones de los scripts que monta el `compose.yml` raíz. |
| `scan_recon.py` | Reconocimiento Modbus/TCP (T0861): sondea Unit IDs, lee el mapa de registros y genera CSV/Markdown. |

## Requisitos

- Docker Desktop (Windows/macOS) o Docker Engine + Compose (Linux), o Podman con `podman compose`.
- Wireshark instalado en el equipo anfitrión (para analizar los PCAP).
- 2 GB de RAM libre y unos 500 MB de disco.
- En Windows, Docker Desktop con backend WSL2.

Ejecuta las pruebas unitarias con Python 3.12:

```bash
python -m unittest discover -s tests -v
```

## Arranque rápido (modo modular)

```bash
cd laboratorio
sh docker_composer up
sh docker_composer status
docker compose -f plc/compose.yml logs -f plc
```

Con Podman, usa `CONTAINER_CLI=podman sh docker_composer up`.

En Windows PowerShell:

```powershell
cd laboratorio
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

Los PCAP quedan en `laboratorio/capture/captures/` (Git los ignora). Copia a `evidencias/pcaps/` los que cites en la memoria y regístralos en `evidencias/MANIFEST.md`.
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

## Modo alternativo: `compose.yml` único

Levanta los cuatro servicios desde la raíz de `laboratorio/`:

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

Para generar tráfico de escritura desde el HMI:

```bash
docker compose exec hmi python hmi_client.py --host plc --operate
```

### Capturar tráfico

La captura más completa se hace **en el contenedor del PLC**: ve todas las peticiones y respuestas de todos los clientes (HMI y atacante), porque todo el tráfico pasa por él.

```bash
docker compose exec plc tcpdump -i eth0 -s 0 -w /app/captures/01_baseline.pcapng 'tcp port 502'
# Detener con Ctrl+C
```

También existe el servicio `capture`, que comparte el namespace del HMI y sirve para ver la perspectiva del HMI. **No ve el tráfico del atacante** (es otro contenedor y otro namespace), así que no lo uses como única fuente para la escritura no autorizada.

Los PCAP quedan en `laboratorio/captures/` (Git los ignora). Copia a `evidencias/pcaps/` los que cites en la memoria y regístralos en `evidencias/MANIFEST.md`.

### Reconocimiento (T0861)

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

### Escritura no autorizada

```bash
docker compose exec attacker python attack_write.py --host plc --setpoint 95 --pump on
```

Para restaurar:

```bash
docker compose exec attacker python attack_write.py --host plc --setpoint 60 --pump off
```

### Parar

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
| `failed to create mountpoint ... read-only file system` | El montaje de un módulo sobre `/app` oculta la ruta del mapa compartido | Usa los Compose incluidos: montan cada módulo bajo `/app/<módulo>` y el mapa por separado. |
| `network cbi-modbus-ics not found` | La red compartida no fue creada (modo modular) | Ejecuta `sh docker_composer up` o `.\lab.ps1 up` para crearla. |
| `port is already allocated` | Puerto 502 ocupado en el host | Los Compose no publican 502; si descomentaste `ports`, cambia a `1502:502`. |
| El HMI no conecta | PLC aún no listo | Espera al healthcheck y revisa los logs del PLC (`docker compose -f plc/compose.yml logs plc` o `docker compose logs plc`). |
| `tcpdump: permission denied` | Faltan capacidades | Los servicios de captura (y el PLC en el modo único) incluyen `NET_RAW` y `NET_ADMIN`; no ejecutes tcpdump en un contenedor sin ellas. |
| No aparece tráfico en el PCAP | Interfaz incorrecta | Ejecuta `ip addr` dentro del contenedor y usa la interfaz correcta (`eth0`). |
| El módulo `capture` deja de capturar | Se reinició o recreó el contenedor cuyo namespace comparte | Modular: `docker compose -f capture/compose.yml up -d --force-recreate capture`. Modo único: `docker compose restart capture`. |
| `scan_recon.py` no se encuentra en el atacante | El atacante modular solo incluye `attack_write.py` | Usa el modo `compose.yml` único para el reconocimiento. |
| ARP spoofing no funciona | Limitación de la red bridge de Docker | Usa un proxy TCP, máquinas virtuales o documenta la técnica como “técnicamente posible” y no como demostrada. |
| Error de versión de PyModbus | Versión distinta a la fijada | Usa `pymodbus==3.7.4`, fijada en el `requirements.txt` común. |

## Nota sobre el alcance

Este laboratorio reproduce un proceso muy simplificado. No incluye un Safety Instrumented System (SIS) independiente, PLC real, red industrial real ni requisitos de tiempo real. Por tanto, los resultados sirven para **comprender y demostrar** debilidades del protocolo y justificar medidas, no para certificar una instalación real.
