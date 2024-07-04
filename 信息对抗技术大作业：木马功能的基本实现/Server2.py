import socket
import threading
import os

def handle_client(client_socket, client_address):
    print(f"Client connected from {client_address}")
    try:
        # 接收文件名和文件大小
        data = client_socket.recv(1024).decode()
        if not data.startswith("UPLOAD:"):
            print("Invalid request format")
            return
        file_info = data.split(':')
        if len(file_info) != 2:
            print("Invalid request format")
            return
        file_name, file_size_str = file_info[1].strip(), ''
        if ',' in file_name:
            file_name, file_size_str = file_name.split(',')[0], file_name.split(',')[1]
        file_size = int(file_size_str)

        # 创建文件以写入数据
        with open(file_name, 'wb') as f:
            remaining_bytes = file_size
            while remaining_bytes > 0:
                data = client_socket.recv(4096)
                if not data:
                    print("Connection closed by client")
                    break
                f.write(data)
                remaining_bytes -= len(data)
        print(f"File {file_name} received successfully.")
    except Exception as e:
        print(f"Error handling client: {e}")
    finally:
        client_socket.close()

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('localhost', 23456))
    server.listen(5)
    print("Server started.")
    while True:
        client_socket, client_address = server.accept()
        client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
        client_thread.start()

if __name__ == "__main__":
    start_server()