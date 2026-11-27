# 6. Análisis del impacto sobre el proceso (4.4 — 25 %)

## 6.1. Amenaza seleccionada y justificación

La amenaza prioritaria es **T0836 — Modify Parameter**: la escritura no autorizada de la consigna de nivel (HR 2) y, como mando de apoyo, el arranque forzado de la bomba (CO 0, FC5 / T0855). Se elige frente a las demás técnicas del capítulo 5 por tres razones:

1. **Es la única demostrada con efecto físico.** T0842 (sniffing) y T0861 (identificación de puntos) afectan a la confidencialidad y preparan el ataque, pero no cambian el proceso. T0830 (MITM) no se reprodujo. T0836 sí modifica el estado del depósito de forma observable.
2. **Cierra la cadena de ataque.** El reconocimiento y la escucha solo tienen valor si permiten actuar; la manipulación del parámetro es la acción que convierte el acceso en daño.
3. **Su impacto alcanza la seguridad del proceso**, no solo la información: puede provocar el desbordamiento del depósito, con consecuencias para equipos, personas y medio ambiente.

## 6.2. Narrativa del ataque

1. **Acceso inicial.** El atacante (172.28.0.66) obtiene conectividad a la red `ics_net` y alcanza el puerto 502 del PLC. No necesita credenciales: Modbus/TCP no las exige.
2. **Reconocimiento.** Con `scan_recon.py` sondea el Unit ID 1 y recorre el mapa de registros (T0861), identificando que HR 2 es la consigna y CO 0 la marcha de la bomba.
3. **Recolección.** Captura el diálogo HMI–PLC en claro (T0842) y confirma el valor normal de la consigna (60 %) y el patrón de control.
4. **Acción.** Escribe `HR 2 = 95` con FC6 y fuerza `CO 0 = 1` con FC5 (`attack_write.py --setpoint 95 --pump on`). El PLC acepta ambas porque no distingue al atacante del HMI.
5. **Efecto.** La bomba se mantiene en marcha y el nivel sube ~0,75 %/s; en torno a minuto y medio alcanza el 90 % y `LS-101` pasa a 1. Si el HMI está operando con la consigna manipulada, persigue el 95 % y no detiene la bomba a tiempo.
6. **Consecuencia.** El nivel supera el 100 % (desbordamiento en el modelo). En una planta real sería vertido, daño a la bomba por funcionamiento fuera de punto, o parada de emergencia.

**Figura 5.** Escenario de ataque. [Fuente: elaboración propia.]

## 6.3. Condiciones necesarias

| Condición | ¿Se da en el laboratorio? | ¿Se daría en una planta real? |
|---|---|---|
| Conectividad al puerto 502 | Sí: el atacante está en `ics_net` y alcanza 172.28.0.10:502 | Solo si la red OT no está segmentada o hay un acceso remoto mal protegido |
| Conocimiento del mapa de registros | Sí: obtenido con `scan_recon.py` (T0861) | Sí: por reconocimiento, documentación del fabricante o ingeniería inversa |
| Ausencia de autenticación/autorización | Sí: Modbus/TCP no las implementa | Frecuente en instalaciones heredadas sin Modbus Security ni cortafuegos de aplicación |
| Ausencia de SIS o enclavamiento independiente | Sí: el laboratorio no tiene SIS | Variable: una planta bien diseñada tendría un SIS que acotaría el impacto |

El ataque es viable cuando se cumplen a la vez conectividad y ausencia de control de acceso; las medidas del capítulo 7 atacan precisamente esas dos condiciones.

## 6.4. Consecuencias

| Dimensión | Efecto | Ejemplo |
|---|---|---|
| Seguridad de las personas | Riesgo por rebose de líquido, salpicadura o reacción | Vertido de producto caliente o corrosivo cerca de operarios |
| Medio ambiente | Derrame fuera de contención | Vertido a la red de drenaje o al terreno |
| Disponibilidad | Parada de proceso y limpieza | Horas de producción perdidas tras el desbordamiento |
| Integridad | El valor del proceso deja de corresponder a la operación legítima | Consigna de 95 % que ningún operador fijó |
| Calidad | Producto fuera de especificación | Lote perdido por dilución o contaminación |
| Equipos | Bomba trabajando fuera de punto; posible cavitación o sobrepresión | Desgaste o avería de `P-101` |
| Económico | Coste de limpieza, reparación, producto y parada | Mantenimiento correctivo no planificado |
| Cumplimiento/reputación | Incidente notificable; incumplimiento ambiental | Sanción o pérdida de confianza del cliente |

## 6.5. Matriz de riesgo

Escala cualitativa 1–5; R = P × I.

| ID | Escenario | Activo | Amenaza | P | I | R | Prioridad |
|---|---|---|---|---:|---:|---:|---|
| S1 | Escritura no autorizada de consigna/bomba → desbordamiento | Depósito y bomba `P-101` | T0836 / T0855 | 4 | 5 | 20 | Alta |
| S2 | Interceptación y manipulación de la vista del operador | Comunicación HMI–PLC | T0830 / T0832 | 2 | 4 | 8 | Media |
| S3 | Escucha del tráfico y mapeo de variables | Confidencialidad del proceso | T0842 / T0861 | 5 | 2 | 10 | Media |

**Figura 6.** Matriz de riesgo. [Fuente: elaboración propia.]

## 6.6. Priorización

**S1 es la prioridad.** Aunque S3 (sniffing + mapeo) es el más probable —prácticamente seguro en una red sin cifrado—, su impacto es bajo porque solo afecta a la confidencialidad y no altera el proceso. S2 (MITM) tiene impacto alto pero probabilidad menor: exige posicionarse entre HMI y PLC, algo que en este entorno no se logró reproducir. S1 combina **probabilidad alta** (la escritura se demostró y solo requiere acceso al puerto 502, sin credenciales) con **impacto máximo** (desbordamiento, con consecuencias físicas, ambientales y de seguridad). Es, además, el escenario que materializa el daño que los otros dos solo preparan. Por eso concentra el riesgo residual que las medidas deben reducir.

## 6.7. Riesgo residual

| Escenario | Riesgo inicial | Medidas | Riesgo residual |
|---|---:|---|---:|
| S1 | 20 (Alta) | Segmentación y cortafuegos que limiten el puerto 502 al HMI; lista de control de acceso por IP; límite de consigna y enclavamiento de nivel alto en el PLC; SIS independiente; detección de escrituras desde orígenes no autorizados | 6 (Baja-Media) |

Con segmentación y un enclavamiento que pare la bomba por nivel alto con lógica independiente, la probabilidad baja (el atacante ya no alcanza el PLC con facilidad) y el impacto se acota (el desbordamiento se evita aunque la escritura llegue). El detalle de las medidas está en el capítulo 7.

## 6.8. Limitaciones

- **Proceso simulado.** El desbordamiento y sus efectos se analizan sobre el modelo `process_model.py`, no sobre una instalación real.
- **Sin SIS real.** La evaluación del riesgo residual supone un SIS que en el laboratorio no existe; su eficacia real dependería de su diseño.
- **Escalas cualitativas.** La probabilidad y el impacto se puntúan de forma cualitativa (1–5); no se dispone de datos de frecuencia reales.
- **Un solo escenario desarrollado.** El análisis se centra en S1; S2 y S3 se valoran de forma comparativa pero no se desarrollan con la misma profundidad.
