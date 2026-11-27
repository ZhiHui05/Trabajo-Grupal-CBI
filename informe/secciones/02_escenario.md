# 2. Descripción del escenario industrial (4.1 — 15 %)

## 2.1. Proceso

[Describe el proceso: depósito, bomba, sensor de nivel, temperatura, HMI. Explica qué representa cada variable y qué se controla.]

## 2.2. Actores y funciones

| Actor | Implementación | Función | Dirección |
|---|---|---|---|
| PLC virtual | [PyModbus] | [Control y simulación] | [172.28.0.10:502] |
| HMI/SCADA | [Python] | [Supervisión y mando] | [172.28.0.11] |
| Captura | [tcpdump] | [Captura de tráfico] | [Comparte HMI] |
| Atacante | [PyModbus] | [Pruebas de escritura] | [172.28.0.66] |

## 2.3. Protocolo de comunicación

[Explica Modbus/TCP: cliente/servidor, puerto 502, MBAP, PDU, function codes, big-endian, ausencia de autenticación/cifrado, Unit ID, excepciones. Incluye una figura o tabla.]

## 2.4. Variables de proceso

| Variable | Tag | Dirección | Tipo | FC | Escala | Origen | Significado |
|---|---|---|---|---|---|---|---|
| Nivel | LT-101 | HR 0 (40001) | uint16 | 3 | /10 % | PLC | [ ] |
| Temperatura | TT-101 | HR 1 (40002) | uint16 | 3 | /10 °C | PLC | [ ] |
| Consigna | SP-101 | HR 2 (40003) | uint16 | 3/6 | % | HMI | [ ] |
| Velocidad | PV-101 | HR 3 (40004) | uint16 | 3/6 | rpm | HMI | [ ] |
| Bomba | P-101 | CO 0 (00001) | bool | 1/5 | 0/1 | HMI | [ ] |
| Nivel alto | LS-101 | DI 0 (10001) | bool | 2 | 0/1 | PLC | [ ] |
| Caudal | FT-101 | IR 0 (30001) | uint16 | 4 | /10 L/min | PLC | [ ] |
| Presión | PT-101 | IR 1 (30002) | uint16 | 4 | /10 bar | PLC | [ ] |

## 2.5. Operaciones

| Operación | Origen → Destino | FC | Frecuencia | Descripción |
|---|---|---|---|---|
| [Lectura de nivel] | [HMI → PLC] | [3] | [1 s] | [ ] |
| [Lectura de caudal] | [HMI → PLC] | [4] | [1 s] | [ ] |
| [Cambio de consigna] | [HMI → PLC] | [6] | [Manual] | [ ] |
| [Marcha de bomba] | [HMI → PLC] | [5] | [Según nivel] | [ ] |

## 2.6. Arquitectura y comunicaciones

[Incluye el diagrama. Debe mostrar PLC, HMI, captura/atacante, red y puertos. Explica el flujo de las operaciones principales.]

**Figura 1.** Arquitectura del laboratorio. [Fuente: elaboración propia.]

## 2.7. Uso en una planta industrial real

[Explica cómo se trasladaría el escenario a una planta de agua, química, alimentación, etc. Menciona PLC, HMI, historian, red OT, acceso remoto y SIS.]

## 2.8. Supuestos y limitaciones del escenario

- [Proceso simulado.]
- [Sin SIS independiente.]
- [Red plana aislada.]
- [Sin requisitos de tiempo real.]
