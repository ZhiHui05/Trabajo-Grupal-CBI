"""HMI/SCADA mínimo para el laboratorio Modbus/TCP.

Por defecto solo monitoriza (no escribe), para que una escritura del atacante
no sea revertida por el propio HMI. Con --operate simula un operador que
mantiene el nivel cerca de la consigna; ese modo se usa para generar tráfico
normal (FC3/FC4/FC2/FC1 y algunas escrituras FC5/FC6).
"""

from __future__ import annotations

import argparse
import os
import sys
import time

from pymodbus.client import ModbusTcpClient

HR_LEVEL = 0
HR_TEMP = 1
HR_SETPOINT = 2
HR_SPEED = 3

CO_PUMP = 0
CO_RESET = 1

DI_HIGH_LEVEL = 0

IR_FLOW = 0
IR_PRESSURE = 1


def connect_with_retry(host: str, port: int, retries: int = 30) -> ModbusTcpClient:
    for attempt in range(1, retries + 1):
        client = ModbusTcpClient(host, port=port)
        if client.connect():
            print(f"[HMI] Conectado a {host}:{port}", flush=True)
            return client
        print(
            f"[HMI] Intento {attempt}/{retries}: PLC no disponible en {host}:{port}",
            flush=True,
        )
        time.sleep(2.0)
    raise SystemExit(f"[HMI] No se pudo conectar a {host}:{port}")


def read_process(client: ModbusTcpClient, unit: int):
    hr = client.read_holding_registers(HR_LEVEL, 4, slave=unit)
    if hr.isError():
        raise RuntimeError(f"Error FC3: {hr}")

    ir = client.read_input_registers(IR_FLOW, 2, slave=unit)
    if ir.isError():
        raise RuntimeError(f"Error FC4: {ir}")

    di = client.read_discrete_inputs(DI_HIGH_LEVEL, 1, slave=unit)
    if di.isError():
        raise RuntimeError(f"Error FC2: {di}")

    co = client.read_coils(CO_PUMP, 2, slave=unit)
    if co.isError():
        raise RuntimeError(f"Error FC1: {co}")

    return hr.registers, ir.registers, di.bits, co.bits


def main() -> None:
    parser = argparse.ArgumentParser(description="HMI Modbus/TCP de laboratorio")
    parser.add_argument(
        "--host", default=os.getenv("PLC_HOST", "plc"), help="Host del PLC"
    )
    parser.add_argument(
        "--port", type=int, default=int(os.getenv("PLC_PORT", "502")), help="Puerto"
    )
    parser.add_argument("--unit", type=int, default=1, help="Unit ID / slave")
    parser.add_argument(
        "--operate",
        action="store_true",
        help="Simula un operador: escribe consigna y controla la bomba",
    )
    parser.add_argument(
        "--interval", type=float, default=1.0, help="Periodo de polling (s)"
    )
    args = parser.parse_args()

    client = connect_with_retry(args.host, args.port)

    if args.operate:
        # Configuración inicial del lazo (genera FC6 y FC5).
        client.write_register(HR_SETPOINT, 60, slave=args.unit)
        client.write_register(HR_SPEED, 1450, slave=args.unit)
        client.write_coil(CO_PUMP, True, slave=args.unit)
        print("[HMI] Modo operación: SP=60 %, 1450 rpm, bomba ON", flush=True)

    try:
        while True:
            hr, ir, di, co = read_process(client, args.unit)
            level = hr[HR_LEVEL] / 10.0
            temperature = hr[HR_TEMP] / 10.0
            setpoint = hr[HR_SETPOINT]
            speed = hr[HR_SPEED]
            flow = ir[IR_FLOW] / 10.0
            pressure = ir[IR_PRESSURE] / 10.0
            pump_on = bool(co[CO_PUMP])
            high_level = bool(di[DI_HIGH_LEVEL])

            print(
                f"[{time.strftime('%H:%M:%S')}] "
                f"Nivel={level:5.1f}% Temp={temperature:4.1f}C SP={setpoint:3d}% "
                f"Bomba={'ON ' if pump_on else 'OFF'} Vel={speed:4d}rpm "
                f"Caudal={flow:5.1f}L/min Presion={pressure:4.1f}bar "
                f"NivelAlto={'SI' if high_level else 'NO'}",
                flush=True,
            )

            if args.operate:
                # Control básico de nivel. No es un SIS: si el nivel es muy
                # alto, el HMI para la bomba; un atacante puede volver a
                # arrancarla, que es precisamente lo que se quiere demostrar.
                if level >= 95.0 and pump_on:
                    client.write_coil(CO_PUMP, False, slave=args.unit)
                elif level < setpoint - 5.0 and not pump_on:
                    client.write_coil(CO_PUMP, True, slave=args.unit)
                elif level > setpoint + 5.0 and pump_on:
                    client.write_coil(CO_PUMP, False, slave=args.unit)

            time.sleep(args.interval)

    except KeyboardInterrupt:
        print("\n[HMI] Detenido", flush=True)
    except Exception as exc:  # noqa: BLE001 - laboratorio
        print(f"[HMI] Error: {exc}", file=sys.stderr, flush=True)
        raise
    finally:
        client.close()


if __name__ == "__main__":
    main()
