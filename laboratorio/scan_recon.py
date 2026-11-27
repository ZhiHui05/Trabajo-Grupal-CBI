"""Reconocimiento Modbus/TCP para el laboratorio (MITRE T0861).

Este script SOLO LEE. Sirve para demostrar como un cliente sin credenciales
puede descubrir el PLC, el Unit ID y el mapa de registros, y para generar la
evidencia de la tecnica T0861 (Point & Tag Identification).

Uso exclusivamente academico. No lo ejecutes contra equipos ajenos.

Ejemplos:
  python scan_recon.py --host plc
  python scan_recon.py --host plc --units 1 --hr-count 12 --delay 0.2
  python scan_recon.py --host 172.28.0.10 --out-dir /app/captures
"""

from __future__ import annotations

import argparse
import csv
import socket
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from pymodbus.client import ModbusTcpClient

# Mapa de registros del PLC del laboratorio (ver laboratorio/README.md).
# La escala es el divisor que convierte el valor crudo en unidad de ingenieria.
HR_TAGS = {
    0: ("LT-101", "Nivel", 10.0, "%"),
    1: ("TT-101", "Temperatura", 10.0, "C"),
    2: ("SP-101", "Consigna de nivel", 1.0, "%"),
    3: ("PV-101", "Consigna de velocidad", 1.0, "rpm"),
}
CO_TAGS = {
    0: ("P-101", "Marcha de bomba"),
    1: ("RESET", "Reset de alarma"),
}
DI_TAGS = {
    0: ("LS-101", "Nivel alto"),
}
IR_TAGS = {
    0: ("FT-101", "Caudal", 10.0, "L/min"),
    1: ("PT-101", "Presion", 10.0, "bar"),
}

FC_NAMES = {1: "FC1 Read Coils", 2: "FC2 Read Discrete Inputs",
            3: "FC3 Read Holding Registers", 4: "FC4 Read Input Registers"}


@dataclass
class Row:
    fc: int
    address: int
    reference: str
    value: str
    tag: str
    note: str = ""


def parse_units(spec: str) -> list[int]:
    """Convierte '0-5,247' en [0, 1, 2, 3, 4, 5, 247]."""
    units: list[int] = []
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            start, end = part.split("-", 1)
            units.extend(range(int(start), int(end) + 1))
        else:
            units.append(int(part))
    return sorted(set(units))


def tcp_probe(host: str, port: int, timeout: float) -> float | None:
    """Devuelve la latencia en ms si el puerto TCP esta abierto, o None."""
    start = time.perf_counter()
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return (time.perf_counter() - start) * 1000.0
    except OSError:
        return None


def error_text(result) -> str:
    code = getattr(result, "exception_code", None)
    if isinstance(code, int):
        names = {1: "Illegal Function", 2: "Illegal Data Address",
                 3: "Illegal Data Value", 4: "Slave Device Failure",
                 11: "Gateway Target Failed to Respond"}
        return "excepcion 0x%02X (%s)" % (code, names.get(code, "desconocida"))
    return "sin respuesta o error de transporte"


def read_hr(client: ModbusTcpClient, unit: int, address: int) -> tuple[int | None, str]:
    result = client.read_holding_registers(address, count=1, slave=unit)
    if result.isError():
        return None, error_text(result)
    return int(result.registers[0]), ""


def read_co(client: ModbusTcpClient, unit: int, address: int) -> tuple[int | None, str]:
    result = client.read_coils(address, count=1, slave=unit)
    if result.isError():
        return None, error_text(result)
    return int(bool(result.bits[0])), ""


def read_di(client: ModbusTcpClient, unit: int, address: int) -> tuple[int | None, str]:
    result = client.read_discrete_inputs(address, count=1, slave=unit)
    if result.isError():
        return None, error_text(result)
    return int(bool(result.bits[0])), ""


def read_ir(client: ModbusTcpClient, unit: int, address: int) -> tuple[int | None, str]:
    result = client.read_input_registers(address, count=1, slave=unit)
    if result.isError():
        return None, error_text(result)
    return int(result.registers[0]), ""


def format_value(raw: int, scale: float | None, unit: str | None) -> str:
    if scale is None:
        return str(raw)
    return ("%.1f %s" % (raw / scale, unit or "")).strip()


