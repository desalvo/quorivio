"""Regression: a queued snapshot is not a WebSocket close on rolling SIGTERM."""
import asyncio
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from aiohttp import WSMsgType

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
from ci_graceful_shutdown import wait_for_restart_close


def frame(kind, data=None):
    return SimpleNamespace(type=kind, data=data)


class Socket:
    def __init__(self, frames, code=None):
        self.frames = list(frames)
        self.close_code = code

    async def receive(self, timeout=None):
        if self.frames:
            return self.frames.pop(0)
        await asyncio.sleep(timeout or .001)
        raise asyncio.TimeoutError


class RestartCloseTests(unittest.IsolatedAsyncioTestCase):
    async def test_direct_1012_close(self):
        self.assertEqual(await wait_for_restart_close(Socket([frame(WSMsgType.CLOSE, 1012)])), 0)

    async def test_queued_snapshot_then_restart_close(self):
        messages = [frame(WSMsgType.TEXT, '{"type":"snapshot","data":{}}') for _ in range(3)]
        self.assertEqual(await wait_for_restart_close(Socket(messages + [frame(WSMsgType.CLOSE, 1012)])), 3)

    async def test_previously_received_close_code_is_accepted_for_closed(self):
        self.assertEqual(await wait_for_restart_close(Socket([frame(WSMsgType.CLOSED)], 1012)), 0)

    async def test_non_restart_close_fails(self):
        with self.assertRaisesRegex(AssertionError, 'must be 1012'):
            await wait_for_restart_close(Socket([frame(WSMsgType.CLOSE, 1000)]))

    async def test_transport_error_fails(self):
        with self.assertRaisesRegex(AssertionError, 'transport error'):
            await wait_for_restart_close(Socket([frame(WSMsgType.ERROR, OSError('socket'))]))

    async def test_unexpected_application_text_fails(self):
        with self.assertRaisesRegex(AssertionError, 'unexpected application message'):
            await wait_for_restart_close(Socket([frame(WSMsgType.TEXT, '{"type":"error"}')]))

    async def test_invalid_json_fails(self):
        with self.assertRaisesRegex(AssertionError, 'invalid queued WebSocket JSON'):
            await wait_for_restart_close(Socket([frame(WSMsgType.TEXT, '{invalid}')]))

    async def test_binary_frame_fails(self):
        with self.assertRaisesRegex(AssertionError, 'unexpected WebSocket frame'):
            await wait_for_restart_close(Socket([frame(WSMsgType.BINARY, b'\x01')]))

    async def test_bound_inflight_messages(self):
        many = [frame(WSMsgType.TEXT, '{"type":"snapshot"}') for _ in range(3)]
        with self.assertRaisesRegex(AssertionError, 'too many queued'):
            await wait_for_restart_close(Socket(many), max_inflight=2)

    async def test_timeout_without_close_fails(self):
        with self.assertRaisesRegex(AssertionError, 'no 1012 restart close'):
            await wait_for_restart_close(Socket([]), seconds=.02)


if __name__ == '__main__':
    unittest.main()
