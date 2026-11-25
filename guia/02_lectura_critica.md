# 2. Lectura crítica: qué se evalúa realmente

## 2.1. El reparto de esfuerzo correcto

Con la ponderación en la mano, el esfuerzo debería parecerse a esto:

| Actividad | Esfuerzo orientativo | Por qué |
|---|---:|---|
| Montaje del laboratorio | 20–25 % | Es necesario, pero no es el objetivo final; no sobreingenierizar |
| Captura y análisis de tráfico | 20–25 % | Genera las evidencias que sostienen todo el informe |
| MITRE ATT&CK for ICS | 25–30 % | Es el bloque con más peso (35 %) |
| Impacto y priorización | 15–20 % | Es el otro bloque grande (25 %) |
| Redacción e integración | 10–15 % | Un buen análisis mal explicado pierde puntos |

Un error típico es dedicar dos semanas a Docker y dos días a MITRE. El enunciado premia la comprensión y la justificación, no la complejidad del despliegue.

## 2.2. Las tres categorías que el profesor quiere ver separadas

El enunciado pide explícitamente diferenciar:

| Categoría | Definición | Ejemplo en Modbus/TCP |
|---|---|---|
| **Vulnerabilidad observada** | Debilidad que se deduce del protocolo, la configuración o el tráfico capturado | Modbus/TCP no autentica ni cifra; el puerto 502 está accesible desde toda la red del laboratorio |
| **Ataque técnicamente posible** | Ataque que podría ejecutarse con las condiciones adecuadas, aunque no se haya demostrado en el laboratorio | ARP spoofing para modificar respuestas Modbus y engañar al HMI |
| **Comportamiento demostrado** | Ataque ejecutado y evidenciado con capturas, logs o cambios en el proceso | Escritura FC6 de la consigna de nivel desde el contenedor atacante y subida real del nivel |

Incluye una tabla o un párrafo con esta distinción. Es una de las formas más sencillas de demostrar rigor.

## 2.3. Errores que penalizan

| Error | Por qué es grave | Cómo evitarlo |
|---|---|---|
| Elegir un protocolo complejo y no llegar al análisis | El 60 % de la nota está en el análisis | Modbus/TCP o MQTT; evitar OPC UA si no hay experiencia |
| Enseñar capturas de Wireshark sin interpretar | El enunciado lo prohíbe expresamente | Explicar campos, valores, función y consecuencia de cada paquete |
| Confundir vulnerabilidad con ataque | Se pierde rigor | Usar la tabla de las tres categorías |
| Copiar descripciones de MITRE sin relación con el escenario | El enunciado lo prohíbe | Cada técnica debe tener condiciones, evidencias y consecuencias propias |
| Analizar solo confidencialidad | El impacto industrial es físico | Incluir integridad, disponibilidad y seguridad del proceso |
| PCAP inexistente o con tráfico irrelevante | Es un requisito obligatorio | Capturar solo el laboratorio y referenciar frames concretos |
| IP/puertos incoherentes entre informe y compose | Rompe la reproducibilidad | Una única tabla de direccionamiento y revisión cruzada |
| Dejar la integración para el final | Es el fallo más común | Congelar contenido 48 h antes y hacer una prueba desde cero |

## 2.4. Qué significa “justificar técnicamente”

No basta con decir “Modbus es inseguro”. Hay que escribir algo como:

> Modbus/TCP no define autenticación, cifrado ni integridad a nivel de protocolo. En la captura, la petición FC6 del frame 128 viaja en texto claro y cualquier host con conectividad al puerto 502 puede reproducirla. El servidor no distingue si el cliente es el HMI legítimo o el contenedor atacante; solo comprueba que la dirección sea válida. Por eso la escritura de la consigna en el frame 128 fue aceptada y el nivel comenzó a subir en los frames 130–190.

Eso es análisis: protocolo + evidencia + consecuencia.

## 2.5. Enfoque recomendado

1. **Semana 1:** elegir escenario, definir variables y arquitectura, montar el esqueleto.
2. **Semana 2:** conseguir tráfico normal, capturarlo y analizarlo; primera escritura no autorizada.
3. **Semana 3:** investigación MITRE, impacto, medidas de protección y, si da tiempo, MITM/DoS.
4. **Semana 4:** integración, reproducibilidad, revisión y entrega.

La guía desarrolla este plan en la sección 13.
