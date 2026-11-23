"""PLC virtual Modbus/TCP para el laboratorio de Ciberseguridad Industrial.

Este servidor simula un depósito con una bomba. Es deliberadamente simple y
NO incorpora autenticación, cifrado ni autorización, igual que Modbus/TCP.

Mapa de registros (direcciones cero-based; ver README):
  HR 0 (40001): nivel x10 (%)
  HR 1 (40002): temperatura x10 (C)
  HR 2 (40003): consigna de nivel (%)
  HR 3 (40004): consigna de velocidad de bomba (rpm)
  CO 0 (00001): marcha de bomba
  CO 1 (00002): reset de alarma
  DI 0 (10001): nivel alto
  IR 0 (30001): caudal x10 (L/min)
  IR 1 (30002): presión x10 (bar)
"""

from __future__ import annotations

import asyncio
import logging
import os
import random

from pymodbus.datastore import (
    ModbusSequentialDataBlock,
    ModbusServerContext,
    ModbusSlaveContext,
)
from pymodbus.server import StartAsyncTcpServer

LOG = logging.getLogger("plc")
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

HOST = os.getenv("MODBUS_HOST", "0.0.0.0")
PORT = int(os.getenv("MODBUS_PORT", "502"))
UNIT_ID = int(os.getenv("MODBUS_UNIT_ID", "1"))

HR_LEVEL = 0
HR_TEMP = 1
HR_SETPOINT = 2
HR_SPEED = 3

CO_PUMP = 0
CO_RESET = 1

DI_HIGH_LEVEL = 0

IR_FLOW = 0
IR_PRESSURE = 1


class Process:
    """Modelo muy simplificado del depósito."""

    def __init__(self) -> None:
        self.level = 20.0
        self.temperature = 25.0
        self.flow = 0.0
        self.pressure = 0.0
        self.high_level = False

    def step(self, pump_on: bool, speed_rpm: int, dt: float = 1.0) -> None:
        speed_rpm = max(0, min(int(speed_rpm), 3000))
        running = pump_on and speed_rpm > 0

        if running:
            # La bomba llena el depósito; se permite superar 100 % para
            # representar un desbordamiento en el escenario de ataque.
            self.level += 0.8 * (speed_rpm / 1450.0) * dt
            self.flow = 60.0 * (speed_rpm / 1450.0)
            self.pressure = 2.0 + 3.0 * (speed_rpm / 1450.0)
        else:
            self.level -= 0.05 * dt
            self.flow = 0.0
            self.pressure = 0.0

        self.level = max(0.0, min(110.0, self.level))
        self.temperature += random.uniform(-0.2, 0.2) * dt
        self.temperature = max(15.0, min(60.0, self.temperature))
        self.high_level = self.level >= 90.0


def build_context() -> ModbusServerContext:
    slave = ModbusSlaveContext(
        di=ModbusSequentialDataBlock(0, [0] * 32),
        co=ModbusSequentialDataBlock(0, [0] * 32),
        hr=ModbusSequentialDataBlock(0, [0] * 32),
        ir=ModbusSequentialDataBlock(0, [0] * 32),
        zero_mode=True,
    )
    # Valores iniciales coherentes con el proceso.
    slave.setValues(3, HR_LEVEL, [200])  # 20.0 %
    slave.setValues(3, HR_TEMP, [250])  # 25.0 C
    slave.setValues(3, HR_SETPOINT, [60])  # 60 %
    slave.setValues(3, HR_SPEED, [1450])  # 1450 rpm
    return ModbusServerContext(slaves={UNIT_ID: slave}, single=False)


async def update_process(context: ModbusServerContext, process: Process) -> None:
    slave = context[UNIT_ID]
    last_log = 0.0

    while True:
        pump_on = bool(slave.getValues(1, CO_PUMP, 1)[0])
        speed_rpm = int(slave.getValues(3, HR_SPEED, 1)[0])
        setpoint = int(slave.getValues(3, HR_SETPOINT, 1)[0])
        reset = bool(slave.getValues(1, CO_RESET, 1)[0])

        process.step(pump_on, speed_rpm)

        if reset:
            slave.setValues(1, CO_RESET, [0])

        # El PLC publica las medidas; no sobrescribe consignas del HMI.
        slave.setValues(3, HR_LEVEL, [int(process.level * 10)])
        slave.setValues(3, HR_TEMP, [int(process.temperature * 10)])
        slave.setValues(4, IR_FLOW, [int(process.flow * 10)])
        slave.setValues(4, IR_PRESSURE, [int(process.pressure * 10)])
        slave.setValues(2, DI_HIGH_LEVEL, [process.high_level])

        now = asyncio.get_running_loop().time()
        if now - last_log >= 10.0:
            LOG.info(
                "Nivel=%.1f%% Temp=%.1fC SP=%d%% Bomba=%s Vel=%drpm "
                "Caudal=%.1fL/min Presion=%.1fbar NivelAlto=%s",
                process.level,
                process.temperature,
                setpoint,
                "ON" if pump_on else "OFF",
                speed_rpm,
                process.flow,
                process.pressure,
                "SI" if process.high_level else "NO",
            )
            last_log = now

        await asyncio.sleep(1.0)


async def main() -> None:
    LOG.info("PLC virtual Modbus/TCP en %s:%d (unit id %d)", HOST, PORT, UNIT_ID)
    context = build_context()
    process = Process()
    asyncio.create_task(update_process(context, process))
    await StartAsyncTcpServer(context=context, address=(HOST, PORT))


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
