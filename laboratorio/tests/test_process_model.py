import unittest
from unittest.mock import patch

from plc.process_model import Process


class ProcessModelTests(unittest.TestCase):
    def test_running_pump_fills_tank_and_updates_measurements(self) -> None:
        process = Process()

        with patch("plc.process_model.random.uniform", return_value=0.0):
            process.step(pump_on=True, speed_rpm=1450, dt=2.0)

        self.assertAlmostEqual(process.level, 21.6)
        self.assertEqual(process.flow, 60.0)
        self.assertEqual(process.pressure, 5.0)
        self.assertFalse(process.high_level)

    def test_stopped_pump_drains_tank_and_clears_flow_and_pressure(self) -> None:
        process = Process()

        with patch("plc.process_model.random.uniform", return_value=0.0):
            process.step(pump_on=False, speed_rpm=1450, dt=3.0)

        self.assertAlmostEqual(process.level, 19.85)
        self.assertEqual(process.flow, 0.0)
        self.assertEqual(process.pressure, 0.0)

    def test_speed_and_level_are_clamped(self) -> None:
        process = Process()
        process.level = 109.5

        with patch("plc.process_model.random.uniform", return_value=0.0):
            process.step(pump_on=True, speed_rpm=5000)

        self.assertEqual(process.level, 110.0)
        self.assertAlmostEqual(process.flow, 60.0 * (3000 / 1450.0))
        self.assertAlmostEqual(process.pressure, 2.0 + 3.0 * (3000 / 1450.0))
        self.assertTrue(process.high_level)

    def test_low_level_is_clamped_and_alarm_clears(self) -> None:
        process = Process()
        process.level = 0.02
        process.high_level = True

        with patch("plc.process_model.random.uniform", return_value=0.0):
            process.step(pump_on=False, speed_rpm=0)

        self.assertEqual(process.level, 0.0)
        self.assertFalse(process.high_level)

    def test_alarm_activates_at_threshold(self) -> None:
        process = Process()
        process.level = 89.5

        with patch("plc.process_model.random.uniform", return_value=0.0):
            process.step(pump_on=True, speed_rpm=1450)

        self.assertTrue(process.high_level)


if __name__ == "__main__":
    unittest.main()
