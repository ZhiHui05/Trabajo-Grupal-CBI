# 13. Organización del grupo y plan de trabajo

## 13.1. Roles

Para un grupo de 5:

| Rol | Responsabilidad principal | Entregables |
|---|---|---|
| **Coordinador/a** | Planificación, integración, calidad, comunicación con el profesor | Cronograma, actas, informe final |
| **Infraestructura/DevOps** | Docker/Podman, red, compose, reproducibilidad | `compose.yml`, `Dockerfile`, README |
| **Desarrollo OT** | PLC, HMI, lógica, mapa de registros | `plc_server.py`, `hmi_client.py`, tabla de variables |
| **Análisis de seguridad** | Capturas, Wireshark, ataques, evidencias | PCAP, tablas de tráfico, scripts de ataque |
| **Amenazas e impacto** | MITRE, incidente, impacto, controles | Fichas, matriz de riesgo, secciones 4.3/4.4/5 |

Para un grupo de 4, fusiona “Coordinador/a” con “Amenazas e impacto” o “Análisis de seguridad”, pero mantén la revisión cruzada. Para un grupo de 3, reparte por bloques del informe y haz revisiones mutuas.

## 13.2. Matriz RACI

R = responsable de hacer, A = aprueba, C = consultado, I = informado.

| Actividad | Coordinador | Infra | OT | Seguridad | Amenazas |
|---|---|---|---|---|---|
| Elección del escenario | A | C | C | C | R |
| Laboratorio y red | A | R | C | C | I |
| PLC/HMI | A | C | R | C | I |
| Capturas | A | C | C | R | I |
| Análisis de tráfico | A | I | C | R | C |
| MITRE | A | I | I | C | R |
| Impacto | A | I | C | C | R |
| Controles | A | C | C | R | C |
| Incidente real | A | I | I | I | R |
| Informe | A/R | C | C | C | C |
| Revisión final | A/R | C | C | C | C |

Nadie debería ser el único que entiende una parte crítica. Si el coordinador desaparece, el trabajo debe continuar.

## 13.3. Plan de 4 semanas

**Semana 1 — Definición**

| Tarea | Responsable | Salida |
|---|---|---|
| Kickoff, reparto de roles, calendario | Coordinador | Acta y cronograma |
| Elección de protocolo y escenario | Todos | Propuesta aprobada |
| Definición del proceso y variables | OT + Amenazas | Tabla de variables |
| Arquitectura y direccionamiento | Infra | Diagrama y tabla de IPs |
| Repositorio y esqueleto Docker | Infra | `compose.yml` inicial |
| Primer contacto con el profesor | Coordinador | Confirmación |

**Semana 2 — Laboratorio y línea base**

| Tarea | Responsable | Salida |
|---|---|---|
| PLC y HMI funcionando | OT | Scripts probados |
| Red y captura | Infra + Seguridad | PCAP base |
| Lectura y escritura normal | Seguridad | Tabla de operaciones |
| Primera escritura no autorizada | Seguridad | PCAP de ataque |
| Borrador de 4.1 y 4.2 | OT + Seguridad | Texto y figuras |
| Revisión cruzada | Todos | Comentarios |

**Semana 3 — Análisis y impacto**

| Tarea | Responsable | Salida |
|---|---|---|
| Fichas MITRE | Amenazas | 3–4 fichas |
| Cadena de ataque | Amenazas + Seguridad | Tabla y figura |
| Análisis de impacto | Amenazas + OT | Sección 4.4 |
| Controles y detección | Seguridad + Infra | Tabla de medidas |
| MITM/DoS opcional | Seguridad | PCAP o justificación |
| Incidente real | Amenazas | Una página |
| Borrador de 4.3 y 4.4 | Amenazas | Texto |

**Semana 4 — Integración y entrega**

| Tarea | Responsable | Salida |
|---|---|---|
| Integración del informe | Coordinador | Borrador completo |
| Prueba desde cero | Infra | Checklist de reproducibilidad |
| Revisión de evidencias | Seguridad | Frames verificados |
| Revisión de estilo y referencias | Todos | Correcciones |
| Congelación de contenido | Coordinador | Versión candidata |
| Exportación y entrega | Coordinador | PDF + anexos + PCAP |

