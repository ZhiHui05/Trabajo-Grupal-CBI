# 6. Guion experimental y capturas

## 6.1. Regla de oro

Cada experimento debe tener:

1. **Objetivo** (qué quiero demostrar).
2. **Hipótesis** (qué espero ver).
3. **Comando y condiciones** (quién, cuándo, cómo).
4. **Evidencia** (PCAP, logs, tabla).
5. **Interpretación** (qué significa y qué limitaciones tiene).

No captures “a ver qué sale”. Captura para responder una pregunta.

## 6.2. Experimento 0 — Línea base

**Objetivo:** obtener el comportamiento normal del sistema y una referencia para comparar.

**Procedimiento:**

1. Arranca PLC y HMI.
2. Ejecuta un HMI en modo operación para generar escrituras normales:
   ```bash
   docker compose exec hmi python hmi_client.py --host plc --operate
   ```
3. En otra terminal, captura:
   ```bash
   docker compose exec plc tcpdump -i eth0 -s 0 -w /app/captures/01_baseline.pcapng 'tcp port 502'
   ```
4. Deja funcionar 60–120 s.
5. Detén la captura con `Ctrl+C` y el HMI en modo operación con `Ctrl+C`.

**Qué esperar:**

- Handshake TCP (SYN, SYN-ACK, ACK).
- Peticiones FC3, FC4, FC2 y FC1 cada segundo.
- Respuestas del PLC con los valores.
- Alguna escritura FC6 (consigna/velocidad) y FC5 (bomba) al inicio o durante el control.
- Ningún cifrado: los valores se ven en claro.

**Evidencia a guardar:**

- `01_baseline.pcapng`.
- Salida del HMI (`logs/hmi_baseline.txt`).
- Salida del PLC (`logs/plc_baseline.txt`).
- Fecha/hora, comandos y versiones.

## 6.3. Experimento 1 — Reconocimiento

**Objetivo:** identificar el PLC, el puerto, el Unit ID y el mapa de registros.

**Procedimiento:**

```bash
# Desde el contenedor atacante
docker compose exec attacker sh -c "nmap -p 502 172.28.0.10 || true"
docker compose exec attacker python - <<'PY'
from pymodbus.client import ModbusTcpClient
c = ModbusTcpClient("plc", port=502)
c.connect()
for addr in range(0, 12):
    r = c.read_holding_registers(addr, 1, slave=1)
    print(addr, r)
c.close()
PY
```

Si `nmap` no está instalado en la imagen, usa `python` con `socket` o `nc`; no es imprescindible. Lo importante es mostrar la **secuencia de lecturas** y la inferencia del mapa.

**Qué esperar:**

- Puerto 502 abierto.
- Respuestas con valores para direcciones válidas.
- Excepciones (0x83, código 0x02) para direcciones no válidas.
- El atacante puede leer el proceso sin credenciales.

**Evidencia:**

- `02_reconocimiento.pcapng`.
- Tabla de direcciones leídas y valores.
- Captura de pantalla del comando y la salida (con fecha/hora).

**Interpretación:** Modbus no distingue entre un cliente legítimo y uno no autorizado; el Unit ID y el Transaction ID no son credenciales.

## 6.4. Experimento 2 — Escritura no autorizada

**Objetivo:** demostrar la modificación de una consigna y el efecto sobre el proceso.

**Procedimiento:**

1. Deja el HMI en modo **monitor** (sin `--operate`) para que no revierta la escritura.
2. Inicia la captura:
   ```bash
   docker compose exec plc tcpdump -i eth0 -s 0 -w /app/captures/03_escritura_no_autorizada.pcapng 'tcp port 502'
   ```
3. Desde el atacante:
   ```bash
   docker compose exec attacker python attack_write.py --host plc --setpoint 95 --pump on --read
   ```
4. Observa el HMI: la consigna cambia a 95 %, la bomba se enciende y el nivel sube.
5. Espera a que el nivel supere el 90 % y se active la alarma.
6. Detén la captura.
7. Restaura:
   ```bash
   docker compose exec attacker python attack_write.py --host plc --setpoint 60 --pump off
   ```

