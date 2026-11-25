# Manifiesto de evidencias

Una fila por cada PCAP de `evidencias/pcaps/` que se cite en la memoria. Los **frames clave** son los números de paquete que aparecen en el informe; el enunciado exige identificar los paquetes utilizados.

Calcular el hash:

```bash
sha256sum evidencias/pcaps/*.pcapng
```

```powershell
Get-FileHash evidencias\pcaps\*.pcapng -Algorithm SHA256
```

## PCAP

| Archivo | Experimento | Fecha y hora | Punto de captura | Comando | SHA-256 | Frames clave → qué demuestran | Sección del informe |
|---|---|---|---|---|---|---|---|
| `01_baseline_AAAAMMDD.pcapng` | Línea base: HMI lee el proceso | | PLC (`eth0`) | `docker compose exec plc tcpdump -i eth0 -s 0 -w /app/captures/01_baseline.pcapng 'tcp port 502'` | | | 4.3 |
| | | | | | | | |

## Capturas de pantalla y logs

| Archivo | Qué muestra | Relacionado con (PCAP / frames) | Sección del informe |
|---|---|---|---|
| | | | |
