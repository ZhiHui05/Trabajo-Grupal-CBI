# 3. Elección del escenario y del protocolo

## 3.1. Comparativa

| Criterio | Modbus/TCP | MQTT | OPC UA |
|---|---|---|---|
| Complejidad de montaje | Baja | Baja-media | Media-alta |
| Modelo | Cliente/servidor | Publicación/suscripción con broker | Cliente/servidor con servicios |
| Puerto habitual | 502/TCP | 1883/TCP (8883 con TLS) | 4840/TCP |
| Seguridad nativa | Ninguna | Usuario/contraseña, TLS y ACL configurables | Certificados, firmas, cifrado y autenticación |
| Facilidad para mostrar debilidades | Muy alta | Alta si se configura sin TLS/ACL | Media: es seguro por diseño; hay que buscar mala configuración |
| Herramientas | PyModbus, mbtget, Wireshark | Mosquitto, `mosquitto_pub/sub`, MQTT Explorer | open62541, `opcua-asyncio`, UaExpert |
| Relación con MITRE | Muy directa | Directa | Directa |
| Riesgo de quedarse sin tiempo | Bajo | Bajo | Alto |
| Recomendación | **Primera opción** | Buena alternativa | Solo con experiencia previa |

## 3.2. Recomendación: Modbus/TCP

Para este enunciado, Modbus/TCP es la opción más eficiente por estas razones:

- Es un protocolo **cliente/servidor simple**, con peticiones y respuestas fáciles de identificar en Wireshark.
- **No tiene autenticación, cifrado ni integridad**, lo que permite demostrar debilidades sin tener que “romper” configuraciones artificialmente.
- El mapa de registros se traduce directamente en variables de proceso: nivel, temperatura, consigna, bomba.
- Permite demostrar **lectura no autorizada**, **escritura no autorizada**, **sniffing**, **MITM** y **DoS** con herramientas sencillas.
- Tiene abundante documentación y ejemplos, y una relación clara con técnicas de MITRE ATT&CK for ICS.
- El montaje con Docker es pequeño: PLC virtual, HMI y un contenedor de captura/ataque.

## 3.3. Cuándo elegir MQTT

MQTT es una buena alternativa si el grupo quiere explorar:

- Broker como elemento central y **ACL por tópico**.
- Autenticación con usuario/contraseña o certificados de cliente.
- TLS y comparación entre configuración segura e insegura.
- Enumeración de tópicos, publicación no autorizada y suplantación de sensores.

Es especialmente interesante si el grupo quiere demostrar **cómo una mala configuración del broker** anula las protecciones que el protocolo sí ofrece. El esfuerzo es algo mayor que Modbus, pero sigue siendo asumible.

## 3.4. Cuándo elegir OPC UA

OPC UA es la opción más rica en seguridad, pero también la más costosa de montar:

- Certificados, confianza mutua, políticas de seguridad y modos de autenticación.
- Address Space, nodos, servicios y sesiones.
- Herramientas como UaExpert y `opcua-asyncio`.

Si el grupo elige OPC UA, el análisis debe centrarse en **malas configuraciones** (por ejemplo, `SecurityPolicy: None`, usuarios anónimos, certificados no verificados), no en afirmar que OPC UA es inseguro. Es fácil que el montaje consuma el tiempo del análisis.

## 3.5. Checklist de decisión

Antes de confirmar el protocolo, el grupo debería responder:

- [ ] ¿Tenemos Docker Desktop o Podman funcionando en al menos dos equipos?
- [ ] ¿Alguien del grupo puede escribir y depurar Python con soltura?
- [ ] ¿Podemos dedicar 3–4 semanas al trabajo?
- [ ] ¿Queremos demostrar un impacto físico (nivel, bomba, temperatura)?
- [ ] ¿El protocolo elegido está aprobado por el profesor?
- [ ] ¿Tenemos un plan B si la red de Docker no permite ARP spoofing?
- [ ] ¿Sabemos qué técnicas de MITRE vamos a investigar antes de montar el laboratorio?

Si alguna respuesta es “no”, Modbus/TCP reduce el riesgo.

## 3.6. Propuesta de escenario para enviar al profesor

> **Asunto:** Propuesta de escenario — Trabajo en Grupo CBI
>
> Hola José:
>
> El grupo [integrantes] propone trabajar con **Modbus/TCP** en un escenario de **control de nivel de un depósito**. El laboratorio constará de un PLC virtual (PyModbus) que expone nivel, temperatura, consigna y estado de bomba; un HMI que consulta y modifica variables; y un contenedor de captura/análisis en una red Docker aislada. Analizaremos el tráfico con Wireshark, demostraremos lectura y escritura no autorizadas y relacionaremos el comportamiento con técnicas de MITRE ATT&CK for ICS (T0842, T0861, T0836 y T0830), además de proponer medidas de detección y protección.
>
> ¿Le parece adecuado el alcance? Quedamos a la espera de su confirmación.
>
> Gracias y un saludo.