**Qué esperar:**

- Petición FC6 con `HR2 = 95` desde `172.28.0.66`.
- Respuesta FC6 que repite la escritura.
- Petición FC5 con `CO0 = 1` (bomba ON).
- Respuesta FC5.
- En la siguiente consulta FC3 del HMI, el valor de consigna es 95.
- El nivel sube y `LS-101` pasa a 1 al llegar al 90 %.
- El HMI muestra la alarma.

**Evidencia:**

- `03_escritura_no_autorizada.pcapng`.
- Logs del HMI y del PLC.
- Tabla de frames: petición, respuesta, valores antes/después.
- Captura de pantalla del HMI antes y después.

**Interpretación:** cualquier host con conectividad al puerto 502 puede escribir una consigna. No hay autenticación, autorización ni integridad. La consecuencia no es solo de confidencialidad: es de **integridad y seguridad del proceso**.

## 6.5. Experimento 3 — MITM con ARP spoofing (opcional)

**Objetivo:** demostrar la posición de intermediario entre HMI y PLC (T0830).

**Procedimiento general:**

1. En el atacante, comprueba la tabla ARP:
   ```bash
   docker compose exec attacker ip neigh
   ```
2. Lanza ARP spoofing hacia HMI y PLC (herramientas: `arpspoof` de dsniff, `bettercap` o un script con Scapy). Ejemplo con `arpspoof`:
   ```bash
   # En el atacante, con IP forwarding activado
   sysctl -w net.ipv4.ip_forward=1
   arpspoof -i eth0 -t 172.28.0.11 172.28.0.10
   arpspoof -i eth0 -t 172.28.0.10 172.28.0.11
   ```
3. Captura en el atacante:
   ```bash
   tcpdump -i eth0 -s 0 -w /app/captures/04_mitm_arp.pcapng 'tcp port 502 or arp'
   ```
4. Comprueba que el HMI sigue funcionando y que su tabla ARP apunta a la MAC del atacante.
5. Detén el spoofing y restaura las tablas ARP (`arp -d` o esperar).

**Qué esperar:**

- Respuestas ARP duplicadas o no solicitadas.
- Cambio de MAC asociada a la IP del PLC en el HMI.
- Tráfico HMI↔PLC visible en el atacante.
- Posible aumento de latencia.

**Si no funciona en Docker:**

- Docker Desktop puede aislar o filtrar ARP; no es un fallo del trabajo.
- Usa un **proxy TCP** o máquinas virtuales con red host-only.
- Documenta: “T0830 se considera técnicamente posible; se demostró la posición de intermediario con un proxy / no se pudo reproducir en Docker por limitaciones de la red bridge”.
- No inventes una captura que no tienes.

**Evidencia:**

- `04_mitm_arp.pcapng`.
- Salida de `ip neigh` antes/después.
- Logs de `arpspoof`/`bettercap`.
- Captura del tráfico redirigido.

## 6.6. Experimento 4 — Denial of Service (opcional)

**Objetivo:** analizar el impacto de una denegación de servicio sobre la disponibilidad (T0814).

**Procedimiento:** un flood TCP al puerto 502 o un agotamiento de conexiones. Ejemplo con `hping3` si está instalado:

```bash
docker compose exec attacker hping3 -S -p 502 --flood 172.28.0.10
```

**Precauciones:**

- Solo en la red aislada del laboratorio.
- Limita la duración (10–30 s).
- Detén el flood y comprueba que el PLC y el HMI se recuperan.
- No lo ejecutes en la red del aula ni contra equipos ajenos.

**Qué esperar:**

- Aumento de conexiones SYN.
- Timeouts o errores de comunicación en el HMI.
- Alarmas de pérdida de comunicación.
- Posible caída del servidor si se agotan recursos.

**Evidencia:**

