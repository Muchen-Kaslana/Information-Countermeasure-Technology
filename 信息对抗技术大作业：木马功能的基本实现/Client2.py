import socket
import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import os


class ClientGUI:
    def __init__(self, master):
        self.master = master
        master.title("Client GUI")
        self.client_socket = None

        self.upload_button = tk.Button(master, text="Upload File to Server", command=self.upload_file_to_server)
        self.upload_button.pack()
        self.connect_to_server()

    def connect_to_server(self):
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect(('localhost', 23456))
            print("Connected to server.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def upload_file_to_server(self):
        if not self.client_socket:
            messagebox.showerror("Error", "Not connected to server.")
            return

        file_path = filedialog.askopenfilename()
        if not file_path:
            return

        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)

        self.client_socket.sendall(f"UPLOAD:{file_name},{file_size}".encode())

        threading.Thread(target=self._upload_file, args=(file_path,)).start()

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


root = tk.Tk()
client_gui = ClientGUI(root)
root.mainloop()