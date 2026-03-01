import unittest

from src.edge_agent.control.runtime import ControlRuntime


class FakeMotor:
    def __init__(self):
        self.speeds = []
        self.nombre = "fake-motor"

    def establecer_velocidad(self, velocidad):
        self.speeds.append(velocidad)


class FakeServo:
    def __init__(self):
        self.angles = []

    def establecer_angulo(self, angulo):
        self.angles.append(angulo)


class FakeActuator:
    def __init__(self):
        self.moves = []
        self.actions = 0

    def mover_eje(self, eje, angulo):
        self.moves.append((eje, angulo))

    def ejecutar_accion(self):
        self.actions += 1


class TestControlRuntime(unittest.TestCase):
    def setUp(self):
        self.runtime = ControlRuntime()
        self.runtime.motores = [FakeMotor(), FakeMotor()]
        self.runtime.servos_direccion = [FakeServo()]
        self.runtime.actuadores_multieje = [FakeActuator()]

    def test_movimiento_command_applies_to_motors_and_servos(self):
        ok = self.runtime.process_command({"tipo": "movimiento", "velocidad": 40, "giro": 100})
        self.assertTrue(ok)
        self.assertEqual(self.runtime.motores[0].speeds[-1], 40)
        self.assertEqual(self.runtime.motores[1].speeds[-1], 40)
        self.assertEqual(self.runtime.servos_direccion[0].angles[-1], 100)

    def test_motor_individual_only_one_motor(self):
        ok = self.runtime.process_command({"tipo": "motor_individual", "indice": 1, "velocidad": 55})
        self.assertTrue(ok)
        self.assertEqual(self.runtime.motores[0].speeds, [])
        self.assertEqual(self.runtime.motores[1].speeds[-1], 55)

    def test_actuador_multieje_moves_and_action(self):
        ok = self.runtime.process_command(
            {
                "tipo": "actuador_multieje",
                "indice": 0,
                "eje": "pan",
                "angulo": 90,
                "ejecutar_accion": True,
            }
        )
        self.assertTrue(ok)
        self.assertEqual(self.runtime.actuadores_multieje[0].moves[-1], ("pan", 90))
        self.assertEqual(self.runtime.actuadores_multieje[0].actions, 1)

    def test_stop_command_sets_all_motors_zero(self):
        ok = self.runtime.process_command({"tipo": "parar"})
        self.assertTrue(ok)
        self.assertEqual(self.runtime.motores[0].speeds[-1], 0)
        self.assertEqual(self.runtime.motores[1].speeds[-1], 0)

    def test_invalid_command_returns_false(self):
        ok = self.runtime.process_command({"foo": "bar"})
        self.assertFalse(ok)


if __name__ == "__main__":
    unittest.main()