- `05_dos.pcapng`.
- Logs del HMI con timeouts.
- Captura de pantalla de la pérdida de comunicación.

## 6.7. Experimento 5 — Validación de controles (recomendado)

**Objetivo:** demostrar que las medidas propuestas funcionan.

**Procedimiento:**

1. Aplica una regla de firewall en el PLC o en un gateway que solo permita al HMI (`172.28.0.11`) acceder al puerto 502.
2. Repite la escritura no autorizada desde el atacante.
3. Comprueba que la conexión se bloquea o que la escritura no llega.
4. Ejecuta un IDS offline sobre el PCAP del ataque y muestra la alerta.
5. Guarda `06_after_controls.pcapng` y los logs.

**Qué esperar:**

- El atacante no puede conectar o la petición se descarta.
- El HMI sigue funcionando.
- El IDS genera una alerta para la escritura desde una IP no autorizada.
- Si se usa autenticación/TLS, el cliente sin certificado no puede escribir.

**Evidencia:**

- PCAP antes/después.
- Reglas de firewall.
- Alertas del IDS.
- Explicación del riesgo residual.

## 6.8. Cómo capturar correctamente

**Dónde capturar:**

- **En el PLC (recomendado):** ve todas las peticiones y respuestas de HMI y atacante, porque todo el tráfico del proceso pasa por él.
- **En el sidecar `capture` (opcional):** ve solo la vista del HMI; útil para comparar lo que ve el operador, pero no para demostrar la escritura del atacante.
- **En el atacante:** ve su propio tráfico; útil si se hace ARP spoofing o un proxy.
- **En el host:** solo si se usa una interfaz puente y se sabe exactamente qué se está viendo.

**Comandos:**

```bash
# Captura completa del puerto 502 en el PLC (recomendado)
docker compose exec plc tcpdump -i eth0 -s 0 -w /app/captures/01_baseline.pcapng 'tcp port 502'

# Captura desde el atacante (para su propio tráfico)
docker compose exec attacker tcpdump -i eth0 -s 0 -w /app/captures/04_mitm.pcapng 'tcp port 502 or arp'

# Ver el tráfico en vivo
docker compose exec plc tcpdump -i eth0 -nn -tttt 'tcp port 502'
```

**Buenas prácticas:**

- `-s 0` para capturar el paquete completo.
- `-w` para escribir a archivo; no analices en la terminal si puedes evitarlo.
- Filtra por `tcp port 502` para que el PCAP sea pequeño y legible.
- Una captura por experimento; no mezcles baseline y ataque.
- Anota hora de inicio/fin, comandos, versiones y estado del HMI.
- No modifiques el PCAP original; trabaja sobre copias.
- Calcula SHA-256 de cada PCAP y inclúyelo en el informe.
- Guarda los PCAP en dos sitios (repo con LFS o nube + copia local).

## 6.9. Nombres de archivo

```text
01_baseline_normal_20261120.pcapng
02_reconocimiento_20261120.pcapng
03_escritura_setpoint_20261120.pcapng
04_mitm_arp_20261120.pcapng
05_dos_20261120.pcapng
06_after_controls_20261120.pcapng
```

Incluye un `captures/README.md` con:

- Topología y direcciones.
- Comandos exactos.
- Fecha/hora y duración.
- Versiones.
- Qué demuestra cada captura.
- Hash SHA-256.

## 6.10. Evidencia mínima exigible

- [ ] Al menos un PCAP/PCAPNG original.
- [ ] Tráfico de lectura (FC3/FC4) identificado.
- [ ] Al menos una escritura (FC5/FC6) identificada.
- [ ] Una escritura no autorizada desde una IP distinta al HMI.
- [ ] Variables del proceso visibles en el tráfico.
- [ ] Ausencia de autenticación/cifrado justificada con paquetes.
- [ ] Frames concretos referenciados en el texto.
- [ ] Comandos de captura y reproducibilidad.
- [ ] Capturas de pantalla solo como apoyo, nunca como única prueba.
