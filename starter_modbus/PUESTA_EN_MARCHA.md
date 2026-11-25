# Puesta en marcha de los contenedores

Guía para iniciar el laboratorio Modbus/TCP completo o levantar sus contenedores
por separado. Ejecuta los comandos desde el directorio `starter_modbus/`.

> Usa este laboratorio únicamente en una red aislada y con equipos propios o
> autorizados.

## Requisitos

- Docker Desktop con backend WSL2 en Windows, o Docker Engine y Compose en Linux.
- En Windows también puedes ejecutar los comandos desde WSL.
- El daemon de Docker debe estar iniciado.

## Iniciar todos los contenedores

El método recomendado crea la red compartida, inicia el PLC y espera a que esté
saludable antes de iniciar HMI, captura y atacante.

### Linux, macOS o WSL

```sh
sh docker_composer up
sh docker_composer status
```

### Windows PowerShell

```powershell
.\lab.ps1 up
.\lab.ps1 status
```

Los servicios que se inician son `plc`, `hmi`, `capture` y `attacker`.
El contenedor atacante queda en espera; no ejecuta acciones por sí solo.

## Iniciar contenedores por separado

Los Compose individuales usan la red externa `cbi-modbus-ics`. Créala una vez
antes de iniciar el primer servicio, a menos que ya exista:

```sh
docker network inspect cbi-modbus-ics
```

Si el comando indica que la red no existe:

```sh
docker network create --driver bridge --subnet 172.28.0.0/24 cbi-modbus-ics
```

Inicia los servicios en este orden:

### 1. PLC

El PLC debe estar iniciado y saludable antes que los demás contenedores.

```sh
docker compose -f plc/compose.yml up -d --build
docker compose -f plc/compose.yml ps
docker compose -f plc/compose.yml logs -f plc
```

Pulsa `Ctrl+C` para salir de los logs; esto no detiene el contenedor. También
puedes comprobar la salud con:

```sh
docker inspect --format '{{.State.Health.Status}}' cbi-plc
```

Continúa cuando el resultado sea `healthy`.

### 2. HMI

El HMI se conecta al PLC y, por defecto, solo monitoriza:

```sh
docker compose -f hmi/compose.yml up -d --build
docker compose -f hmi/compose.yml ps
docker compose -f hmi/compose.yml logs -f hmi
```

Para ejecutar el HMI en modo operación dentro del contenedor ya iniciado:

```sh
docker compose -f hmi/compose.yml exec hmi python -m hmi.hmi_client --host plc --operate
```

Detén ese proceso con `Ctrl+C` cuando termines.

### 3. Captura de tráfico

El contenedor de captura comparte el espacio de red del PLC, por lo que este
debe estar en ejecución antes de iniciar `capture`.

```sh
docker compose -f capture/compose.yml up -d --build
docker compose -f capture/compose.yml ps
```

Inicia una captura dentro del contenedor:

```sh
docker compose -f capture/compose.yml exec capture sh /app/capture.sh /captures/01_baseline.pcapng
```

Detén la captura con `Ctrl+C`. Los archivos PCAP se guardan en
`capture/captures/` en el equipo anfitrión.

### 4. Contenedor atacante

Este contenedor se mantiene en espera para permitir ejecutar el cliente de
demostración manualmente:

```sh
docker compose -f attacker/compose.yml up -d --build
docker compose -f attacker/compose.yml ps
```

El contenedor no realiza ninguna acción automáticamente. Para consultar las
opciones del cliente:

```sh
docker compose -f attacker/compose.yml exec attacker python -m attacker.attack_write --help
```

## Parar los contenedores

Para parar todo el laboratorio:

```sh
sh docker_composer down
```

En Windows PowerShell:

```powershell
.\lab.ps1 down
```

Para parar un solo servicio, ejecuta `down` con su archivo Compose, por ejemplo:

```sh
docker compose -f hmi/compose.yml down
```

## Si un servicio no está en ejecución

`docker compose exec` requiere que el contenedor correspondiente esté activo.
Inícialo con `up -d --build` y revisa su estado:

```sh
docker compose -f hmi/compose.yml up -d --build
docker compose -f hmi/compose.yml ps -a
docker compose -f hmi/compose.yml logs --tail=80 hmi
```

Si falla el PLC, revisa primero sus logs; HMI y captura dependen de que el PLC
esté disponible. Si Docker informa de un error al montar en `/app` sobre un
sistema de archivos de solo lectura, comprueba que estás usando los Compose
actualizados del proyecto.
