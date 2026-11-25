# 5. Diseño del laboratorio y reproducibilidad

## 5.1. Herramientas recomendadas

| Herramienta | Versión orientativa | Uso |
|---|---|---|
| Docker Desktop / Docker Engine + Compose | 4.x / 24.x o superior | Contenedores y red aislada |
| Podman + `podman compose` | 4.x/5.x | Alternativa a Docker |
| Python | 3.12 | Scripts del PLC, HMI y ataque |
| PyModbus | 3.7.4 (fijada) | Servidor y cliente Modbus/TCP |
| Wireshark | 4.x | Análisis de PCAP |
| tcpdump | 4.99+ | Captura dentro del contenedor |
| Git | 2.x | Control de versiones |
| Opcional: Scapy | 2.6+ | Manipulación de paquetes y MITM |
| Opcional: Suricata/Zeek | 7.x/6.x | Detección offline sobre PCAP |

Fija las versiones en `requirements.txt` y en el `Dockerfile`. Un trabajo reproducible no dice “funciona en mi máquina”; dice “con estas versiones y este comando, funciona en cualquier máquina”.

## 5.2. Estructura del repositorio

```text
trabajo-cbi/
├── README.md                 # Cómo reproducir el laboratorio
├── compose.yml               # Definición de servicios y red
├── Dockerfile                # Imagen común
├── requirements.txt          # Versiones fijadas
├── plc_server.py             # PLC virtual
├── hmi_client.py             # HMI/SCADA
├── attack_write.py           # Escritura no autorizada
├── capture.sh                # Ayuda de captura
├── captures/                 # PCAP/PCAPNG (no versionar los grandes)
├── docs/
│   ├── informe.md            # Borrador de la memoria
│   ├── figuras/
│   └── referencias.bib
└── evidence/
    ├── logs/
    └── capturas_pantalla/
```

## 5.3. Plan de direccionamiento

| Host | IP | Puerto | Función |
|---|---|---|---|
| PLC | 172.28.0.10 | 502/TCP | Servidor Modbus |
| HMI | 172.28.0.11 | Efímero | Cliente Modbus |
| Captura | Comparte red del HMI | — | tcpdump |
| Atacante | 172.28.0.66 | Efímero | Cliente Modbus / sniffing / ARP |
| Host (opcional) | — | 1502 → 502 | Wireshark o `mbtget` desde el equipo anfitrión |

No publiques el puerto 502 en el host salvo que lo necesites. En una planta real, exponer el PLC a la red corporativa o a Internet es una mala práctica; en el laboratorio, la red aislada evita accidentes.

## 5.4. Piezas del `compose.yml`

El archivo completo está en `laboratorio/compose.yml`. Los elementos que debes saber explicar:

- **`build: .`**: una única imagen con Python, PyModbus, tcpdump y utilidades.
- **`networks.ics_net`**: red bridge con subred `172.28.0.0/24`; IPs fijas para que el informe y las capturas coincidan.
- **`depends_on` + `healthcheck`**: el HMI espera a que el PLC esté escuchando.
- **`capture` con `network_mode: "service:hmi"`**: comparte el namespace de red del HMI y ve todo su tráfico. Es útil para la vista del HMI, pero **no ve el tráfico de otros contenedores** (por ejemplo, la escritura del atacante).
- **Captura en el PLC**: `docker compose exec plc tcpdump ...`. Como todo el tráfico del proceso pasa por el PLC, esta captura ve las peticiones y respuestas del HMI y del atacante. Es la opción recomendada para las evidencias principales.
- **`attacker` con `NET_ADMIN` y `NET_RAW`**: necesario para tcpdump y, opcionalmente, ARP spoofing.
- **Volúmenes**: `./:/app` para editar scripts sin reconstruir; `./captures:/captures` para conservar los PCAP.

## 5.5. El problema del sniffing en Docker (importante)

En una red bridge de Docker, el tráfico **unicast** entre HMI y PLC no se difunde a todos los contenedores. Un contenedor atacante cualquiera **no verá** ese tráfico por defecto, aunque esté en la misma subred. Si el informe dice “capturé el tráfico desde el atacante” sin más, probablemente sea falso o esté mal justificado.

