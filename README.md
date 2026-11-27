# Trabajo en Grupo — Ciberseguridad Industrial (GIIROB 2026/27)

**Análisis de ciberseguridad de comunicaciones industriales.** Escenario elegido: **Modbus/TCP** — PLC virtual y HMI que controlan el nivel de un depósito con una bomba, desplegados con Docker.

> El laboratorio es **deliberadamente inseguro**. Ejecútalo solo en la red aislada de Docker y con fines académicos. No lances los scripts de ataque contra equipos ajenos.

## Entregables (enunciado, apartado 6)

| Entregable | Dónde está en el repo |
|---|---|
| 1. Memoria técnica en PDF | `informe/secciones/` → se genera con `informe/build.ps1` o `informe/build.sh` |
| 2a. Archivos PCAP/PCAPNG originales | `evidencias/pcaps/` + `evidencias/MANIFEST.md` |
| 2b. `compose.yml` para reproducir el entorno | `laboratorio/compose.yml` |
| 2c. Scripts y configuraciones | `laboratorio/*.py`, `laboratorio/capture.sh` |

## Estructura

```text
├── README.md               # este archivo: estado, reparto y cómo trabajar
├── TRAZABILIDAD.md         # cada requisito del enunciado → sección → evidencia → responsable
├── laboratorio/            # PLC, HMI, atacante y captura en Docker (ver laboratorio/README.md)
├── evidencias/
│   ├── pcaps/              # PCAP elegidos como evidencia (sí se versionan)
│   ├── MANIFEST.md         # comando, fecha, SHA-256 y frames clave de cada PCAP
│   ├── capturas_pantalla/
│   └── logs/
├── informe/
│   ├── secciones/          # un archivo por capítulo de la memoria
│   ├── figuras/
│   └── build.ps1 / build.sh  # genera la memoria con pandoc
└── guia/                   # material de apoyo (no se entrega)
    ├── README.md           # índice: qué capítulos lee cada bloque
    ├── 01_enunciado.md … 17_anexos.md   # un archivo por capítulo
    └── checklist_entrega.md
```

## Reparto por bloque

Rellenad los nombres. Cada responsable lee su parte de la guía, escribe en su archivo de `informe/secciones/` y abre su propia rama. Todo el grupo lee antes `guia/01`, `02`, `03` y `13`.

| Bloque | Peso | Leer en `guia/` | Escribir en `informe/secciones/` | Responsable | Revisor |
|---|---:|---|---|---|---|
| 4.1 Descripción del escenario | 15 % | `04_escenario.md` | `02_escenario.md` | [ ] | [ ] |
| 4.2a Laboratorio y capturas | 25 % (con 4.2b) | `05_laboratorio.md`, `06_experimentos.md` | `03_despliegue.md` + `evidencias/` | [ ] | [ ] |
| 4.2b Análisis del tráfico | — | `07_trafico.md` | `04_trafico.md` | [ ] | [ ] |
| 4.3 MITRE ATT&CK for ICS | 35 % | `08_mitre.md` | `05_mitre.md` | [ ] | [ ] |
| 4.4 Impacto sobre el proceso | 25 % | `09_impacto.md` | `06_impacto.md` | [ ] | [ ] |
| 5. Incidente real (voluntaria, máx. 1 página) | 15 % | `11_incidente_real.md` | `08_incidente_real.md` | [ ] | [ ] |
| Detección/protección, introducción, conclusiones y montaje final | — | `10_deteccion_proteccion.md`, `12_redaccion_informe.md` | `01_`, `07_`, `09_`, `00_` | [ ] | [ ] |

## Cómo reproducir el laboratorio

```bash
cd laboratorio
docker compose up -d --build
docker compose logs -f hmi
```

Los comandos de captura y de ataque están en [`laboratorio/README.md`](laboratorio/README.md).

## Flujo de evidencias

1. Captura en el PLC: las capturas de trabajo quedan en `laboratorio/captures/` y Git las ignora.
2. Copia a `evidencias/pcaps/` solo las que se citan en la memoria, con el nombre `NN_experimento_AAAAMMDD.pcapng`.
3. Añade una fila en `evidencias/MANIFEST.md` con el comando, la fecha, el SHA-256 y los **números de frame** que usa el informe. El enunciado exige identificar los paquetes utilizados.

## Cómo generar la memoria

Requiere [pandoc](https://pandoc.org/installing.html). Para PDF hace falta además un motor LaTeX (MiKTeX o TeX Live); sin él, el script genera un `.docx` que se puede exportar a PDF desde Word.

```powershell
.\informe\build.ps1
```

El resultado queda en `informe/build/`.

## Forma de trabajar con Git

- Una rama por tarea: `docs/mitre`, `docs/trafico`, `feat/scan-recon`, `fix/compose`…
- Pull request hacia `main` revisado por otra persona del grupo.
- Mensajes de commit descriptivos, por ejemplo `docs(trafico): analiza FC6 del frame 42`.
- Al entregar, etiqueta `v1.0-entrega` en el commit entregado.

## Nota sobre el enunciado

El PDF del enunciado no está en el repo. Confirmad con el profesor la fecha de entrega, la extensión máxima y cómo se suma la actividad voluntaria.
