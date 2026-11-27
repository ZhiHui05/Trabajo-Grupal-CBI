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
| `02_reconocimiento_20261127.pcapng` | Reconocimiento T0861: Unit IDs y mapa de registros | 2026-11-27 16:13:13 UTC (39 s) | PLC (`eth0`) | `docker compose exec plc tcpdump -i eth0 -s 0 -w /app/captures/02_reconocimiento_20261127.pcapng 'tcp port 502'` | `08c3486ba61c838b507265a63c3115d59362bc84343fdf56067844ee1d7dd54c` | 300–369: 12 lecturas FC3 unitarias desde `172.28.0.66`; 302–315: Unit IDs no válidos con 0x0B; 398: excepción 0x02 en HR 32 | 5.4 |
| `03_escritura_setpoint_20261127.pcapng` | Escritura no autorizada de consigna y bomba | 2026-11-27 16:16:49 UTC (92 s) | PLC (`eth0`) | `docker compose exec plc tcpdump -i eth0 -s 0 -w /app/captures/03_escritura_setpoint_20261127.pcapng 'tcp port 502'` | `5cc524f7958e8ae9be3c48012517749c88429b99d81e02c46c357acb2f20597c` | 284/286: FC6 HR2=95; 288/289: FC5 CO0=1; 291: FC3 ya lee SP=95; 954: nivel 105,0 %; 959: LS-101=1 | 5.5 |

## Capturas de pantalla y logs

| Archivo | Qué muestra | Relacionado con (PCAP / frames) | Sección del informe |
|---|---|---|---|
| `logs/recon_20261127.txt` | Salida completa de `scan_recon.py`: Unit ID 1, mapa y excepción 0x02 | `02_reconocimiento_20261127.pcapng`, frames 300–398 | 5.4 |
| `logs/recon_tabla_20261127.md` | Tabla Markdown generada por el script | `02_reconocimiento_20261127.pcapng` | 5.4 |
| `logs/hmi_ataque_20261127.txt` | Consigna 95 %, bomba ON y `NivelAlto=SI` | `03_escritura_setpoint_20261127.pcapng`, frames 284–959 | 5.5 |
| `logs/plc_ataque_20261127.txt` | Nivel hasta 110 %, `NivelAlto=SI` | `03_escritura_setpoint_20261127.pcapng` | 5.5 |
| | | | |
