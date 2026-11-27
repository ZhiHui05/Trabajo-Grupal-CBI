"""PLC virtual Modbus/TCP para el módulo PLC del laboratorio industrial.

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

from pymodbus.datastore import (
    ModbusSequentialDataBlock,
    ModbusServerContext,
    ModbusSlaveContext,
)
from pymodbus.server import StartAsyncTcpServer

from modbus_map import (
    CO_PUMP,
    CO_RESET,
    DI_HIGH_LEVEL,
    HR_LEVEL,
    HR_SETPOINT,
    HR_SPEED,
    HR_TEMP,
    IR_FLOW,
    IR_PRESSURE,
)
from plc.process_model import Process

LOG = logging.getLogger("plc")
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

HOST = os.getenv("MODBUS_HOST", "0.0.0.0")
PORT = int(os.getenv("MODBUS_PORT", "502"))
UNIT_ID = int(os.getenv("MODBUS_UNIT_ID", "1"))


def build_context() -> ModbusServerContext:
    """Crea las tablas Modbus en memoria y les asigna sus valores iniciales."""
    slave = ModbusSlaveContext(
        di=ModbusSequentialDataBlock(0, [0] * 32),
        co=ModbusSequentialDataBlock(0, [0] * 32),
        hr=ModbusSequentialDataBlock(0, [0] * 32),
        ir=ModbusSequentialDataBlock(0, [0] * 32),
        zero_mode=True,
    )
    # Cada tabla empieza en la dirección 0; el código 3 selecciona holding registers.
    slave.setValues(3, HR_LEVEL, [200])  # 20.0 %
    slave.setValues(3, HR_TEMP, [250])  # 25.0 C
    slave.setValues(3, HR_SETPOINT, [60])  # 60 %
    slave.setValues(3, HR_SPEED, [1450])  # 1450 rpm
    return ModbusServerContext(slaves={UNIT_ID: slave}, single=False)


async def update_process(context: ModbusServerContext, process: Process) -> None:
    """Lee órdenes Modbus, avanza el modelo y publica sus mediciones."""
    slave = context[UNIT_ID]
    last_log = 0.0

    while True:
        # FC 1 lee bobinas (CO); FC 3 lee holding registers (HR).
        pump_on = bool(slave.getValues(1, CO_PUMP, 1)[0])
        speed_rpm = int(slave.getValues(3, HR_SPEED, 1)[0])
        # La consigna se registra, pero todavía no interviene en el control de la bomba.
        setpoint = int(slave.getValues(3, HR_SETPOINT, 1)[0])
        reset = bool(slave.getValues(1, CO_RESET, 1)[0])

        process.step(pump_on, speed_rpm)

        if reset:
            # Consume la orden de reset para que el cliente pueda volver a activarla.
            slave.setValues(1, CO_RESET, [0])

        # Publica medidas en décimas: FC 3 = HR, FC 4 = IR y FC 2 = DI.
        # No sobrescribe las consignas que el HMI guarda en HR.
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

        # Un paso de simulación por vuelta; la pausa nominal es de un segundo.
        await asyncio.sleep(1.0)


async def main() -> None:
    """Prepara el PLC y ejecuta en paralelo el servidor Modbus y el ciclo del proceso."""
    LOG.info("PLC virtual Modbus/TCP en %s:%d (unit id %d)", HOST, PORT, UNIT_ID)
    context = build_context()
    process = Process()
    update_task = asyncio.create_task(update_process(context, process))
    try:
        await StartAsyncTcpServer(context=context, address=(HOST, PORT))
    finally:
        update_task.cancel()
        try:
            await update_task
        except asyncio.CancelledError:
            pass


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
