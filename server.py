import socket
import os
import mimetypes
import threading


DIR = "website"


def handle_request(connection, address):
    try:
        request = connection.recv(1024).decode()
        print(f"[NEW REQUEST] от {address}: {request}")

        try:
            method, target, protocol = request.splitlines()[0].split()
            path = target.replace("/", "")
            if not path:
                path = "index.html"
        except Exception as e:
            print(f"Ошибка: {e}")
            send_error(connection, 400, "Bad Request")
            return

        file_path = os.path.join(DIR, path)

        if not os.path.exists(file_path):
            send_error(connection, 404, "Not Found")
            return

        with open(file_path, "rb") as f:
            content = f.read()

        content_type = mimetypes.guess_type(file_path)[0] or "application/octet-stream"

        response = f"""
            HTTP/1.1 200 OK\r\n
            Content-Type: {content_type}\r\n
            Content-Length: {len(content)}\r\n
            Connection: close\r\n\r\n
        """
        connection.send(response.encode() + content)

    except Exception as e:
        print(f"Ошибка: {e}")
        send_error(connection, 500, "Internal Server Error")
    finally:
        connection.close()


def send_error(connection, code, message):
    response = f"""
        HTTP/1.1 {code} {message}\r\n
        Content-Type: text/plain\r\n
        Connection: close\r\n\r\n
        {message}
    """
    connection.send(response.encode())


if __name__ == "__main__":
    if not os.path.exists(DIR):
        os.makedirs(DIR)
        
    with open(os.path.join(DIR, "index.html"), "w", encoding='utf-8') as f:
        f.write("<h1>Test</h1>")

    HOST = '127.0.0.1'
    PORT = 8080

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"Сервер работает на {HOST}:{PORT}")
        while True:
            connection, address = s.accept()
            client_thread = threading.Thread(target=handle_request, args=(connection, address))
            client_thread.start()
