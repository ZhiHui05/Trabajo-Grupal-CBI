from __future__ import annotations

import os
import socket
import subprocess


def stream_capture(
    connection: socket.socket, interface: str, capture_filter: str
) -> None:
    command = [
        "tcpdump",
        "-n",
        "-i",
        interface,
        "-s",
        "0",
        "-U",
        "-w",
        "-",
        capture_filter,
    ]

    with subprocess.Popen(command, stdout=subprocess.PIPE) as capture:
        if capture.stdout is None:
            raise RuntimeError("tcpdump did not provide a packet stream")

        disconnected = False
        try:
            while packet_data := os.read(capture.stdout.fileno(), 65536):
                connection.sendall(packet_data)
        except ConnectionError:
            disconnected = True
        finally:
            if capture.poll() is None:
                capture.terminate()
            try:
                capture.wait(timeout=5)
            except subprocess.TimeoutExpired:
                capture.kill()
                capture.wait()

        if not disconnected and capture.returncode:
            raise subprocess.CalledProcessError(capture.returncode, command)


def main() -> None:
    host = os.getenv("STREAM_HOST", "0.0.0.0")
    port = int(os.getenv("STREAM_PORT", "15002"))
    interface = os.getenv("IFACE", "eth0")
    capture_filter = os.getenv("FILTER", "tcp port 502")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listener.bind((host, port))
        listener.listen(1)
        print(
            f"[stream] Escuchando en {host}:{port}; "
            f"interfaz={interface}; filtro={capture_filter}",
            flush=True,
        )

        try:
            while True:
                connection, address = listener.accept()
                print(f"[stream] Cliente Wireshark conectado: {address}", flush=True)
                with connection:
                    connection.setsockopt(
                        socket.IPPROTO_TCP, socket.TCP_NODELAY, 1
                    )
                    stream_capture(connection, interface, capture_filter)
                print("[stream] Cliente desconectado", flush=True)
        except KeyboardInterrupt:
            print("[stream] Captura detenida", flush=True)


if __name__ == "__main__":
    main()
