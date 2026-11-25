# 11. Actividad voluntaria: incidente real

> Vale un 15 % adicional según el enunciado. Hazla si el grupo puede: es una página y refuerza mucho la parte de impacto.

## 11.1. Criterios de selección

Elige un incidente que:

- Esté **documentado** con fuentes primarias o informes técnicos.
- Se relacione con **el protocolo, una técnica MITRE o el procedimiento** del escenario.
- Permita explicar **consecuencias reales**, no solo el titular.
- Puedas resumir en **una página**.

## 11.2. Opciones

| Incidente | Año | Vector/protocolo | Técnicas relacionadas | Similitud con el escenario |
|---|---|---|---|---|
| **Oldsmar (EE. UU.)** | 2021 | Acceso remoto (TeamViewer) a HMI | T0836, T0855 | Cambio de consigna de producto químico |
| **FrostyGoop / Lviv (Ucrania)** | 2024 | Modbus/TCP a controladores ENCO | T0836 | Cambio de registros de retención; pérdida de calefacción |
| **Maroochy Shire (Australia)** | 2000 | Telemetría radio | T0855, T0836 | Comandos no autorizados, vertido de aguas residuales |
| **Unitronics (EE. UU./Israel)** | 2023 | PLC Unitronics, contraseña por defecto | Acceso con credenciales por defecto, T0855 | PLC/HMI de agua expuestos, manipulación |
| **2026 U.S. water utilities** | 2026 | PLC MicroLogix expuestos a Internet | T0836, T0855 | Cambio de configuración/acceso a PLC de agua |
| **Industroyer2 (Ucrania)** | 2022 | IEC 60870-5-104 | T0855, T0831 | Comandos directos a subestación |
| **Havex (Europa)** | 2014 | OPC | T0861, T0842 | Reconocimiento de sistemas ICS |
| **Stuxnet (Irán)** | 2010 | S7/Step7 | T0836, T0831 | Manipulación de parámetros de centrífugas |
| **Triton (Arabia Saudí)** | 2017 | Triconex SIS | T0855/T0836 | Manipulación de sistema de seguridad |

## 11.3. Recomendación: FrostyGoop u Oldsmar

**Si quieres la relación más directa con Modbus/TCP, elige FrostyGoop (2024).** Es un caso reciente, documentado por Dragos y con el mismo protocolo y la misma técnica que el escenario: escritura de registros de retención para alterar el control de calefacción.

**FrostyGoop — hechos que debes verificar y citar:**

- Enero de 2024, empresa municipal de calefacción de Lviv (Ucrania).
- Malware escrito en Go que utiliza **Modbus/TCP por el puerto 502**.
- Envió comandos Modbus a controladores **ENCO** para modificar registros de retención.
- Afectó a más de **600 edificios de apartamentos**, con pérdida de calefacción durante casi **48 horas** en pleno invierno.
- No se reportaron daños físicos directos; el impacto fue de disponibilidad y continuidad del servicio.
- Relación con nuestro escenario: T0836, escritura de parámetros, ausencia de autenticación, controladores posiblemente expuestos.
- Lecciones: segmentación, no exponer Modbus a Internet, allowlist de escrituras, monitorización de cambios, inventario y respuesta.

> **Cuidado con los detalles:** las cifras y la atribución pueden variar entre fuentes. Cita el informe de Dragos y, si existe, el aviso de CISA; no mezcles datos de medios con conclusiones técnicas.

**Oldsmar (2021)** sigue siendo una buena opción si prefieres un caso más conocido y centrado en acceso remoto. **Hechos que debes verificar y citar:**

- Febrero de 2021, planta de tratamiento de agua de Oldsmar, Florida.
- El atacante accedió remotamente mediante TeamViewer.
- Aumentó la consigna de hidróxido de sodio (NaOH) de aproximadamente 100 ppm a aproximadamente 11.100 ppm.
- Un operador lo detectó y revirtió el cambio; no hubo impacto en el suministro.
- Investigación del FBI y la oficina del sheriff; se señalaron debilidades de acceso remoto y sistemas desactualizados.

**Relación con nuestro escenario:**

- Cambio de una consigna (T0836) con efecto físico directo.
- Acceso remoto sin controles suficientes (segmentación, MFA, mínimo privilegio).
- Importancia de la monitorización y de que el operador detecte el cambio.
- Diferencia: no fue Modbus/TCP ni un ataque de malware; fue acceso legítimo mal utilizado.

**Lecciones:**

- Eliminar o restringir el acceso remoto innecesario.
- MFA y cuentas individuales.
- Segmentar la red OT.
- Limitar quién puede cambiar consignas.
- Alarmas y límites independientes.
- Monitorizar y registrar cambios.

**Fuentes:** busca la nota de prensa del FBI, la información de CISA, el informe municipal y artículos técnicos; evita basarte solo en titulares. Cita la fecha de consulta.

## 11.4. Plantilla de una página

| Apartado | Contenido | Extensión |
|---|---|---|
| Contexto | Organización, sector, proceso afectado | 2–3 líneas |
| Cronología | Fechas y hitos principales | 3–5 líneas |
| Vector | Cómo entró el atacante, qué protocolo/herramienta usó | 3–5 líneas |
| Acción | Qué manipuló o ejecutó | 2–3 líneas |
| Consecuencias | Impacto real, respuesta, duración | 3–5 líneas |
| Relación con el escenario | Técnica MITRE, similitudes y diferencias | 4–6 líneas |
| Lecciones | 3–5 medidas aplicables | 3–5 líneas |
| Fuentes | 3–5 referencias | — |

## 11.5. Errores que evitar

- Copiar y pegar un artículo entero.
- Exagerar consecuencias que no ocurrieron.
- Mezclar varios incidentes en una página.
- No citar fuentes o citar solo medios generalistas.
- No explicar la relación con el escenario.
- Superar la página.
