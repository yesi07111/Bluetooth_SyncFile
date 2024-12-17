import socket
import threading
import os
import base64
import zipfile
from file_manager import FileManager

class BTFileSystem:
    def __init__(self, local_addr: str, peer_addr: str, root_directory: str='~', port: int=30, is_visual: bool=False) -> None:
        """
        Initializes the BTFileSystem with the local and peer Bluetooth addresses, root directory, and port.        
        :param local_addr: The MAC address of the local Bluetooth device.        :param peer_addr: The MAC address of the peer Bluetooth device.
        :param root_directory: The root directory to be synchronized. Defaults to '~'.        :param port: The port number for Bluetooth communication. Defaults to 30.
        :param is_visual: A flag to indicate if visual feedback is needed. Defaults to False.        """
        self.peer_addr = peer_addr
        self.local_addr = local_addr
        self.port = port

        self.server_socket = None
        self.refresh_server()

        self.server_thread = threading.Thread(target=self.accept_connections)
        self.server_thread.daemon = True
        self.server_thread.start()

        self.file_manager = FileManager(root_directory)
        self.root_directory = root_directory
    
    def refresh_server(self):
        """
        Refreshes the server socket by closing the existing one and creating a new one.        """
        
        # Close the existing socket if it exists
        if isinstance(self.server_socket, socket.socket):
            try:
                self.server_socket.close()  # Properly close the socket
            except OSError as e:
                print(f"Error closing socket: {e}")

        # Create a new server socket
        self.server_socket = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)

        try:
            # Bind the new socket to the specified address and port
            self.server_socket.bind((self.local_addr, self.port))
            self.server_socket.listen(1)  # Start listening for incoming connections
        except socket.error as e:
            self.server_socket = None  # Ensure the server_socket attribute is reset on error
            print(f"Error binding socket: {e}")

    def accept_connections(self):
        """
        Accepts incoming connections and processes commands received from the peer.        """
        
        while True:
            try:
                client_sock, _ = self.server_socket.accept()
                data = client_sock.recv(1 << 20) # Receive data (up to 1 MB)
                data = data.decode()

                command = self.parse_command(data)

                if command:
                    command, *args = command
                    response = self.file_manager.execute(command, *args)
                    
                    for msg in response:
                        self.send_message(msg)

                client_sock.close()
            except socket.error as e:
                print(f"Socket error: {e}")
                self.refresh_server()
            except Exception as e:
                print(f"Unexpected error: {e}")
                self.refresh_server()

    def send_message(self, message: str, is_command: bool=False):
        """        Sends a message to the peer device.
                :param message: The message to be sent.
        :param is_command: A flag to indicate if the message is a command. Defaults to False.        """
        
        with socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM) as sock:
            try: 
                if is_command:
                    message = f'command::{message}'
                
                if message.startswith('command::send'):
                    command, *args = self.parse_command(message)
                    message = self.file_manager.execute(command, *args)
                
                if not isinstance(message, str):
                    for msg in message:
                        self.send_message(msg)
                    return

                sock.connect((self.peer_addr, self.port))
                sock.send(message.encode())
            except socket.error as e:
                print(f"Error sending message: {e}")

    def parse_command(self, command: str):
        """
        Parses the received command and handles file and message data.        
        :param command: The command string received from the peer.        :return: The parsed command and its arguments, or None if the command is invalid.
        """
        
        if command.startswith('command::'):
            command = command[9:].split()
            command, *args = command
            return command, *args

        if command.startswith('error::'):
            pass

        if command.startswith('file::'):
            try:
                _, filename, total_chunks, chunk_index, content = command.split('::')

                total_chunks = int(total_chunks)
                chunk_index = int(chunk_index)

                print(total_chunks, chunk_index)
                
                if not hasattr(self, 'file_chunks'):
                    self.file_chunks = {}

                if filename not in self.file_chunks:
                    self.file_chunks[filename] = {}

                self.file_chunks[filename][chunk_index] = content
                
                if len(self.file_chunks[filename]) == total_chunks:
                    try:
                        content = [base64.b64decode(self.file_chunks[filename][i] + "=" * (4 - len(self.file_chunks[filename][i]) % 4)) for i in range(1, total_chunks + 1)]
                        filepath = os.path.join(self.file_manager.cwd, filename)
                        
                        with open(filepath, 'wb') as file:
                            for content_bytes in content:
                                file.write(content_bytes)
                        
                        # Optionally, extract the file if it's a zip
                        if filename.endswith('.zip'):
                            with zipfile.ZipFile(filepath, 'r') as zip_ref:
                                zip_ref.extractall(self.file_manager.cwd)
                            os.remove(filepath)  # Clean up the zip file after extraction

                    except Exception as e:
                        print(f"Error decoding file: {e}")

                    del self.file_chunks[filename]

            except ValueError as e:
                print(f"Error: Invalid file fragment received: {e}")

        if command.startswith('message::'):
            print(command[9:])

if __name__ == '__main__':
    # Example usage: Initialize the BTFileSystem with local and peer MAC addresses, root directory, and port    
    # Main loop to continuously accept user input and send commands
    
    s = BTFileSystem("34:6F:24:8F:31:0A", "F4:7B:09:5C:D2:93",  'E:/ESCUELA/Ciber', 27)

    while True:
        msg = input()
        s.send_message(msg, True)