# 10. Detección y protección

> El enunciado pide proponer medidas de detección y protección adecuadas para un despliegue industrial real. Aunque 4.4 se centre en el impacto, esta sección es necesaria para cerrar el análisis.

## 10.1. Zonas y conductos (IEC 62443)

| Zona | Activos | Función | SL-T | Justificación |
|---|---|---|---|---|
| Z0 — Proceso | PLC, sensores, actuadores, SIS | Control y seguridad | 3 | Impacto alto en seguridad física |
| Z1 — Supervisión | HMI/SCADA, historian | Operación y registro | 2–3 | Integridad de datos y disponibilidad |
| Z2 — Ingeniería | Estación de ingeniería, repositorio | Mantenimiento y cambios | 2–3 | Acceso privilegiado |
| Z3 — Corporativa | Usuarios, correo, ERP | Negocio | 1–2 | No crítica para el proceso |
| Z4 — Remota | VPN, proveedores | Mantenimiento externo | 2–3 | Acceso desde fuera |

**No asumas que una VLAN es una zona.** Una zona se define por requisitos de seguridad comunes, no por la topología. Justifica por qué los activos comparten zona.

| Conducto | Origen → Destino | Protocolo | Puerto | Dirección | Medida |
|---|---|---|---|---|---|
| C1 | HMI → PLC | Modbus/TCP | 502 | HMI→PLC | Firewall DPI, allowlist de IP/FC/direcciones, IDS |
| C2 | PLC → HMI | Modbus/TCP | 502 | Respuestas | Inspección stateful |
| C3 | Historian → PLC | Modbus/TCP | 502 | Solo lectura | FC3/FC4, allowlist, cuenta de solo lectura |
| C4 | Ingeniería → PLC | Modbus/TCP | 502 | Temporal | Jump host, MFA, regla temporal |
| C5 | Corporativa → Historian | HTTPS/OPC UA | 443/4840 | Solo lectura | DMZ, proxy inverso |
| C6 | Remota → Z2 | VPN/TLS | 443 | Entrada | MFA, NAC, grabación de sesión |

## 10.2. Niveles de seguridad objetivo (SL-T)

Propuesta razonada:

- **Z0:** SL-T 3. Un fallo puede afectar a la seguridad de las personas y al medio ambiente.
- **Z1:** SL-T 2–3. La integridad de la supervisión es crítica, pero no controla directamente el proceso.
- **Z2:** SL-T 2–3. Los cambios de ingeniería pueden comprometer todo el sistema.
- **Z3:** SL-T 1–2. El riesgo es principalmente de negocio.
- **Z4:** SL-T 2–3. El acceso remoto es un vector frecuente; exige autenticación fuerte y monitorización.

No es necesario hacer un análisis formal completo; basta con justificar los niveles y relacionarlos con las medidas.

## 10.3. Medidas de protección

| Medida | FR IEC 62443 | Amenazas que mitiga | Cómo se valida |
|---|---|---|---|
| M1. Segmentación y firewall industrial con DPI | FR5 | T0836, T0855, T0842, T0814 | El atacante no alcanza el puerto 502; PCAP antes/después |
| M2. Allowlist de IP, función, dirección y rango | FR5/FR2 | T0836, T0855 | FC6 fuera de rango bloqueada; alerta |
| M3. Autenticación fuerte y MFA para acceso remoto/ingeniería | FR1 | T0830, T0836 | Sin MFA no hay sesión; logs |
| M4. TLS/VPN o Modbus/TCP Security | FR3/FR4 | T0842, T0830 | Tráfico cifrado; cliente sin certificado rechazado |
| M5. IDS/IPS con reglas Modbus | FR6 | T0836, T0855, T0814 | Alerta ante escritura desde IP no autorizada |
| M6. Baseline y detección de anomalías | FR6 | T0861, T0836, T0832 | Desviación de polling, setpoint fuera de rango |
| M7. Mínimo privilegio y roles de solo lectura | FR2 | T0836, T0855 | Usuario de historian no puede escribir |
| M8. Rate limiting y límites de conexión | FR7 | T0814 | Flood limitado; HMI sigue funcionando |
| M9. SIS independiente y alarmas locales | FR7/FR3 | T0836, T0831, T0832 | El SIS para la bomba aunque el PLC no lo haga |
| M10. Copias de seguridad, plan de respuesta y forense | FR7/FR6 | T0814, T0836 | Restauración probada; PCAP y logs conservados |
| M11. Inventario, hardening y parcheo | FR1/FR3 | Todas | Versiones, puertos y cuentas documentados |
| M12. Seguridad física y control de acceso | FR1 | Insider, T0830 | Acceso a armarios y red restringido |

