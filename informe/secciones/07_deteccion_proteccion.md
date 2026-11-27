# 7. Detección y protección

## 7.1. Zonas y conductos

| Zona | Activos | Función | SL-T |
|---|---|---|---|
| [Z0] | [ ] | [ ] | [ ] |
| [Z1] | [ ] | [ ] | [ ] |

| Conducto | Origen → Destino | Protocolo | Puerto | Medida |
|---|---|---|---|---|
| [C1] | [HMI → PLC] | [Modbus/TCP] | [502] | [ ] |

## 7.2. Medidas de protección

| Medida | FR | Amenaza | Implementación | Validación |
|---|---|---|---|---|
| [Segmentación] | [FR5] | [T0836] | [ ] | [ ] |
| [Allowlist] | [FR5/FR2] | [T0836] | [ ] | [ ] |
| [IDS] | [FR6] | [T0836] | [ ] | [ ] |
| [SIS] | [FR7] | [T0831] | [ ] | [ ] |

## 7.3. Detección

| Detección | Fuente | Lógica | Técnica |
|---|---|---|---|
| [Escritura desde IP no autorizada] | [PCAP/IDS] | [FC6 y src != HMI] | [T0836] |
| [Cambio de ARP] | [IDS] | [MAC/IP] | [T0830] |

## 7.4. Validación

| Control | Antes | Después | Evidencia |
|---|---|---|---|
| [Firewall] | [ ] | [ ] | [ ] |
| [IDS] | [ ] | [ ] | [ ] |

## 7.5. Riesgo residual y recomendaciones

[Resume el riesgo que queda y las recomendaciones prioritarias.]
