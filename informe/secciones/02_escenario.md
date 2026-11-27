# 2. Descripción del escenario industrial (4.1 — 15 %)

## 2.1. Proceso

El laboratorio reproduce el **lazo de llenado de un depósito** de una planta de proceso. Una bomba (`P-101`) impulsa líquido hacia el depósito; un transmisor de nivel (`LT-101`) mide cuánto hay, y el objetivo del control es mantener el nivel cerca de una **consigna** (`SP-101`, 60 % por defecto). Un transmisor de temperatura (`TT-101`), un caudalímetro (`FT-101`) y un transmisor de presión (`PT-101`) completan la instrumentación, y un interruptor de nivel alto (`LS-101`) actúa como alarma cuando el depósito se acerca al rebose.

El controlador (PLC) simula la física del depósito: con la bomba en marcha a 1450 rpm el nivel sube unos 0,8 puntos porcentuales por segundo y el caudal es de 60 L/min; con la bomba parada, el nivel baja lentamente por consumo (0,05 %/s) y el caudal y la presión caen a cero. La alarma `LS-101` se activa al llegar al 90 % y el modelo permite superar el 100 % para representar el **desbordamiento** en el escenario de ataque.

El HMI supervisa el proceso leyendo todas las variables cada segundo. En su modo de operación cierra el lazo: si el nivel baja de la consigna arranca la bomba, y si sube por encima la detiene. Esta separación de papeles —el PLC simula y publica, el HMI supervisa y manda— es la que se analiza desde el punto de vista de la ciberseguridad.

## 2.2. Actores y funciones

| Actor | Implementación | Función | Dirección |
|---|---|---|---|
| PLC virtual | Python + PyModbus 3.7.4 (`plc_server.py`) | Servidor Modbus/TCP: simula el proceso y publica las variables; acepta lecturas y escrituras | 172.28.0.10:502 |
| HMI/SCADA | Python + PyModbus (`hmi_client.py`) | Cliente Modbus: supervisa cada 1 s y, en modo `--operate`, controla consigna y bomba | 172.28.0.11 |
| Captura | tcpdump (servicio `capture` / captura en el PLC) | Registra el tráfico Modbus para análisis en Wireshark | Comparte el *namespace* del HMI |
| Atacante | Python + PyModbus (`attack_write.py`, `scan_recon.py`) | Cliente no autorizado: sondea, lee y escribe registros del PLC | 172.28.0.66 |

Los cuatro actores conviven en una red Docker aislada (`ics_net`, subred 172.28.0.0/24) con direcciones IP fijas para que el informe y las capturas sean reproducibles.

## 2.3. Protocolo de comunicación

El escenario usa **Modbus/TCP**, un protocolo industrial cliente/servidor (histórico *maestro/esclavo*) que opera sobre el **puerto TCP 502**. El cliente (HMI o atacante) abre una conexión al servidor (PLC) y le envía peticiones; el servidor responde.

Cada mensaje se compone de:

- **Cabecera MBAP** (7 bytes): identificador de transacción, identificador de protocolo (0), longitud y **Unit ID** (identificador del esclavo; en el laboratorio, 1).
- **PDU**: un **código de función** (FC) y sus datos. Los valores numéricos van en **big-endian**.

Los códigos de función usados son FC1 (*Read Coils*), FC2 (*Read Discrete Inputs*), FC3 (*Read Holding Registers*), FC4 (*Read Input Registers*), FC5 (*Write Single Coil*) y FC6 (*Write Single Register*). Si una petición no es válida, el servidor devuelve una **respuesta de excepción** (p. ej. `0x02`, *Illegal Data Address*).

La característica decisiva para este trabajo es que **Modbus/TCP no incorpora autenticación, autorización ni cifrado**. No hay usuario ni contraseña, el PLC no distingue qué cliente le escribe, y las peticiones y respuestas viajan en texto claro. Cualquier host con acceso al puerto 502 puede leer y escribir cualquier registro. Esta ausencia de controles es el origen de todas las debilidades analizadas en los bloques 4.3 y 4.4.

## 2.4. Variables de proceso

| Variable | Tag | Dirección | Tipo | FC | Escala | Origen | Significado y consecuencia de su manipulación |
|---|---|---|---|---|---|---|---|
| Nivel | LT-101 | HR 0 (40001) | uint16 | 3 | /10 % | PLC | Nivel del depósito. Falsearlo en lectura (vía MITM) ocultaría un llenado peligroso al operador |
| Temperatura | TT-101 | HR 1 (40002) | uint16 | 3 | /10 °C | PLC | Temperatura del líquido. Valor informativo en este proceso |
| Consigna | SP-101 | HR 2 (40003) | uint16 | 3/6 | % | HMI | Nivel objetivo. Subirla hace que el HMI mantenga la bomba y lleve el depósito a ese valor; es el parámetro de T0836 |
| Velocidad | PV-101 | HR 3 (40004) | uint16 | 3/6 | rpm | HMI | Velocidad de la bomba. Subirla acelera el llenado y aumenta caudal y presión |
| Bomba | P-101 | CO 0 (00001) | bool | 1/5 | 0/1 | HMI | Marcha/paro de la bomba. Forzarla a 1 arranca el llenado aunque el nivel sea alto |
| Nivel alto | LS-101 | DI 0 (10001) | bool | 2 | 0/1 | PLC | Alarma de nivel ≥ 90 %. Solo lectura para el cliente |
| Caudal | FT-101 | IR 0 (30001) | uint16 | 4 | /10 L/min | PLC | Caudal impulsado. Solo lectura |
| Presión | PT-101 | IR 1 (30002) | uint16 | 4 | /10 bar | PLC | Presión de impulsión. Solo lectura |

