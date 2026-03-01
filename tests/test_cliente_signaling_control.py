import unittest

from cliente_vehiculo import ClienteVehiculo


class DummyDeadman:
    def __init__(self):
        self.touches = 0

    def touch(self):
        self.touches += 1


class DummyRuntime:
    def __init__(self, result):
        self.result = result

    def process_command(self, _raw):
        return self.result


class TestClienteControlPath(unittest.TestCase):
    def test_control_ok_touches_deadman_and_increments_metric(self):
        cliente = ClienteVehiculo()
        cliente.control_runtime = DummyRuntime(True)
        cliente.deadman = DummyDeadman()

        before = cliente.metrics.snapshot()["counters"].get("control_commands_ok", 0)
        cliente.procesar_comando_control('{"tipo":"parar"}')
        after = cliente.metrics.snapshot()["counters"].get("control_commands_ok", 0)

        self.assertEqual(cliente.deadman.touches, 1)
        self.assertEqual(after, before + 1)

    def test_control_invalid_increments_invalid_metric(self):
        cliente = ClienteVehiculo()
        cliente.control_runtime = DummyRuntime(False)
        cliente.deadman = DummyDeadman()

        before = cliente.metrics.snapshot()["counters"].get("control_commands_invalid", 0)
        cliente.procesar_comando_control('{"foo":"bar"}')
        after = cliente.metrics.snapshot()["counters"].get("control_commands_invalid", 0)

        self.assertEqual(cliente.deadman.touches, 0)
        self.assertEqual(after, before + 1)


if __name__ == "__main__":
    unittest.main()