## 10.4. Detección

| Detección | Fuente | Lógica | Técnica |
|---|---|---|---|
| Escritura desde IP no autorizada | PCAP/IDS | FC5/FC6/FC15/FC16 y `src != 172.28.0.11` | T0836/T0855 |
| Escritura fuera de rango | IDS/PLC | Consigna fuera de 40–80 % o velocidad > 1800 rpm | T0836 |
| Lectura secuencial anómala | IDS/NetFlow | Muchas direcciones en poco tiempo | T0861 |
| Cambio de intervalo de polling | IDS | Frecuencia distinta al baseline | T0842/T0861 |
| ARP duplicado o cambio de MAC | IDS/switch | MAC asociada a IP cambia | T0830 |
| Múltiples SYN o conexiones | Firewall/IDS | Tasa anómala al puerto 502 | T0814 |
| Discrepancia HMI–PLC | Comparador | Nivel HMI ≠ nivel PLC o ≠ medidor local | T0832 |
| Alarma de nivel alto no reconocida | HMI/PLC | LS-101 activo y bomba sigue ON | T0831 |

**Ejemplo de lógica Zeek (orientativo):**

```zeek
event modbus_message(c: connection, headers: ModbusHeaders, is_orig: bool) {
    if (is_orig && (headers$function_code == 5 || headers$function_code == 6) &&
        c$id$orig_h != 172.28.0.11) {
        NOTICE([$note=Modbus_Write_Outside_HMI,
                $msg="Escritura Modbus desde host no autorizado",
                $conn=c]);
    }
}
```

> Verifica la sintaxis y el nombre de los eventos según la versión de Zeek. Si no puedes probarlo, preséntalo como pseudocódigo y no como código validado.

**Ejemplo de regla conceptual para Suricata:** alertar sobre FC5/FC6 desde cualquier IP distinta a la del HMI. La sintaxis exacta del keyword `modbus` depende de la versión; consulta la documentación antes de incluir la regla.

## 10.5. Validación de las medidas

| Control | Antes | Después | Evidencia |
|---|---|---|---|
| Firewall | El atacante escribe FC6 | El atacante no conecta o la petición se descarta | PCAP y logs |
| Allowlist FC | FC6 a HR2 se acepta | FC6 a HR2 desde IP no autorizada se bloquea | Regla y alerta |
| IDS | No hay alerta | Alerta de escritura no autorizada | Log del IDS |
| TLS | Tráfico en claro | Tráfico cifrado; cliente sin certificado rechazado | Captura y logs |
| SIS | El nivel supera 100 % | El SIS para la bomba al 95 % | Log del SIS simulado |

La validación es lo que convierte una lista de medidas en una propuesta de ingeniería. Si no puedes implementar todas, valida al menos una y explica cómo validarías las demás.

## 10.6. Recomendaciones finales

1. **No exponer Modbus/TCP a Internet.** Nunca.
2. **Segmentar** PLC, HMI, ingeniería y corporativa; deny by default, allow by exception.
3. **Limitar** qué IP puede escribir y qué función/dirección puede usar.
4. **Monitorizar** escrituras, cambios de consigna y accesos remotos.
5. **Añadir un SIS independiente** para funciones críticas; no confiar solo en el PLC.
6. **Autenticar** el acceso remoto y de ingeniería con MFA.
7. **Cifrar** cuando el protocolo o un gateway lo permitan; si no, compensar con VPN/segmentación.
8. **Mantener** inventario, versiones, copias y un plan de respuesta.
9. **Probar** las medidas con los mismos ataques del laboratorio.
10. **Documentar** el riesgo residual y quién lo acepta.
