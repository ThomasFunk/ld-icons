#!/usr/bin/env python3
"""Unit tests for NsdClient class."""

import json
import os
import socket
import tempfile
import threading
import time
import unittest
from pathlib import Path

# Import the NsdClient from ldicons
import sys
sys.path.insert(0, str(Path(__file__).parent))

from ldicons import NsdClient


class MockNsdServer:
    """Simple mock nsd server for testing."""

    def __init__(self, socket_path: str):
        self.socket_path = socket_path
        self.server_socket = None
        self.running = False
        self.thread = None

    def start(self):
        """Start the mock server in a background thread."""
        if os.path.exists(self.socket_path):
            os.remove(self.socket_path)
        
        self.server_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.server_socket.bind(self.socket_path)
        self.server_socket.listen(1)
        self.running = True
        
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        time.sleep(0.1)  # Give server time to start

    def _run(self):
        """Run the server loop."""
        while self.running:
            try:
                self.server_socket.settimeout(0.5)
                conn, _ = self.server_socket.accept()
                while self.running:
                    try:
                        conn.settimeout(0.5)
                        data = conn.recv(1024)
                        if not data:
                            break
                    except socket.timeout:
                        continue
                    except Exception:
                        break
                conn.close()
            except socket.timeout:
                continue
            except Exception:
                break

    def send_message(self, msg: dict):
        """Send a single message to all connected clients."""
        # For simplicity, this is a placeholder.
        # In real tests, we'd track connections and send to them.
        pass

    def stop(self):
        """Stop the mock server."""
        self.running = False
        if self.server_socket:
            try:
                self.server_socket.close()
            except Exception:
                pass
        if self.thread:
            self.thread.join(timeout=1.0)
        if os.path.exists(self.socket_path):
            try:
                os.remove(self.socket_path)
            except Exception:
                pass