Las variables de solo lectura para el cliente (entradas discretas DI e *input registers* IR) representan medidas de campo; las que el cliente puede escribir (*holding registers* HR y *coils* CO) representan consignas y mandos. La manipulación de mayor impacto es la de los elementos escribibles que cierran el lazo: la consigna (HR 2), la velocidad (HR 3) y la marcha de la bomba (CO 0).

## 2.5. Operaciones

| Operación | Origen → Destino | FC | Frecuencia | Descripción |
|---|---|---|---|---|
| Lectura de nivel, temperatura, consigna y velocidad | HMI → PLC | 3 | 1 s | Lee en bloque HR 0–3 (`start=0`, `count=4`) |
| Lectura de caudal y presión | HMI → PLC | 4 | 1 s | Lee en bloque IR 0–1 |
| Lectura de nivel alto | HMI → PLC | 2 | 1 s | Lee la entrada discreta DI 0 |
| Lectura del estado de la bomba | HMI → PLC | 1 | 1 s | Lee las *coils* CO 0–1 |
| Cambio de consigna | HMI → PLC | 6 | Manual / modo operación | Escribe el nivel objetivo en HR 2 |
| Marcha o paro de la bomba | HMI → PLC | 5 | Según el nivel | Escribe CO 0 para arrancar o parar la bomba |

La captura de línea base (`01_baseline_20261127.pcapng`) registra el ciclo de lectura (FC3, FC4, FC2, FC1) repetido cada segundo; las escrituras FC6 y FC5 aparecen cuando el HMI opera o cuando un cliente las ejecuta.

## 2.6. Arquitectura y comunicaciones

La red `ics_net` es una red *bridge* de Docker con subred 172.28.0.0/24. El PLC escucha en 172.28.0.10:502; el HMI (172.28.0.11) y el atacante (172.28.0.66) son clientes. El puerto 502 **no se publica** en el equipo anfitrión: la práctica recomendada es no exponer el PLC fuera de su zona, y la red aislada evita accidentes.

```text
            ics_net  172.28.0.0/24  (Modbus/TCP, puerto 502, en claro)

   HMI 172.28.0.11  ──FC1/2/3/4 (lectura 1 s)──▶  PLC 172.28.0.10:502
        │           ──FC5/6 (escritura)────────▶   (simula el depósito
        │                                            y la bomba)
   capture (comparte namespace del HMI)                 ▲
                                                        │ FC3/FC6/FC5
   Atacante 172.28.0.66 ──sondeo, lectura y escritura──┘
```

**Figura 1.** Arquitectura del laboratorio. [Fuente: elaboración propia.]

El flujo normal es el bucle de supervisión HMI→PLC cada segundo. El flujo anómalo es el del atacante, que al estar en la misma red y sin ningún control de acceso puede dirigirse directamente al puerto 502 del PLC con las mismas funciones que el HMI.

## 2.7. Uso en una planta industrial real

El mismo patrón —un PLC que controla una bomba y un nivel, supervisado por un HMI sobre Modbus/TCP— aparece en **estaciones de bombeo de agua potable o residual, depósitos de proceso en plantas químicas y de alimentación, y sistemas de trasiego**. En una instalación real se añadirían:

- Un **historian** que registra las variables para trazabilidad y análisis.
- Una **red OT segmentada** en zonas y conductos (IEC 62443), separada de la red corporativa (IT) por cortafuegos industriales.
- **Acceso remoto** controlado (VPN, estación de salto) para mantenimiento.
- Un **SIS** (Safety Instrumented System) independiente que, ante un nivel crítico, pararía la bomba o abriría un alivio con lógica propia, al margen del PLC de control.

El laboratorio reproduce el lazo de control y su protocolo, pero deliberadamente **no** incluye segmentación, historian ni SIS: esa ausencia es la que permite mostrar las debilidades y, por contraste, justificar las medidas de protección del capítulo 7.

## 2.8. Supuestos y limitaciones del escenario

- **Proceso simulado.** La física del depósito es un modelo sencillo (`process_model.py`), no un proceso real; sirve para demostrar causas y efectos, no para dimensionar una instalación.
- **Sin SIS independiente.** No hay capa de seguridad funcional separada del control; en una planta real existiría y acotaría el impacto.
- **Red plana y aislada.** Todos los nodos comparten una única red sin segmentación, por simplicidad; en producción habría zonas, conductos y cortafuegos.
- **Sin requisitos de tiempo real.** Los tiempos de sondeo (1 s) y la simulación son holgados; no se modelan restricciones deterministas.
- **Punto de captura privilegiado.** La captura en el PLC ve todo el tráfico por construcción, lo que facilita el análisis pero no equivale a la posición de un atacante externo (se discute en 4.3).
