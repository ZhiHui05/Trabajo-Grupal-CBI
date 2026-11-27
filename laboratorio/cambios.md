# Cambios realizados respecto al proyecto inicial

## Organización modular

- Se sustituyó el Compose monolítico por configuraciones independientes en `plc/compose.yml`,
  `hmi/compose.yml`, `capture/compose.yml` y `attacker/compose.yml`.
- Se separaron las imágenes en un `Dockerfile` por componente. Cada imagen copia solo el código
  que necesita y comparte el contexto de build raíz.
- Se movieron los servidores y clientes a sus carpetas respectivas:
  `plc/plc_server.py`, `hmi/hmi_client.py`, `attacker/attack_write.py` y `capture/capture.sh`.
- Se ajustaron los montajes de PLC, HMI y atacante para montar cada módulo bajo `/app/<módulo>`,
  evitando que el montaje de solo lectura ocultara el destino del mapa Modbus compartido. Los
  comandos Compose usan ahora la ejecución por módulos de Python.
- Se trasladó la salida de capturas a `capture/captures/`.
- Se añadieron `docker_composer` y `lab.ps1` para crear la red, esperar a que el PLC esté saludable,
  desplegar los módulos en orden, consultar su estado y detener/limpiar el laboratorio.

## Dependencias y registros compartidos

- Se consolidaron las dependencias Python en el único `requirements.txt` raíz. PLC, HMI y atacante
  instalan desde ese archivo; captura solo instala las herramientas del sistema que necesita.
- Se añadió `modbus_map.py` como fuente común de las direcciones Modbus para evitar que los scripts
  mantengan copias divergentes.
- Se extrajo el modelo de proceso a `plc/process_model.py`, separado de la implementación del
  servidor Modbus.
- La tarea de simulación del PLC se cancela explícitamente al terminar el servidor, evitando que
  quede ejecutándose durante el cierre.

## Despliegue y seguridad del laboratorio

- La red externa compartida mantiene valores predeterminados reproducibles y permite configurar
  `NETWORK_SUBNET`, `PLC_IP`, `HMI_IP` y `ATTACKER_IP` mediante variables de entorno.
- La captura comparte el namespace de red del PLC para observar tráfico del HMI y del atacante.
- Se añadió `capture/stream_capture.py` para transmitir paquetes Modbus en directo a Wireshark por
  TCP. El puerto `15002` se publica únicamente en `127.0.0.1` y puede cambiarse con
  `WIRESHARK_STREAM_PORT`.
- PLC y HMI usan UID/GID no root (`10001:10001`) y montan su código en solo lectura.
- Las capacidades de captura/red se mantienen en los módulos que las requieren; el PLC ya no
  necesita capacidades de captura.
- Se fijó por digest la imagen base de los cuatro módulos
  (`python:3.12-slim@sha256:191083cdf6c7bda8c76158983163ead5d5cf7b77cf3033e805bb0f5296f51b4b`)
  para hacer repetibles los builds.
- Se añadió `.dockerignore` para excluir cachés y PCAP del contexto de construcción.

## Pruebas y documentación

- Se añadieron cinco pruebas unitarias estándar para el modelo del proceso: llenado y drenaje,
  límites de nivel y velocidad, medidas de caudal/presión y alarma de nivel alto. Se añadió una
  sexta prueba para comprobar la retransmisión del flujo PCAP.
- Se actualizaron `README.md`, `00_Guia_Trabajo_Grupo.md` y `wireshark_filters.txt` para reflejar
  las rutas, comandos, estructura, valores de red predeterminados y configuración actuales.
- Se añadió `PUESTA_EN_MARCHA.md` con instrucciones para iniciar cada contenedor y visualizar
  tráfico en directo con Wireshark.
- Se añadió en el README el comando para ejecutar las pruebas:
  `python -m unittest discover -s tests -v`.
