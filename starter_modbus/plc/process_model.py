"""Modelo sencillo del depósito simulado en el laboratorio."""

from __future__ import annotations

import random


class Process:
    """Modela el depósito, la bomba y la alarma de nivel alto."""

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
            self.level += 0.8 * (speed_rpm / 1450.0) * dt
            self.flow = 60.0 * (speed_rpm / 1450.0)
            self.pressure = 2.0 + 3.0 * (speed_rpm / 1450.0)
        else:
            self.level -= 0.05 * dt
            self.flow = 0.0
            self.pressure = 0.0

        # Se permite superar el 100 % para representar el desbordamiento.
        self.level = max(0.0, min(110.0, self.level))
        self.temperature += random.uniform(-0.2, 0.2) * dt
        self.temperature = max(15.0, min(60.0, self.temperature))
        self.high_level = self.level >= 90.0
