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
| `01_baseline_20261127.pcapng` | Línea base: HMI en modo monitor lee el proceso cada 1 s (460 paquetes, 45 s, solo HMI 172.28.0.11 ↔ PLC 172.28.0.10:502) | 2026-11-27 17:28:11–17:28:57 | PLC (`eth0`) | `docker compose exec plc tcpdump -i eth0 -s 0 -w /app/captures/01_baseline.pcapng 'tcp port 502'` | `34120428cf0d3fb6129c79f0445a3752cd0856e8057a25be93d74a3d75008583` | Ciclo de sondeo completo: #1–2 FC3 Read Holding Registers (nivel, temp., consigna, velocidad), #4–5 FC4 Read Input Registers (caudal, presión), #6–7 FC2 Read Discrete Inputs (nivel alto), #8 FC1 Read Coils (bomba). 46 ciclos idénticos, sin escrituras. Sin autenticación ni cifrado: valores en claro | 4.2 (tráfico) |
| | | | | | | | |

## Capturas de pantalla y logs

| Archivo | Qué muestra | Relacionado con (PCAP / frames) | Sección del informe |
|---|---|---|---|
| | | | |