**Hitos:**

- **M1 (fin semana 1):** escenario aprobado y repositorio creado.
- **M2 (fin semana 2):** laboratorio reproducible y PCAP base.
- **M3 (fin semana 3):** análisis MITRE e impacto completos.
- **M4 (día -2):** informe congelado.
- **M5 (día 0):** entrega.

## 13.4. Reunión semanal (30–45 min)

1. Estado de cada bloque (5 min por persona).
2. Bloqueos y decisiones (10 min).
3. Revisión de una evidencia concreta (10 min): abrir un PCAP y verificar un frame.
4. Tareas y responsables (5 min).
5. Fecha de la siguiente reunión.

Guarda un acta breve con decisiones, no solo tareas. Las decisiones técnicas deben quedar por escrito.

## 13.5. Flujo de trabajo con Git

```bash
git init
git add .
git commit -m "chore: estructura inicial del laboratorio"
git branch -M main
git remote add origin <url>
git push -u origin main
```

Convenciones:

- Ramas: `feat/plc-simulacion`, `feat/captura-baseline`, `docs/mitre`, `fix/hmi-reconnect`.
- Commits: `feat(plc): añade simulación de nivel`, `docs(trafico): analiza FC6`, `fix(compose): corrige IP del HMI`.
- Pull request con revisión de otra persona.
- Issues para tareas y decisiones.
- Etiqueta `v1.0-entrega` al final.
- No subas PCAP grandes al repositorio; usa Git LFS o una carpeta compartida y un manifiesto con hashes.
- `.gitignore` para `captures/*.pcap`, `__pycache__`, `.venv`, `.env`.

## 13.6. Nombres de archivo

| Tipo | Convención | Ejemplo |
|---|---|---|
| PCAP | `NN_experimento_AAAAMMDD.pcapng` | `03_escritura_setpoint_20261120.pcapng` |
| Figura | `fig_N_descripcion.png` | `fig_3_flujo_fc3.png` |
| Tabla | `tabla_N_descripcion.md` | `tabla_4_mecanismos.md` |
| Script | `verbo_objeto.py` | `attack_write.py` |
| Documento | `NN_nombre.md` | `08_mitre.md` |

## 13.7. Definición de “hecho”

Una tarea está hecha cuando:

- [ ] El código funciona desde una copia limpia.
- [ ] La evidencia está guardada y referenciada.
- [ ] El texto explica qué se hizo, qué se observó y qué significa.
- [ ] Otra persona lo ha revisado.
- [ ] No hay TODOs ni placeholders.
- [ ] Las figuras/tablas están numeradas y referenciadas.
- [ ] Las fuentes están citadas.

## 13.8. Comunicación

- Un canal rápido para dudas (WhatsApp/Slack/Teams).
- Un tablero o issues para tareas.
- Una carpeta compartida para PCAP y documentos.
- Una persona responsable de cada bloque.
- Respuesta comprometida en 24 h laborables.
- Avisa con antelación si no puedes asistir o entregar.
- No tomes decisiones que afecten a otro bloque sin consultar.

## 13.9. Contingencias

| Riesgo | Probabilidad | Impacto | Plan |
|---|---|---|---|
| Docker no funciona en algún equipo | Media | Alto | Podman, VM o equipo alternativo; documentar |
| ARP spoofing no funciona | Alta | Medio | Proxy TCP o VMs; declarar “posible” |
| PyModbus cambia de API | Media | Medio | Versión fijada; no actualizar a última hora |
| Pérdida de PCAP | Baja | Alto | Dos copias + hash |
| Compañero no disponible | Media | Alto | Rol de respaldo y documentación |
| Retraso en la integración | Alta | Alto | Congelar 48 h antes; revisión semanal |
| El profesor cambia requisitos | Baja | Alto | Confirmar por escrito al inicio |
