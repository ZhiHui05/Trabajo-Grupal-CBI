# 3. Despliegue del laboratorio (4.2 — 25 %)

## 3.1. Herramientas y versiones

| Herramienta | Versión | Uso |
|---|---|---|
| Docker/Podman | [ ] | [Contenedores] |
| Python | [3.12] | [Scripts] |
| PyModbus | [3.7.4] | [PLC/HMI] |
| Wireshark | [4.x] | [Análisis] |
| tcpdump | [4.99+] | [Captura] |
| [Opcional] | [ ] | [ ] |

## 3.2. Topología y direccionamiento

| Host | IP | Puerto | Función |
|---|---|---|---|
| PLC | 172.28.0.10 | 502/TCP | [ ] |
| HMI | 172.28.0.11 | Efímero | [ ] |
| Captura | Comparte HMI | — | [ ] |
| Atacante | 172.28.0.66 | Efímero | [ ] |

**Figura 2.** Topología de red. [Fuente: elaboración propia.]

## 3.3. Configuración del entorno

[Explica el `compose.yml`: servicios, red, volúmenes, healthcheck, capacidades. Incluye el archivo completo en el anexo y aquí solo los fragmentos relevantes.]

```yaml
# Fragmento relevante del compose.yml
[ ]
```

## 3.4. Procedimiento de despliegue

1. [Clonar el repositorio.]
2. [Ejecutar `docker compose up -d --build`.]
3. [Comprobar `docker compose ps`.]
4. [Revisar logs del PLC y del HMI.]
5. [Verificar conectividad y captura.]

## 3.5. Problemas encontrados y soluciones

| Problema | Causa | Solución |
|---|---|---|
| [ ] | [ ] | [ ] |

## 3.6. Reproducibilidad

- [ ] Versiones fijadas.
- [ ] Comandos documentados.
- [ ] Sin rutas absolutas.
- [ ] Prueba desde una copia limpia.
- [ ] PCAP de ejemplo incluido.
