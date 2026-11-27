# 1. Resumen del enunciado

## 1.1. Datos generales

| Aspecto | Contenido |
|---|---|
| Asignatura | Ciberseguridad Industrial |
| Curso | 2026/27 |
| Titulación | GIIROB |
| Profesor | José Vera Pérez |
| Modalidad | Trabajo en grupo, entrega única |
| Título | Análisis de ciberseguridad de comunicaciones industriales |
| Enfoque | Desplegar un escenario virtualizado, capturar tráfico, identificar debilidades, relacionarlas con MITRE ATT&CK for ICS y analizar el impacto |

## 1.2. Objetivo

Desplegar un escenario de comunicación industrial virtualizado y realizar una evaluación básica de su ciberseguridad, combinando experimentación práctica con investigación y análisis de amenazas.

El enunciado insiste en que **no es necesario construir un proceso industrial complejo ni implementar un protocolo desde cero**. Se valora especialmente:

- La comprensión del funcionamiento del sistema.
- El análisis de las evidencias obtenidas.
- La justificación técnica de las decisiones de ciberseguridad.

## 1.3. Qué pide el trabajo, en una frase

Elegir un protocolo industrial, montar un pequeño laboratorio con dos o más componentes que intercambien datos, capturar y explicar el tráfico, identificar debilidades, estudiar al menos dos técnicas de MITRE ATT&CK for ICS, analizar el impacto de la amenaza más relevante y proponer medidas de detección y protección para una planta real.

## 1.4. Objetivos de aprendizaje

Al finalizar, el grupo debe ser capaz de:

1. Comprender el funcionamiento de un protocolo de comunicaciones industriales y su aplicación en un proceso real.
2. Desplegar un entorno virtualizado sencillo que reproduzca el intercambio de información entre dispositivos o aplicaciones industriales.
3. Capturar, interpretar y documentar tráfico de red con Wireshark.
4. Identificar debilidades y posibles vectores de ataque asociados al protocolo y a su configuración.
5. Investigar y relacionar amenazas con técnicas documentadas en MITRE ATT&CK for ICS.
6. Analizar las consecuencias de un ciberataque sobre la operación de una instalación industrial.

## 1.5. Ponderación

| Bloque | Peso | Qué se evalúa |
|---|---:|---|
| 4.1 Descripción del escenario industrial | 15 % | Proceso, actores, protocolo, variables, operaciones, arquitectura y uso en una planta real |
| 4.2 Despliegue y análisis del tráfico | 25 % | Reproducibilidad, captura, interpretación, evidencias y ausencia/presencia de mecanismos de seguridad |
| 4.3 Investigación de amenazas con MITRE ATT&CK for ICS | 35 % | Rigor, relación con el escenario, condiciones, evidencias, consecuencias y justificación |
| 4.4 Análisis del impacto sobre el proceso | 25 % | Escenario de ataque, condiciones, efectos y priorización de la amenaza |
| 5. Actividad voluntaria: incidente real | 15 % | Incidente documentado, consecuencias, similitudes y fuentes |

**Interpretación:** los bloques 4.1 a 4.4 suman el 100 %. La actividad voluntaria indica un 15 % adicional; confirma con el profesor si se suma a la nota o si forma parte de otra escala. En cualquier caso, **el 60 % de la nota está en el análisis (4.3 + 4.4)**, no en la complejidad del montaje.

## 1.6. Entregables

1. **Memoria técnica en PDF.**
2. **Evidencias y archivos técnicos:**
   - Archivos **PCAP/PCAPNG** originales.
   - Archivo `compose.yml` o instrucciones equivalentes para reproducir el entorno.
   - **Scripts o configuraciones** desarrollados o modificados, cuando corresponda.

La entrega es **única por grupo**. No se entregan carpetas separadas por miembro; el grupo debe integrar y revisar todo.

## 1.7. Escenarios admitidos

| Protocolo | Proceso sugerido | Herramientas orientativas |
|---|---|---|
| Modbus/TCP | PLC virtual y HMI intercambian registros de proceso | PyModbus |
| MQTT | Sensores industriales publican variables hacia un sistema de supervisión | Eclipse Mosquitto y clientes MQTT |
| OPC UA | Servidor industrial expone variables y un cliente las consulta o modifica | open62541 o Python `opcua-asyncio` |
| Otro | Debe validarse antes con el profesor | Depende del protocolo |

Requisitos mínimos:

- Al menos **dos componentes** que intercambien información por una red virtual.
- Se pueden añadir elementos adicionales si el protocolo lo necesita (por ejemplo, el broker en MQTT).
- Proceso sencillo: temperatura, nivel de un depósito, supervisión de una bomba, consignas de velocidad, monitorización de variables de una máquina, etc.
- Definir qué representa cada variable, cómo se intercambia y qué consecuencias tendría su manipulación.

## 1.8. Contenido obligatorio de cada bloque

**4.1 Descripción del escenario (15 %)**

- Dispositivos o aplicaciones que participan y su función.
- Protocolo utilizado y características principales.
- Variables de proceso intercambiadas.
- Operaciones: lectura, escritura, publicación, suscripción, etc.
- Esquema sencillo de arquitectura y comunicaciones.
- Explicación de cómo se usaría en una planta industrial real.

**4.2 Despliegue y análisis del tráfico (25 %)**

- Despliegue con Docker/Podman o solución equivalente justificada.
- Generación y observación de tráfico.
- Capturas con Wireshark, tcpdump u otra herramienta compatible.
- Documentar:
  - Direcciones IP, puertos y participantes.
  - Mensajes y operaciones características.
  - Al menos dos operaciones o intercambios representativos, incluyendo alguna modificación o actualización de datos.
  - Variables o información del proceso observables.
  - Presencia o ausencia de autenticación, cifrado o protección de mensajes.
- **PCAP/PCAPNG original obligatorio**, identificando en el informe los paquetes que justifican el análisis.
- No basta con capturas de pantalla sin interpretación.

**4.3 MITRE ATT&CK for ICS (35 %)**

- Al menos **dos técnicas** relacionadas con el escenario.
- Para cada técnica:
  - Identificador y denominación.
  - Descripción del comportamiento del atacante.
  - Condiciones necesarias.
  - Relación con el protocolo o la arquitectura.
  - Posibles evidencias de ejecución.
  - Consecuencias potenciales para el proceso.
- La selección debe estar justificada.
- No basta con enumerar técnicas: hay que explicar su relación con el proceso.
- Diferenciar claramente entre **vulnerabilidades observadas**, **ataques técnicamente posibles** y **comportamientos demostrados experimentalmente**.

**4.4 Análisis del impacto (25 %)**

- Seleccionar la amenaza más relevante y desarrollar un escenario hipotético de ataque.
- Explicar cómo actuaría el atacante, qué condiciones necesitaría y qué efectos produciría.
- Considerar disponibilidad, integridad de variables, continuidad del servicio, calidad de producción y seguridad del proceso.
- Justificar por qué se considera prioritaria esa amenaza.

**5. Actividad voluntaria (15 %)**

- Investigar un incidente real documentado, relacionado con el protocolo, una técnica MITRE seleccionada o una amenaza semejante.
- Explicar qué ocurrió, qué consecuencias tuvo y qué similitudes existen con el escenario.
- La relación puede ser por el procedimiento del atacante, aunque el incidente use otro protocolo.
- Máximo una página, con fuentes.
