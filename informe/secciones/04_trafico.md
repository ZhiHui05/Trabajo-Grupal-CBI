# 4. Análisis del tráfico (4.2 — 25 %)

## 4.1. Método de captura

[Explica dónde se capturó, con qué comando, durante cuánto tiempo y en qué condiciones. Si se usó un sidecar, explica por qué y qué limitación tiene.]

```bash
[comando de captura]
```

## 4.2. Participantes

| Rol | IP | MAC | Puerto | Protocolo |
|---|---|---|---|---|
| [PLC] | [172.28.0.10] | [ ] | [502] | [Modbus/TCP] |
| [HMI] | [172.28.0.11] | [ ] | [ ] | [Modbus/TCP] |
| [Atacante] | [172.28.0.66] | [ ] | [ ] | [Modbus/TCP] |

## 4.3. Operaciones representativas

### 4.3.1. Operación A — [Lectura de nivel y temperatura (FC3)]

[Contexto, filtro, frames, bytes, interpretación, implicación de seguridad.]

| Campo | Bytes | Valor | Interpretación |
|---|---|---|---|
| Transaction ID | [ ] | [ ] | [ ] |
| Protocol ID | [ ] | [ ] | [ ] |
| Length | [ ] | [ ] | [ ] |
| Unit ID | [ ] | [ ] | [ ] |
| Function Code | [ ] | [ ] | [ ] |
| Dirección | [ ] | [ ] | [ ] |
| Cantidad/valor | [ ] | [ ] | [ ] |

**Figura 3.** [Captura de Wireshark o flujo de la operación.] [Fuente: elaboración propia.]

### 4.3.2. Operación B — [Cambio de consigna (FC6)]

[Contexto, filtro, frames, bytes, interpretación.]

### 4.3.3. Operación C — [Escritura no autorizada (FC6 + FC5)]

[Contexto, frames, diferencia de IP, interpretación, efecto en el proceso.]

## 4.4. Variables observadas

| Variable | Dirección | Valor observado | Unidad | Interpretación |
|---|---|---|---|---|
| [Nivel] | [HR 0] | [ ] | [%] | [ ] |
| [Temperatura] | [HR 1] | [ ] | [°C] | [ ] |
| [Consigna] | [HR 2] | [ ] | [%] | [ ] |
| [Bomba] | [CO 0] | [ ] | [0/1] | [ ] |

## 4.5. Mecanismos de seguridad

| Mecanismo | ¿Presente? | Evidencia | Consecuencia |
|---|---|---|---|
| Autenticación | [No] | [ ] | [ ] |
| Autorización | [No] | [ ] | [ ] |
| Cifrado | [No] | [ ] | [ ] |
| Integridad | [No] | [ ] | [ ] |
| Replay | [No] | [ ] | [ ] |
| Auditoría | [No] | [ ] | [ ] |
| Segmentación | [No] | [ ] | [ ] |

## 4.6. Interpretación

[Qué puede hacer un atacante con esta visibilidad. Relaciona con las propiedades de seguridad y con el proceso.]

## 4.7. Limitaciones

- [Punto de captura.]
- [Red plana.]
- [Proceso simulado.]
- [Tráfico de laboratorio, no de planta.]
