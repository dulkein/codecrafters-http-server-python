import socket
import threading


def handle_client(client_socket):
    with client_socket:
        request = client_socket.recv(4096)
        request_text = request.decode("utf-8", errors="replace")
        request_line, _, remainder = request_text.partition("\r\n")
        parts = request_line.split(" ")

        if len(parts) < 2:
            response = b"HTTP/1.1 400 Bad Request\r\n\r\n"
        elif parts[1] == "/":
            response = b"HTTP/1.1 200 OK\r\n\r\n"
        elif parts[1].startswith("/echo/"):
            value = parts[1][6:]
            body = value.encode("utf-8")
            response = (
                b"HTTP/1.1 200 OK\r\n"
                b"Content-Type: text/plain\r\n"
                + f"Content-Length: {len(body)}\r\n\r\n".encode("utf-8")
                + body
            )
        elif parts[1] == "/user-agent":
            headers = remainder.split("\r\n")
            user_agent = ""
            for header in headers:
                if not header:
                    break
                name, _, value = header.partition(":")
                if name.strip().lower() == "user-agent":
                    user_agent = value.strip()
                    break

            body = user_agent.encode("utf-8")
            response = (
                b"HTTP/1.1 200 OK\r\n"
                b"Content-Type: text/plain\r\n"
                + f"Content-Length: {len(body)}\r\n\r\n".encode("utf-8")
                + body
            )
        else:
            response = b"HTTP/1.1 404 Not Found\r\n\r\n"

        client_socket.sendall(response)


def main():
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)

    while True:
        client_socket, _ = server_socket.accept()
        thread = threading.Thread(target=handle_client, args=(client_socket,))
        thread.daemon = True
        thread.start()


if __name__ == "__main__":
    main()
