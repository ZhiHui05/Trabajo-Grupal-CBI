#!/bin/sh
# Captura Modbus/TCP dentro del módulo de captura.
# Uso:
#   sh capture.sh [salida.pcapng]
# El módulo de captura monta el directorio compartido en /captures.
# Variables:
#   IFACE=eth0 FILTER='tcp port 502' sh capture.sh /captures/01_baseline.pcapng
set -eu

OUT="${1:-/captures/capture_$(date +%Y%m%d_%H%M%S).pcapng}"
IFACE="${IFACE:-eth0}"
FILTER="${FILTER:-tcp port 502}"

mkdir -p "$(dirname "$OUT")"

echo "[capture] Interfaz: $IFACE"
echo "[capture] Filtro:   $FILTER"
echo "[capture] Destino:  $OUT"
echo "[capture] Detén la captura con Ctrl+C"

exec tcpdump -i "$IFACE" -s 0 -w "$OUT" "$FILTER"
