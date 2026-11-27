# Trazabilidad enunciado → memoria → evidencia

Cada fila es un requisito del enunciado. Antes de entregar, todas deben estar en **Hecho**, con la sección y la evidencia rellenas.
En **Evidencia**, citad el PCAP y los frames (`03_escritura_setpoint.pcapng #42–45`), una figura o un script. Una captura de pantalla sin interpretar **no basta** (enunciado, 4.2).

Estado: `Pendiente` · `En curso` · `Revisión` · `Hecho`

## 4.1 Descripción del escenario industrial (15 %) — `informe/secciones/02_escenario.md`

| Requisito | Sección | Evidencia | Responsable | Estado |
|---|---|---|---|---|
| Dispositivos o aplicaciones que participan y su función | 2.2 | | Luis Roberto | Revisión |
| Protocolo utilizado y sus características principales | 2.3 | | Luis Roberto | Revisión |
| Variables de proceso intercambiadas (qué representa cada una) | 2.4 | `laboratorio/README.md` (mapa de registros) | Luis Roberto | Revisión |
| Operaciones: lectura, escritura, etc. | 2.5 | | Luis Roberto | Revisión |
| Esquema sencillo de la arquitectura y de las comunicaciones | 2.6 | `informe/figuras/` | Luis Roberto | Revisión |
| Cómo podría usarse este escenario en una planta industrial real | 2.7 | | Luis Roberto | Revisión |
| Consecuencias de manipular cada variable (enunciado, 3) | 2.4 | | Luis Roberto | Revisión |

## 4.2 Despliegue y análisis del tráfico (25 %) — `03_despliegue.md`, `04_trafico.md`

| Requisito | Sección | Evidencia | Responsable | Estado |
|---|---|---|---|---|
| Despliegue con Docker/Podman o solución equivalente justificada | 3.1–3.4 | `laboratorio/compose.yml` | | Pendiente |
| El sistema genera y permite observar tráfico del proceso | 3.4 | `01_baseline` | | Pendiente |
| Capturas con Wireshark/tcpdump | 4.1 | `evidencias/MANIFEST.md` | | Pendiente |
| Direcciones IP, puertos y participantes | 4.2 | PCAP + frames | | Pendiente |
| Mensajes y operaciones característicos del protocolo | 4.3 | PCAP + frames | | Pendiente |
| ≥ 2 operaciones representativas, **incluida una modificación o actualización de datos** | 4.3 | PCAP + frames (FC6/FC5) | | Pendiente |
| Variables o información del proceso observables en la comunicación | 4.4 | PCAP + frames | | Pendiente |
| Presencia o ausencia de autenticación, cifrado o protección de mensajes | 4.5 | PCAP + frames | | Pendiente |
| **≥ 1 PCAP/PCAPNG original entregado**, con los paquetes usados identificados en el informe | 4.x, Anexo C | `evidencias/pcaps/` | | Pendiente |

## 4.3 Investigación de amenazas con MITRE ATT&CK for ICS (35 %) — `05_mitre.md`

Mínimo **dos técnicas**. Rellenad una fila por técnica y por requisito, o una tabla por técnica.

| Requisito (por técnica) | Sección | Evidencia | Responsable | Estado |
|---|---|---|---|---|
| Identificador y nombre de la técnica | 5.2 | `05_mitre.md §5.2` | Zhihui Li | Hecho |
| Descripción del comportamiento del atacante | 5.3–5.6 | `05_mitre.md §5.3–5.6` | Zhihui Li | Hecho |
| Condiciones necesarias para que se produzca | 5.3–5.6 | `05_mitre.md §5.3–5.6` | Zhihui Li | Hecho |
| Relación con el protocolo o la arquitectura desplegada | 5.3–5.6 | `05_mitre.md §5.3–5.6; laboratorio/scan_recon.py` | Zhihui Li | Hecho |
| Posibles evidencias de su ejecución | 5.3–5.6 | `02_reconocimiento_*.pcapng y 03_escritura_setpoint_*.pcapng (frames en las fichas)` | Zhihui Li | Hecho |
| Consecuencias potenciales para el proceso industrial | 5.3–5.6 | `05_mitre.md §5.3–5.6` | Zhihui Li | Hecho |
| Selección justificada (no solo enumerar técnicas) | 5.1 | `05_mitre.md §5.1` | Zhihui Li | Hecho |
| Distinguir **vulnerabilidad observada / ataque técnicamente posible / comportamiento demostrado** | 5.8 | `05_mitre.md §5.8` | Zhihui Li | Hecho |

Estado de cada técnica candidata:

| Técnica | Categoría (observada / posible / demostrada) | Script o experimento | PCAP + frames |
|---|---|---|---|
| T0842 Network Sniffing | Demostrada | `capture.sh` / `tcpdump` | `01_baseline_20261127.pcapng`, frames 1–9 y 264–270 |
| T0861 Point & Tag Identification | Demostrada/parcial | `scan_recon.py` | `02_reconocimiento_20261127.pcapng`, frames 300–369 y 398 |
| T0836 Modify Parameter | Demostrada | `attack_write.py` | `03_escritura_setpoint_20261127.pcapng`, frames 284–291, 954 y 959 |
| T0830 Adversary-in-the-Middle | Posible (no reproducida en Docker) | intento con ARP spoofing/proxy | Sin PCAP |

## 4.4 Análisis del impacto sobre el proceso (25 %) — `06_impacto.md`

| Requisito | Sección | Evidencia | Responsable | Estado |
|---|---|---|---|---|
| Amenaza más relevante seleccionada | 6.1 | | Luis Roberto | Revisión |
| Escenario hipotético de ataque: cómo actuaría el atacante | 6.2 | | Luis Roberto | Revisión |
| Condiciones necesarias | 6.3 | | Luis Roberto | Revisión |
| Efectos sobre el funcionamiento de la instalación | 6.4 | | Luis Roberto | Revisión |
| Consecuencias: disponibilidad, integridad de variables, continuidad, calidad, seguridad del proceso | 6.4–6.5 | | Luis Roberto | Revisión |
| Justificación conjunta de por qué es la amenaza prioritaria | 6.6 | | Luis Roberto | Revisión |

## 5. Actividad voluntaria: incidente real (15 %) — `08_incidente_real.md`

| Requisito | Sección | Evidencia | Responsable | Estado |
|---|---|---|---|---|
| Incidente industrial documentado, relacionado con el protocolo, una técnica MITRE o una amenaza semejante | 8.1–8.3 | | | Pendiente |
| Qué ocurrió | 8.2–8.3 | | | Pendiente |
| Consecuencias | 8.4 | | | Pendiente |
| Similitudes con el escenario estudiado | 8.5 | | | Pendiente |
| **Máximo una página** | — | | | Pendiente |
| Fuentes consultadas | 8.7 | | | Pendiente |

## Otros puntos del enunciado

| Requisito | Sección | Evidencia | Responsable | Estado |
|---|---|---|---|---|
| Medidas de detección y protección para un despliegue real (introducción del enunciado; sin peso propio) | 7 | | | Pendiente |

## 6. Entregables

| Entregable | Ubicación | Responsable | Estado |
|---|---|---|---|
| Memoria técnica en PDF | `informe/build/` | | Pendiente |
| Archivos PCAP/PCAPNG | `evidencias/pcaps/` | | Pendiente |
| `compose.yml` o instrucciones equivalentes | `laboratorio/` | | Pendiente |
| Scripts o configuraciones desarrollados o modificados | `laboratorio/` | | Pendiente |
