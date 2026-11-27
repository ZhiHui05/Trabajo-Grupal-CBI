# Checklist de entrega — Trabajo en Grupo CBI

> Imprime o copia esta lista. Marca cada punto antes de entregar.

## 1. Entregables del enunciado

- [ ] Memoria técnica en PDF.
- [ ] Al menos un PCAP/PCAPNG original.
- [ ] `compose.yml` o instrucciones equivalentes para reproducir el entorno.
- [ ] Scripts o configuraciones desarrollados/modificados.
- [ ] `README.md` con pasos de reproducción.
- [ ] Anexo de evidencias (frames, tablas, capturas).
- [ ] Actividad voluntaria de incidente real (si se realiza).
- [ ] Fuentes citadas.

## 2. Bloque 4.1 — Descripción (15 %)

- [ ] Proceso descrito y justificado.
- [ ] Actores y funciones identificados.
- [ ] Protocolo y características explicadas.
- [ ] Variables de proceso con dirección, tipo, escala y significado.
- [ ] Operaciones (lectura, escritura, publicación, suscripción) descritas.
- [ ] Esquema de arquitectura y comunicaciones.
- [ ] Uso en una planta industrial real.
- [ ] Supuestos y limitaciones.

## 3. Bloque 4.2 — Despliegue y tráfico (25 %)

- [ ] Entorno desplegado con Docker/Podman o alternativa justificada.
- [ ] Sistema genera tráfico observable.
- [ ] Captura con Wireshark/tcpdump.
- [ ] IP, puertos y participantes documentados.
- [ ] Mensajes y operaciones características.
- [ ] Al menos dos operaciones representativas.
- [ ] Alguna operación con modificación/actualización de datos.
- [ ] Variables del proceso visibles en el tráfico.
- [ ] Autenticación/cifrado/protección evaluados con evidencia.
- [ ] PCAP original incluido.
- [ ] Frames concretos referenciados en el texto.
- [ ] Capturas de pantalla interpretadas, no solo pegadas.
- [ ] Comandos de captura y condiciones documentados.
- [ ] Limitaciones del punto de captura explicadas.

## 4. Bloque 4.3 — MITRE (35 %)

- [ ] Al menos dos técnicas investigadas.
- [ ] Identificador y denominación.
- [ ] Táctica.
- [ ] Comportamiento del atacante.
- [ ] Condiciones necesarias.
- [ ] Relación con el protocolo/arquitectura.
- [ ] Evidencias posibles.
- [ ] Consecuencias potenciales.
- [ ] Justificación de la selección.
- [ ] Cadena de ataque.
- [ ] Distinción vulnerabilidad/posible/demostrado.
- [ ] Fuentes MITRE con fecha de consulta.
- [ ] Limitaciones.

## 5. Bloque 4.4 — Impacto (25 %)

- [ ] Amenaza más relevante seleccionada.
- [ ] Escenario hipotético de ataque.
- [ ] Cómo actuaría el atacante.
- [ ] Condiciones necesarias.
- [ ] Efectos sobre la instalación.
- [ ] Disponibilidad, integridad, continuidad, calidad y seguridad.
- [ ] Matriz de riesgo.
- [ ] Justificación de la prioridad.
- [ ] Riesgo residual.
- [ ] Limitaciones.

## 6. Actividad voluntaria (15 %)

- [ ] Incidente real documentado.
- [ ] Contexto y cronología.
- [ ] Vector y acción.
- [ ] Consecuencias reales.
- [ ] Relación con el escenario.
- [ ] Lecciones.
- [ ] Fuentes.
- [ ] Máximo una página.

## 7. Calidad técnica

- [ ] El laboratorio se reproduce desde una copia limpia.
- [ ] Versiones fijadas.
- [ ] Sin rutas absolutas.
- [ ] IP/puertos coherentes entre informe y `compose.yml`.
- [ ] Los frames citados existen en el PCAP.
- [ ] Los valores y escalas son coherentes.
- [ ] Las figuras son legibles.
- [ ] Las tablas tienen unidades.
- [ ] Cada figura/tabla está referenciada.
- [ ] No hay capturas sin interpretación.
- [ ] No hay afirmaciones sin evidencia o fuente.
- [ ] Limitaciones declaradas.

## 8. Formato y revisión

- [ ] Portada completa.
- [ ] Índice y números de página.
- [ ] Abreviaturas definidas.
- [ ] Ortografía y gramática.
- [ ] Referencias completas y consistentes.
- [ ] PDF exportado correctamente.
- [ ] Tamaño de archivo razonable.
- [ ] Nombres de archivo claros.
- [ ] Paquete final comprimido y probado.

## 9. Últimas 48 horas

- [ ] Prueba desde cero en otro equipo.
- [ ] Abrir el PCAP en otro Wireshark.
- [ ] Verificar frames citados.
- [ ] Revisar IP/puertos/nombres.
- [ ] Revisar figuras/tablas.
- [ ] Revisar referencias.
- [ ] Congelar contenido.
- [ ] Exportar PDF.
- [ ] Crear `SHA256SUMS.txt`.
- [ ] Entregar con margen.

## 10. Paquete final

```text
Entrega_Grupo_CBI/
├── Memoria_Grupo_CBI.pdf
├── LEEME.txt
├── SHA256SUMS.txt
├── evidencias/
│   ├── pcaps/
│   ├── capturas_pantalla/
│   └── logs/
├── laboratorio/
│   ├── compose.yml
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── scripts/
│   └── README.md
└── anexos/
```
