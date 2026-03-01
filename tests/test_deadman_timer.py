import asyncio
import unittest

from src.edge_agent.safety.deadman import DeadmanTimer


class TestDeadmanTimer(unittest.IsolatedAsyncioTestCase):
    async def test_timeout_triggers_once_until_touch(self):
        calls = 0

        async def on_timeout():
            nonlocal calls
            calls += 1

        deadman = DeadmanTimer(timeout_ms=120, on_timeout=on_timeout)
        deadman.start()

        try:
            await asyncio.sleep(0.25)
            self.assertEqual(calls, 1)

            await asyncio.sleep(0.25)
            self.assertEqual(calls, 1)

            deadman.touch()
            await asyncio.sleep(0.25)
            self.assertEqual(calls, 2)
        finally:
            deadman.stop()

    async def test_stop_prevents_timeout(self):
        calls = 0

        def on_timeout():
            nonlocal calls
            calls += 1

        deadman = DeadmanTimer(timeout_ms=150, on_timeout=on_timeout)
        deadman.start()
        deadman.stop()

        await asyncio.sleep(0.2)
        self.assertEqual(calls, 0)


if __name__ == "__main__":
    unittest.main()
