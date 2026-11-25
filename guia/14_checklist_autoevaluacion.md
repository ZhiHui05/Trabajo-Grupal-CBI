# 14. Checklist de entrega y autoevaluación

## 14.1. Entregables

- [ ] Memoria técnica en PDF.
- [ ] Al menos un PCAP/PCAPNG original.
- [ ] `compose.yml` o instrucciones equivalentes.
- [ ] Scripts y configuraciones.
- [ ] `README.md` de reproducibilidad.
- [ ] Anexo de evidencias (frames, tablas, capturas).
- [ ] Actividad voluntaria (si se realiza).
- [ ] Revisión cruzada.
- [ ] Nombres de archivo y hashes.
- [ ] Paquete final comprimido.

## 14.2. Autoevaluación por criterios

| Bloque | Criterio | ¿Cumplido? | Evidencia | Responsable |
|---|---|---|---|---|
| 4.1 | Proceso descrito | ☐ | Sección 2 | |
| 4.1 | Actores y funciones | ☐ | Tabla 1 | |
| 4.1 | Protocolo y características | ☐ | Sección 2.3 | |
| 4.1 | Variables y operaciones | ☐ | Tablas 2 y 3 | |
| 4.1 | Arquitectura | ☐ | Figura 1 | |
| 4.1 | Uso en planta real | ☐ | Sección 2.7 | |
| 4.2 | Despliegue reproducible | ☐ | `compose.yml` + README | |
| 4.2 | IP, puertos y participantes | ☐ | Tabla de red | |
| 4.2 | Mensajes característicos | ☐ | Sección 4 | |
| 4.2 | Dos operaciones con modificación | ☐ | Sección 4.3 | |
| 4.2 | Variables observables | ☐ | Tabla 4 | |
| 4.2 | Autenticación/cifrado evaluados | ☐ | Tabla 5 | |
| 4.2 | PCAP original y frames | ☐ | Anexo | |
| 4.3 | Al menos dos técnicas | ☐ | Fichas | |
| 4.3 | ID, nombre y táctica | ☐ | Fichas | |
| 4.3 | Comportamiento y condiciones | ☐ | Fichas | |
| 4.3 | Relación con protocolo/arquitectura | ☐ | Fichas | |
| 4.3 | Evidencias y consecuencias | ☐ | Fichas | |
| 4.3 | Justificación de la selección | ☐ | Sección 5.2 | |
| 4.3 | Vulnerabilidad/posible/demostrado | ☐ | Tabla 8.5 | |
| 4.4 | Amenaza prioritaria | ☐ | Sección 6.1 | |
| 4.4 | Narrativa del ataque | ☐ | Sección 6.2 | |
| 4.4 | Condiciones | ☐ | Tabla 6.3 | |
| 4.4 | Consecuencias por dimensión | ☐ | Tabla 6.4 | |
| 4.4 | Priorización justificada | ☐ | Sección 6.6 | |
| 5 | Incidente real (si aplica) | ☐ | Sección 8 | |
| — | Referencias y citas | ☐ | Bibliografía | |
| — | Formato y ortografía | ☐ | Revisión final | |

## 14.3. Últimas 48 horas

- [ ] Prueba desde una copia limpia del repositorio.
- [ ] Abrir el PCAP en otro equipo y verificar los frames citados.
- [ ] Comprobar IP, puertos y nombres en todo el informe.
- [ ] Verificar que cada figura/tabla está referenciada.
- [ ] Revisar que no hay capturas de pantalla sin explicación.
- [ ] Revisar ortografía y concordancia.
- [ ] Comprobar que las referencias están completas.
- [ ] Exportar el PDF y revisar los marcadores.
- [ ] Crear el paquete final y comprobar que se abre.
- [ ] Entregar con margen.

## 14.4. Estructura del paquete final

```text
Entrega_Grupo_CBI/
├── Memoria_Grupo_CBI.pdf
├── LEEME.txt
├── SHA256SUMS.txt
├── evidencias/
│   ├── pcaps/
│   │   ├── 01_baseline.pcapng
│   │   ├── 02_reconocimiento.pcapng
│   │   └── 03_escritura_setpoint.pcapng
│   ├── capturas_pantalla/
│   └── logs/
├── laboratorio/
│   ├── compose.yml
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── scripts/
│   └── README.md
└── anexos/
    ├── tablas/
    └── figuras/
```

Calcula los hashes:

```bash
sha256sum evidencias/pcaps/*.pcapng > SHA256SUMS.txt
```

En Windows PowerShell:

```powershell
Get-FileHash evidencias\pcaps\*.pcapng -Algorithm SHA256 | Format-List
```
