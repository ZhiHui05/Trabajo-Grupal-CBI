# 15. Riesgos, contingencias y preguntas para el profesor

## 15.1. Riesgos técnicos

| Riesgo | Señal | Mitigación |
|---|---|---|
| El HMI no conecta | Timeout, logs de error | Healthcheck, reintentos, revisar IP/puerto |
| El puerto 502 está ocupado | `port is already allocated` | No publicar 502; mapear 1502 |
| El PCAP no contiene tráfico | Solo ARP/broadcast | Capturar en el PLC (ve todo) o en el sidecar del HMI (solo HMI); si hace falta, ARP spoofing |
| ARP spoofing falla | El tráfico no pasa por el atacante | Proxy TCP o VMs; documentar limitación |
| PyModbus cambia | ImportError/API distinta | Versión fijada 3.7.4 |
| El PLC se cae por DoS | Sin respuesta | Reiniciar; limitar duración; no usar en producción |
| Los valores no cuadran | Escalas distintas | Documentar escala y convención de direcciones |

## 15.2. Riesgos logísticos

| Riesgo | Mitigación |
|---|---|
| Falta de tiempo | Priorizar 4.3 y 4.4; congelar 48 h antes |
| Miembros con carga desigual | RACI y revisión semanal |
| Pérdida de archivos | Git + copia en nube + USB |
| Falta de acceso a Docker | Podman/VM/equipo alternativo |
| Cambios de última hora | Rama de congelación y revisión |
| Desconocimiento del formato | Preguntar al profesor al inicio |

## 15.3. Preguntas para el profesor

1. ¿Cuál es la fecha límite exacta y la fecha de presentación?
2. ¿Cuántos miembros debe tener el grupo?
3. ¿Hay una extensión máxima o una plantilla obligatoria?
4. ¿La actividad voluntaria suma un 15 % sobre la nota o forma parte del 100 %?
5. ¿Se permite Docker Desktop/Podman en los equipos del aula?
6. ¿Es aceptable demostrar solo algunas técnicas y analizar otras como “técnicamente posibles”?
7. ¿El PCAP debe entregarse dentro del PDF o como archivo separado?
8. ¿Se exige una demostración en vivo?
9. ¿Qué estilo de citas prefiere?
10. ¿Hay alguna restricción sobre el uso de herramientas de IA?
11. ¿Se puede usar el mismo proceso que en el trabajo individual?
12. ¿Qué nivel de detalle espera en la sección de protección/detección?

## 15.4. Cómo plantear una duda al profesor

> Hola José:
>
> Estamos trabajando en el escenario de Modbus/TCP y tenemos una duda sobre [tema]. Nuestra interpretación actual es [resumen]. ¿Es correcto o preferiría que [alternativa]? Adjuntamos [captura/tabla] por si ayuda.
>
> Gracias.

Sé breve, concreto y adjunta evidencia. No preguntes algo que ya está en el enunciado.
