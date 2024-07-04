import socket
import threading
import os
import time
from PIL import ImageGrab
import io

shutdown_scheduled = False
shutdown_thread = None


def shutdown_computer():
    global shutdown_scheduled
    time.sleep(5)  # 假设有一个5秒的延迟来模拟关机前的准备时间
    if shutdown_scheduled:
        print("Shutting down the computer...")
        # 在Windows系统上执行关机命令
        os.system('shutdown -s -t 60')  # 60s延迟，再次之前可随时取消


def cancel_shutdown():
    global shutdown_scheduled, shutdown_thread
    shutdown_scheduled = False
    if shutdown_thread and shutdown_thread.is_alive():
        print("Attempting to cancel shutdown...")
        os.system('shutdown -a')  # 取消关机命令

def delete_file(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"File {file_path} deleted.")
    else:
        print(f"File {file_path} does not exist.")


def save_file(data, file_name="myFile.txt"):
    with open(file_name, 'wb') as f:
        f.write(data)
    print(f"File {file_name} saved.")


def send_file(conn, file_path):
    if os.path.exists(file_path):
        file_size = os.path.getsize(file_path)
        conn.sendall(str(file_size).encode())  # 发送文件大小
        conn.recv(1024)  # 等待客户端确认
        with open(file_path, 'rb') as f:
            while True:
                data = f.read(4096)
                if not data:
                    break
                conn.sendall(data)
        print(f"File {file_path} sent.")
    else:
        print(f"File {file_path} does not exist.")

def save_screenshot(conn, file_name="screenshot.png"):
    with open(file_name, 'wb') as f:
        while True:
            data = conn.recv(4096)
            if not data:
                break
            f.write(data)
    print(f"Screenshot {file_name} saved.")


def handle_client(conn):
    global shutdown_scheduled, shutdown_thread
    while True:
        try:
            data = conn.recv(1024).decode()
            if not data:
                break

            if data.startswith("DELETE:"):
                file_path = data[len("DELETE:"):].strip()
                delete_file(file_path)  # 假设这个函数用于删除文件
            elif data.startswith("UPLOAD:"):
                file_size_data = conn.recv(16).decode()
                file_size = int(file_size_data)
                conn.sendall(b'READY')  # 发送确认给客户端，表示准备好接收文件内容
                file_data = b''
                remaining_bytes = file_size
                while remaining_bytes > 0:
                    packet = conn.recv(4096)
                    file_data += packet
                    remaining_bytes -= len(packet)
                save_file(file_data)  # 保存文件内容到myFile.txt
                print("Current working directory:", os.getcwd())

            elif data.startswith("DOWNLOAD:"):
                file_path = data[len("DOWNLOAD:"):].strip()
                send_file(conn, file_path)  # 发送文件内容给客户端
            elif data.startswith("ECHO:"):
                echo_message = data[len("ECHO:"):].strip()
                print(echo_message)  # 输出字符串
            elif data == "LIST_C_DRIVE":
                # 遍历C盘目录并发送文件列表
                c_drive = "C:\\"  # Windows系统的C盘路径
                for root, dirs, files in os.walk(c_drive):
                    for file in files:
                        file_path = os.path.join(root, file)
                        # 这里可以根据需要过滤掉系统文件或隐藏文件
                        # 发送文件路径给客户端
                        conn.sendall(file_path.encode() + b'\n')
                conn.sendall(b'END_OF_LIST\n')  # 发送结束标记
            elif data == "SHUTDOWN:":
                if not shutdown_scheduled:
                    shutdown_scheduled = True
                    shutdown_thread = threading.Thread(target=shutdown_computer)
                    shutdown_thread.start()
                    print("Shutdown scheduled.")
            elif data == "CANCEL_SHUTDOWN:":
                cancel_shutdown()
                print("Shutdown canceled.")
            elif data.startswith("SCREENSHOT:"):
                    # 接收文件大小（字符串形式），直到遇到换行符
                    file_size_data = b''
                    while True:
                        size_byte = conn.recv(1)
                        if not size_byte or size_byte == b'\n':
                            break
                        file_size_data += size_byte
                    file_size = int(file_size_data.decode())

                    # 接收截图数据并保存为文件
                    with open("screenshot.png", 'wb') as f:
                        received_bytes = 0
                        while received_bytes < file_size:
                            data = conn.recv(4096)
                            f.write(data)
                            received_bytes += len(data)
                    print("Screenshot saved.")
                    print("Current working directory:", os.getcwd())#文件保存位置
            else:
                print(f"Client Commend: {data}")
        except ConnectionResetError:
            break
    conn.close()

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('localhost', 12345))
    server.listen(5)
    print("Server started.")
    while True:
        client, addr = server.accept()
        print(f"Client connected from {addr}.")
        client_thread = threading.Thread(target=handle_client, args=(client,))
        client_thread.start()


if __name__ == "__main__":
    start_server()