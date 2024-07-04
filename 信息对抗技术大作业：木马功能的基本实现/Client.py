import socket
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
from PIL import ImageGrab
import io
import os


class ClientGUI:
    def __init__(self, master):
        self.master = master
        master.title("Client GUI")

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect(('localhost', 12345))

        # GUI components

        self.echo_button = tk.Button(master, text="Echo Message to Server", command=self.send_echo_command)
        self.echo_button.pack()

        self.send_screenshot_button = tk.Button(master, text="Send Screenshot", command=self.send_screenshot)
        self.send_screenshot_button.pack()

        self.shutdown_button = tk.Button(master, text="Schedule Shutdown", command=self.send_shutdown_command)
        self.shutdown_button.pack()

        self.cancel_shutdown_button = tk.Button(master, text="Cancel Shutdown",
                                                command=self.send_cancel_shutdown_command)
        self.cancel_shutdown_button.pack()

        self.list_c_drive_button = tk.Button(master, text="List C Drive on Server", command=self.list_c_drive_on_server)
        self.list_c_drive_button.pack()


        self.delete_button = tk.Button(master, text="Delete File on Server", command=self.delete_file_on_server)
        self.delete_button.pack()

        self.upload_button = tk.Button(master, text="Upload File to Server", command=self.upload_file_to_server)
        self.upload_button.pack()

        self.download_button = tk.Button(master, text="Download File from Server",
                                         command=self.download_file_from_server)

        self.download_button.pack()

        self.text_widget = tk.Text(master, height=20, width=80)  # 可以根据需要调整高度和宽度
        self.text_widget.pack()



    def send_shutdown_command(self):
        self.client_socket.sendall("SHUTDOWN:".encode())
        messagebox.showinfo("Command Sent", "Shutdown has been scheduled.")

    def send_cancel_shutdown_command(self):
        self.client_socket.sendall("CANCEL_SHUTDOWN:".encode())
        messagebox.showinfo("Command Sent", "Shutdown has been cancelled.")
    def send_command(self):
        command = self.entry.get()
        if command:
            self.client_socket.sendall(command.encode())
            self.entry.delete(0, tk.END)

    def delete_file_on_server(self):
        file_path = simpledialog.askstring("Delete File",
                                           "Enter the file path on the server (e.g., C:\\path\\to\\file.txt):")
        if file_path:
            self.client_socket.sendall(f"DELETE:{file_path}".encode())

    def upload_file_to_server(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            try:
                file_size = os.path.getsize(file_path)
                self.client_socket.sendall(f"UPLOAD:{file_size}".encode())
                self.client_socket.recv(1024)  # 等待服务端确认

                # 使用线程来避免阻塞GUI
                threading.Thread(target=self._upload_file, args=(file_path,)).start()

                messagebox.showinfo("File Upload Started", "File upload has been started.")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def _upload_file(self, file_path):
        try:
            with open(file_path, 'rb') as f:
                while True:
                    data = f.read(4096)
                    if not data:
                        break
                    self.client_socket.sendall(data)
            messagebox.showinfo("File Uploaded", "File uploaded successfully.")
        except Exception as e:
            messagebox.showerror("Upload Error", str(e))

    def download_file_from_server(self):
        file_path = simpledialog.askstring("Download File",
                                           "Enter the file path on the server (e.g., C:\\path\\to\\file.txt):")
        if file_path:
            self.client_socket.sendall(f"DOWNLOAD:{file_path}".encode())
            file_size_data = self.client_socket.recv(16).decode()
            file_size = int(file_size_data)
            self.client_socket.sendall(b'READY')  # Send ready to server
            file_data = b''
            remaining_bytes = file_size
            while remaining_bytes > 0:
                data = self.client_socket.recv(4096)
                file_data += data
                remaining_bytes -= len(data)
            save_path = filedialog.asksaveasfilename(defaultextension=".bin", filetypes=[("Binary files", "*.bin")])
            if save_path:
                with open(save_path, 'wb') as f:
                    f.write(file_data)
                messagebox.showinfo("File Downloaded", "File downloaded successfully.")

    def send_screenshot(self):
        screenshot = ImageGrab.grab()
        output = io.BytesIO()
        screenshot.save(output, format='PNG')
        screenshot_data = output.getvalue()

        try:
            # 发送"SCREENSHOT:"通知服务端
            self.client_socket.sendall("SCREENSHOT:".encode())
            # 发送文件大小（字符串形式），后面跟着换行符
            self.client_socket.sendall(str(len(screenshot_data)).encode() + b'\n')
            # 发送截图数据
            self.client_socket.sendall(screenshot_data)
            messagebox.showinfo("Screenshot Sent", "Screenshot has been sent successfully.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def send_echo_command(self):
        echo_message = simpledialog.askstring("Echo Message", "Enter a message to echo on the server:")
        if echo_message:
            self.client_socket.sendall(f"ECHO:{echo_message}".encode())

    def list_c_drive_on_server(self):
            self.client_socket.sendall("LIST_C_DRIVE".encode())
            self.text_widget.delete('1.0', tk.END)  # 清空之前的文本

            while True:
                data = self.client_socket.recv(4096).decode().rstrip('\n')
                if data == 'END_OF_LIST':
                    break
                self.text_widget.insert(tk.END, data + '\n')  # 将文件路径插入到Text widget中

    def close_connection(self):
        self.client_socket.close()
        self.master.destroy()


root = tk.Tk()
client_gui = ClientGUI(root)
root.protocol("WM_DELETE_WINDOW", client_gui.close_connection)  # Close connection on window close
root.mainloop()