Opciones válidas:

| Opción | Ventaja | Limitación |
|---|---|---|
| **Captura en el PLC** (`tcpdump` dentro del contenedor) | Ve todo el tráfico del proceso: HMI y atacante | Es un punto de observación privilegiado, no un atacante externo; requiere `NET_RAW` |
| **Sidecar de captura** que comparte el namespace del HMI | Fiable y sencillo; ve todas las peticiones y respuestas del HMI | No ve el tráfico del atacante; es un punto de observación en el endpoint |
| **ARP spoofing** desde el contenedor atacante | Demuestra MITM real; el tráfico pasa por el atacante | Puede fallar según la configuración de Docker; requiere `NET_ADMIN` y forwarding |
| **Proxy TCP** entre HMI y PLC | Controlado y reproducible; permite ver y modificar | Cambia la topología; el HMI apunta al proxy |
| **Máquinas virtuales con switch virtual en modo promiscuo** | Se acerca a una red real | Más recursos y configuración |

Recomendación para el trabajo: usar la **captura en el PLC** para la evidencia principal (ve HMI y atacante) y, si se quiere, el **sidecar del HMI** para comparar la vista del operador. Si se quiere demostrar MITM, intentar **ARP spoofing** y documentar el resultado. Si no funciona, describirlo como “técnicamente posible” y usar un proxy o VMs como alternativa. Esta honestidad suma puntos, no resta.

## 5.6. Arranque y comprobaciones

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

Comprueba:

- [ ] El PLC escucha en 502.
- [ ] El HMI muestra nivel, temperatura, consigna, bomba, caudal y presión.
- [ ] El HMI actualiza cada segundo.
- [ ] El PLC permite ejecutar `tcpdump` (capacidad `NET_RAW`).
- [ ] El contenedor `capture` está en ejecución (opcional, para la vista del HMI).
- [ ] El atacante puede hacer `ping plc` y conectar al puerto 502.
- [ ] Los logs no muestran errores de versión ni de conexión.

## 5.7. Reproducibilidad

Un compañero o el profesor debería poder ejecutar el laboratorio desde cero. Para ello:

- [ ] `README.md` con requisitos, comandos y solución de problemas.
- [ ] Versiones fijadas (`pymodbus==3.7.4`, imagen `python:3.12-slim`).
- [ ] Sin rutas absolutas ni credenciales personales.
- [ ] `compose.yml` con IPs y puertos documentados.
- [ ] Scripts con valores por defecto razonables y opciones por línea de comandos.
- [ ] PCAP de ejemplo y `README` de capturas con comandos y timestamps.
- [ ] Prueba final en un equipo limpio (o al menos en otro equipo del grupo).
- [ ] `docker compose down` y `docker compose up` funcionan sin pasos manuales ocultos.

## 5.8. Alternativa sin Docker

Si no es posible usar Docker/Podman, se puede montar con máquinas virtuales o equipos físicos:

- VMs con red host-only o interna.
- PLC virtual y HMI en VMs separadas.
- Captura con Wireshark en el host o en una VM con port mirroring.
- Documentar la decisión y las diferencias respecto a Docker.

El enunciado permite “una solución equivalente justificada”. La justificación debe explicar por qué se eligió, qué limitaciones tiene y cómo se garantiza la reproducibilidad.

## 5.9. Ampliaciones útiles (opcionales)

- **IDS offline:** ejecutar Suricata o Zeek sobre el PCAP para demostrar detección.
- **Firewall:** reglas `iptables`/`nftables` en el PLC para permitir solo al HMI; validar antes/después.
- **TLS:** añadir un proxy TLS o usar Modbus/TCP Security si las herramientas lo permiten; comparar con el tráfico en claro.
- **Historian:** un pequeño logger que guarde variables; útil para demostrar integridad y trazabilidad.
- **SIS simulado:** un segundo PLC independiente que compare el nivel y active una parada; demuestra defensa en profundidad.

No añadas complejidad si no la vas a analizar. Cada elemento extra debe tener una función en el informe.