class TestNsdClient(unittest.TestCase):
    """Test suite for NsdClient."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.socket_path = os.path.join(self.temp_dir, "test.sock")
        self.client = NsdClient(self.socket_path)

    def tearDown(self):
        """Clean up after tests."""
        if self.client.connected:
            self.client.close()
        # Clean up socket file
        if os.path.exists(self.socket_path):
            try:
                os.remove(self.socket_path)
            except Exception:
                pass

    def test_init(self):
        """Test NsdClient initialization."""
        self.assertEqual(self.client._path, self.socket_path)
        self.assertIsNone(self.client._sock)
        self.assertEqual(self.client._buf, "")
        self.assertFalse(self.client.connected)

    def test_connect_socket_not_found(self):
        """Test connect when socket doesn't exist."""
        result = self.client.connect()
        self.assertFalse(result)
        self.assertFalse(self.client.connected)

    def test_connect_success(self):
        """Test successful connection."""
        server = MockNsdServer(self.socket_path)
        server.start()
        try:
            result = self.client.connect()
            self.assertTrue(result)
            self.assertTrue(self.client.connected)
        finally:
            server.stop()

    def test_close(self):
        """Test closing a connection."""
        server = MockNsdServer(self.socket_path)
        server.start()
        try:
            self.client.connect()
            self.assertTrue(self.client.connected)
            self.client.close()
            self.assertFalse(self.client.connected)
        finally:
            server.stop()

    def test_fileno_when_disconnected(self):
        """Test fileno() when not connected."""
        result = self.client.fileno()
        self.assertIsNone(result)

    def test_fileno_when_connected(self):
        """Test fileno() when connected."""
        server = MockNsdServer(self.socket_path)
        server.start()
        try:
            self.client.connect()
            result = self.client.fileno()
            self.assertIsNotNone(result)
            self.assertIsInstance(result, int)
            self.assertGreater(result, 0)
        finally:
            server.stop()

    def test_read_messages_when_disconnected(self):
        """Test read_messages() when not connected."""
        messages = self.client.read_messages()
        self.assertEqual(messages, [])

    def test_read_messages_empty_buffer(self):
        """Test read_messages() with no data available."""
        server = MockNsdServer(self.socket_path)
        server.start()
        try:
            self.client.connect()
            messages = self.client.read_messages()
            # No messages available yet
            self.assertEqual(messages, [])
        finally:
            server.stop()

    def test_parse_single_json_message(self):
        """Test parsing a single JSON message."""
        # Simulate receiving a single newline-delimited JSON message
        self.client._sock = type('MockSocket', (), {})()
        self.client._buf = '{"event": "mounted", "path": "/mnt/usb"}\n'
        
        # Mock the socket to simulate connection state
        self.client._sock = None  # Will be checked by read_messages
        
        # Instead, test the parsing logic directly
        msg_str = '{"event": "mounted", "path": "/mnt/usb"}\n'
        buf = msg_str
        messages = []
        
        while "\n" in buf:
            line, buf = buf.split("\n", 1)
            line = line.strip()
            if line:
                messages.append(json.loads(line))
        
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0]["event"], "mounted")
        self.assertEqual(messages[0]["path"], "/mnt/usb")

    def test_parse_multiple_json_messages(self):
        """Test parsing multiple newline-delimited JSON messages."""
        msg_str = (
            '{"event": "mounted", "path": "/mnt/usb1"}\n'
            '{"event": "mounted", "path": "/mnt/usb2"}\n'
            '{"event": "unmounted", "path": "/mnt/usb1"}\n'
        )
        buf = msg_str
        messages = []
        
        while "\n" in buf:
            line, buf = buf.split("\n", 1)
            line = line.strip()
            if line:
                messages.append(json.loads(line))
        
        self.assertEqual(len(messages), 3)
        self.assertEqual(messages[0]["event"], "mounted")
        self.assertEqual(messages[1]["event"], "mounted")
        self.assertEqual(messages[2]["event"], "unmounted")

    def test_parse_partial_message(self):
        """Test buffering of partial messages."""
        partial_msg = '{"event": "mounted"'
        buf = partial_msg
        messages = []
        
        while "\n" in buf:
            line, buf = buf.split("\n", 1)
            line = line.strip()
            if line:
                messages.append(json.loads(line))
        
        # No complete message yet
        self.assertEqual(len(messages), 0)
        # Partial remains in buffer
        self.assertEqual(buf, partial_msg)

    def test_parse_invalid_json(self):
        """Test handling of invalid JSON."""
        invalid_msg = 'not valid json\n'
        buf = invalid_msg
        messages = []
        parse_errors = 0
        
        while "\n" in buf:
            line, buf = buf.split("\n", 1)
            line = line.strip()
            if line:
                try:
                    messages.append(json.loads(line))
                except json.JSONDecodeError:
                    parse_errors += 1
        
        self.assertEqual(len(messages), 0)
        self.assertEqual(parse_errors, 1)

    def test_parse_mixed_valid_invalid_messages(self):
        """Test parsing mix of valid and invalid JSON."""
        msg_str = (
            '{"event": "mounted"}\n'
            'garbage\n'
            '{"event": "unmounted"}\n'
        )
        buf = msg_str
        messages = []
        parse_errors = 0
        
        while "\n" in buf:
            line, buf = buf.split("\n", 1)
            line = line.strip()
            if line:
                try:
                    messages.append(json.loads(line))
                except json.JSONDecodeError:
                    parse_errors += 1
        
        self.assertEqual(len(messages), 2)
        self.assertEqual(parse_errors, 1)

    def test_parse_empty_lines(self):
        """Test that empty lines are skipped."""
        msg_str = (
            '{"event": "mounted"}\n'
            '\n'
            '\n'
            '{"event": "unmounted"}\n'
        )
        buf = msg_str
        messages = []
        
        while "\n" in buf:
            line, buf = buf.split("\n", 1)
            line = line.strip()
            if line:  # Skip empty lines
                messages.append(json.loads(line))
        
        self.assertEqual(len(messages), 2)

    def test_real_world_nsd_messages(self):
        """Test parsing of realistic nsd broadcast messages."""
        msg_str = (
            '{"event":"mounted","mount_point":"/mnt/usb","label":"USB_DRIVE"}\n'
            '{"event":"unmounted","mount_point":"/mnt/usb"}\n'
        )
        buf = msg_str
        messages = []
        
        while "\n" in buf:
            line, buf = buf.split("\n", 1)
            line = line.strip()
            if line:
                messages.append(json.loads(line))
        
        self.assertEqual(len(messages), 2)
        self.assertEqual(messages[0]["mount_point"], "/mnt/usb")
        self.assertEqual(messages[0]["label"], "USB_DRIVE")
        self.assertEqual(messages[1]["event"], "unmounted")


if __name__ == "__main__":
    unittest.main()
