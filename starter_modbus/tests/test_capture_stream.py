import os
import socket
import threading
import unittest
from contextlib import closing
from unittest.mock import Mock, patch

from capture.stream_capture import stream_capture


class CaptureStreamTests(unittest.TestCase):
    def test_forwards_tcpdump_output_to_wireshark_connection(self):
        expected = b"pcap packet data"
        read_fd, write_fd = os.pipe()
        process = Mock()
        process.__enter__ = Mock(return_value=process)
        process.__exit__ = Mock(return_value=False)
        process.stdout = os.fdopen(read_fd, "rb")
        process.poll.return_value = 0
        process.returncode = 0

        def write_packet_data():
            with os.fdopen(write_fd, "wb") as stream:
                stream.write(expected)

        writer = threading.Thread(target=write_packet_data)
        writer.start()
        try:
            wireshark, relay = socket.socketpair()
            with closing(wireshark), closing(relay):
                wireshark.settimeout(2)
                with patch(
                    "capture.stream_capture.subprocess.Popen",
                    return_value=process,
                ) as popen:
                    stream_capture(relay, "eth0", "tcp port 502")

                received = bytearray()
                while len(received) < len(expected):
                    received.extend(wireshark.recv(len(expected) - len(received)))

            popen.assert_called_once()
            self.assertEqual(bytes(received), expected)
        finally:
            writer.join(timeout=2)
            process.stdout.close()


if __name__ == "__main__":
    unittest.main()