def scan_unit(client: ModbusTcpClient, unit: int, hr_count: int,
              delay: float, probe_addr: int, use_tags: bool = True) -> list[Row]:
    rows: list[Row] = []
    hr_tags = HR_TAGS if use_tags else {}
    co_tags = CO_TAGS if use_tags else {}
    di_tags = DI_TAGS if use_tags else {}
    ir_tags = IR_TAGS if use_tags else {}

    # Lecturas individuales y secuenciales: es el patron que delata T0861.
    for address in range(hr_count):
        raw, error = read_hr(client, unit, address)
        tag = hr_tags.get(address)
        if error:
            rows.append(Row(3, address, "4%04d" % (address + 1), "-",
                            tag[0] if tag else "desconocido", error))
        elif tag:
            name, description, scale, units = tag
            rows.append(Row(3, address, "4%04d" % (address + 1),
                            str(raw), name,
                            "%s; %s" % (description, format_value(raw, scale, units))))
        else:
            rows.append(Row(3, address, "4%04d" % (address + 1),
                            str(raw), "sin etiquetar",
                            "direccion valida del bloque, sin variable asignada"))
        time.sleep(delay)

    for address in (0, 1):
        raw, error = read_co(client, unit, address)
        tag = co_tags.get(address)
        rows.append(Row(1, address, "0%04d" % (address + 1),
                        "-" if error else str(raw),
                        tag[0] if tag else "sin etiquetar",
                        error or (tag[1] if tag else "lectura cruda")))
        time.sleep(delay)

    raw, error = read_di(client, unit, 0)
    tag = di_tags.get(0)
    rows.append(Row(2, 0, "10001", "-" if error else str(raw),
                    tag[0] if tag else "sin etiquetar",
                    error or (tag[1] if tag else "lectura cruda")))
    time.sleep(delay)

    for address in (0, 1):
        raw, error = read_ir(client, unit, address)
        tag = ir_tags.get(address)
        if error:
            rows.append(Row(4, address, "3%04d" % (address + 1), "-",
                            tag[0] if tag else "desconocido", error))
        elif tag:
            name, description, scale, units = tag
            rows.append(Row(4, address, "3%04d" % (address + 1),
                            str(raw), name,
                            "%s; %s" % (description, format_value(raw, scale, units))))
        else:
            rows.append(Row(4, address, "3%04d" % (address + 1),
                            str(raw), "sin etiquetar", "lectura cruda"))
        time.sleep(delay)

    # Sonda fuera del bloque declarado: debe devolver excepcion 0x02.
    raw, error = read_hr(client, unit, probe_addr)
    rows.append(Row(3, probe_addr, "4%04d" % (probe_addr + 1),
                    "-" if error else str(raw), "fuera de mapa",
                    error or "respondio: la direccion existe"))
    return rows


def write_csv(path: Path, rows: list[Row]) -> None:
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.writer(handle, delimiter=";")
        writer.writerow(["FC", "Direccion", "Referencia", "Valor", "Variable", "Interpretacion"])
        for row in rows:
            writer.writerow([row.fc, row.address, row.reference, row.value,
                             row.tag, row.note])


def write_markdown(path: Path, rows: list[Row]) -> None:
    lines = [
        "| FC | Direccion | Referencia | Valor | Variable inferida | Interpretacion |",
        "|---|---|---|---|---|---|",
    ]
    for row in rows:
        lines.append("| %d | %d | %s | %s | %s | %s |" % (
            row.fc, row.address, row.reference, row.value, row.tag, row.note))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Reconocimiento Modbus/TCP del laboratorio (T0861)")
    parser.add_argument("--host", default="plc", help="Host del PLC")
    parser.add_argument("--port", type=int, default=502, help="Puerto TCP")
    parser.add_argument("--units", default="0-5,247",
                        help="Unit IDs a sondear; admite rangos: 1 o 0-5,247")
    parser.add_argument("--hr-count", type=int, default=12,
                        help="Numero de holding registers a leer desde 0")
    parser.add_argument("--delay", type=float, default=0.15,
                        help="Pausa entre lecturas (s) para que el PCAP muestre el sondeo")
    parser.add_argument("--probe-addr", type=int, default=32,
                        help="Direccion HR fuera del mapa para forzar excepcion")
    parser.add_argument("--timeout", type=float, default=1.5,
                        help="Timeout de conexion y de respuesta (s)")
    parser.add_argument("--out-dir", default=".",
                        help="Directorio donde dejar el CSV y el Markdown")
    parser.add_argument("--raw", action="store_true",
                        help="No usar el mapa conocido: muestra direcciones y valores crudos")
    args = parser.parse_args()

    print("[1] Comprobando %s:%d ..." % (args.host, args.port))
    latency = tcp_probe(args.host, args.port, args.timeout)
    if latency is None:
        print("[!] El puerto %d no responde en %s" % (args.port, args.host),
              file=sys.stderr)
        raise SystemExit(1)
    print("[+] Puerto %d/tcp abierto (%.1f ms)" % (args.port, latency))

    client = ModbusTcpClient(args.host, port=args.port,
                             timeout=args.timeout, retries=1)
    if not client.connect():
        print("[!] No se pudo establecer la sesion Modbus/TCP", file=sys.stderr)
        raise SystemExit(1)

    try:
        print("[2] Sondeando Unit IDs: %s" % args.units)
        responding: list[int] = []
        for unit in parse_units(args.units):
            raw, error = read_hr(client, unit, 0)
            if raw is None:
                print("    unit %-3d -> %s" % (unit, error))
            else:
                print("    unit %-3d -> responde (HR0=%d)" % (unit, raw))
                responding.append(unit)

        if not responding:
            print("[!] Ningun Unit ID respondio", file=sys.stderr)
            raise SystemExit(1)

        unit = responding[0]
        print("[+] Unit ID accesible: %d" % unit)
        print("[3] Leyendo el mapa de registros del unit %d ..." % unit)
        rows = scan_unit(client, unit, args.hr_count, args.delay,
                         args.probe_addr, use_tags=not args.raw)
    finally:
        client.close()

    header = "FC  Dir      Ref      Valor  Variable       Interpretacion"
    print(header)
    print("-" * len(header))
    for row in rows:
        print("%-3d %-7d  %-7s  %-5s  %-13s  %s" % (
            row.fc, row.address, row.reference, row.value, row.tag, row.note))

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    prefix = "recon_%s_%s" % (args.host.replace(".", "_"), stamp)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    csv_path = out_dir / (prefix + ".csv")
    md_path = out_dir / (prefix + ".md")
    write_csv(csv_path, rows)
    write_markdown(md_path, rows)

    print("[+] CSV: %s" % csv_path)
    print("[+] Markdown: %s" % md_path)
    print("[i] Recuerda capturar en paralelo: tcpdump -i eth0 -w ... 'tcp port 502'")


if __name__ == "__main__":
    main()
