# Memoria técnica

Cada capítulo es un archivo de `secciones/`. Los scripts de build los concatenan **en orden alfabético**, así que conservad el prefijo numérico.

| Archivo | Contenido | Bloque del enunciado |
|---|---|---|
| `00_portada_resumen.md` | Portada, resumen ejecutivo, abreviaturas | — |
| `01_introduccion.md` | Introducción y objetivos | — |
| `02_escenario.md` | Descripción del escenario industrial | 4.1 (15 %) |
| `03_despliegue.md` | Despliegue del laboratorio | 4.2 (25 %) |
| `04_trafico.md` | Análisis del tráfico | 4.2 (25 %) |
| `05_mitre.md` | MITRE ATT&CK for ICS | 4.3 (35 %) |
| `06_impacto.md` | Impacto sobre el proceso | 4.4 (25 %) |
| `07_deteccion_proteccion.md` | Detección y protección | Introducción del enunciado |
| `08_incidente_real.md` | Incidente real (máx. 1 página) | 5 (15 %) |
| `09_conclusiones.md` | Conclusiones | — |
| `10_referencias.md` | Referencias | — |
| `11_anexos.md` | Anexos | — |

## Reglas

- Las figuras van en `figuras/` y se enlazan como `![Fig. 3 — Flujo FC3](figuras/fig_3_flujo_fc3.png)`.
- Al citar tráfico, indicad siempre el PCAP y los frames: `03_escritura_setpoint.pcapng, frames 42–45`. Esos frames deben aparecer en `evidencias/MANIFEST.md`.
- Las notas en blockquote (`> …`) son recordatorios de la plantilla: borradlas antes de entregar.

## Generar la memoria

Requiere [pandoc](https://pandoc.org/installing.html). Para PDF, además, un motor LaTeX (MiKTeX en Windows o TeX Live). Sin LaTeX, los scripts generan un `.docx` que se exporta a PDF desde Word.

```powershell
.\informe\build.ps1
```

```bash
sh informe/build.sh
```

La salida queda en `informe/build/` (ignorada por Git).

## Antes de entregar

- [ ] No quedan corchetes `[ ]` ni notas en blockquote.
- [ ] Todos los frames citados existen en el PCAP entregado y están en `evidencias/MANIFEST.md`.
- [ ] Todas las figuras y tablas están numeradas y referenciadas en el texto.
- [ ] La actividad voluntaria ocupa como máximo una página.
- [ ] `TRAZABILIDAD.md` está completo.
