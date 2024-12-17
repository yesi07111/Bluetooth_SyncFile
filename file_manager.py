import os
import base64
from typing import Iterable

FILE_CHUNK_SIZE = 512

class FileManager:
    def __init__(self, root: str) -> None:
        """
        Initializes the FileManager with the root directory.
        
        Parameters:
        -----------
        root : str
            The root directory to be managed.
        """
        self.root = self.cwd = root

    def execute(self, command: str, *args) -> Iterable[str]:
        """
        Executes the given command with the provided arguments.
        
        Parameters:
        -----------
        command : str
            The command to execute.
        *args : tuple
            Arguments for the command.
        
        Returns:
        --------
        Iterable[str]
            An iterable of response messages.
        """
        func = getattr(self, command)

        try:
            response = func(*args)
            if isinstance(response, str):
                return [response, ]
            return response
        except Exception as e:
            print(f'An error occurred: {e}')

    def ls(self) -> str:
        """
        Lists the contents of the current directory.
        
        Returns:
        --------
        str
            A message with the list of directory contents.
        """
        dirs = os.listdir(self.cwd)
        all_dirs = '\n'.join(dirs)
        return f'message::{all_dirs}'

    def cd(self, dir: str) -> str:
        """
        Changes the current working directory.
        
        Parameters:
        -----------
        dir : str
            The directory to change to.
        
        Returns:
        --------
        str
            A message indicating the success or failure of the operation.
        """
        new_path = str(os.path.abspath(os.path.join(self.cwd, dir))).replace('\\', '/')

        if os.path.isdir(new_path) and new_path.startswith(self.root):
            self.cwd = new_path
            new_path = new_path.replace(self.root, '//')
            return f'message::Changed directory to {self.cwd}'
        else:
            return f'error::{dir} is not a valid directory'

    def get(self, filename: str) -> Iterable[str]:
        """
        Copies a file from the shared directory to the local directory.
        
        Parameters:
        -----------
        filename : str
            The name of the file to copy.
        
        Returns:
        --------
        Iterable[str]
            An iterable of file chunks or an error message.
        """
        filepath = os.path.abspath(os.path.join(self.cwd, filename)).replace('\\', '/')

        if os.path.isfile(filepath) and filepath.startswith(self.root):
            with open(filepath, 'rb') as file:
                # Read the file in chunks of 1 KB
                file_data = file.read()
                chunks = [base64.b64encode(file_data[i:i + FILE_CHUNK_SIZE]).decode()  # Chunks of 1KB
                        for i in range(0, len(file_data), FILE_CHUNK_SIZE)]

                # Send each chunk with an index
                total_chunks = len(chunks)
                for idx, chunk in enumerate(chunks):
                    yield f'file::{filename}::{total_chunks}::{idx+1}::{chunk}'

        else:
            return f'error::{filename} not found.'

    def send(self, filename: str) -> Iterable[str]:
        """
        Sends a file from the local directory to the shared directory.
        
        Parameters:
        -----------
        filename : str
            The name of the file to send.
        
        Returns:
        --------
        Iterable[str]
            An iterable of file chunks or an error message.
        """
        return self.get(filename)

    def pwd(self) -> str:
        """
        Shows the current working directory.
        
        Returns:
        --------
        str
            A message with the current working directory.
        """
        return f'message::Current directory: {self.cwd}'

    def rm(self, target: str) -> str:
        """
        Removes a file or directory.
        
        Parameters:
        -----------
        target : str
            The file or directory to remove.
        
        Returns:
        --------
        str
            A message indicating the success or failure of the operation.
        """
        path = os.path.abspath(os.path.join(self.cwd, target)).replace('\\', '/')

        if path.startswith(self.root):
            if os.path.isfile(path):
                os.remove(path)
                return f'message::File {target} removed successfully.'
            elif os.path.isdir(path):
                try:
                    import shutil
                    shutil.rmtree(path)
                    return f'message::Directory {target} removed successfully.'
                except Exception as e:
                    return f'error::Unable to remove directory {target}. {str(e)}'
            else:
                return f'error::{target} does not exist.'
        else:
            return f'error::Invalid path {target}.'

    def mkdir(self, name: str) -> str:
        """
        Creates a new directory or file if an extension is provided.
        
        Parameters:
        -----------
        name : str
            The name of the directory or file to create.
        
        Returns:
        --------
        str
            A message indicating the success or failure of the operation.
        """
        path = os.path.abspath(os.path.join(self.cwd, name)).replace('\\', '/')

        if '.' in os.path.basename(name):  # Has extension, create file
            if path.startswith(self.root):
                try:
                    with open(path, 'w') as file:
                        pass
                    return f'message::File {name} created successfully.'
                except Exception as e:
                    return f'error::Unable to create file {name}. {str(e)}'
            else:
                return f'error::Invalid path {name}.'
        else:  # No extension, create directory
            if path.startswith(self.root):
                try:
                    os.makedirs(path, exist_ok=True)
                    return f'message::Directory {name} created successfully.'
                except Exception as e:
                    return f'error::Unable to create directory {name}. {str(e)}'
            else:
                return f'error::Invalid directory path {name}.'

    def mv(self, src: str, dest: str) -> str:
        """
        Moves a file or directory.
        
        Parameters:
        -----------
        src : str
            The source file or directory to move.
        dest : str
            The destination directory.
        
        Returns:
        --------
        str
            A message indicating the success or failure of the operation.
        """
        # Ensure src is an absolute path
        if not os.path.isabs(src):
            src = os.path.abspath(os.path.join(self.cwd, src)).replace('\\', '/')

        # Determine the destination path
        if dest != self.cwd:
            dest_path = os.path.abspath(os.path.join(self.cwd, dest, os.path.basename(src))).replace('\\', '/')
        else:
            dest_path = os.path.abspath(os.path.join(dest, os.path.basename(src))).replace('\\', '/')

        # Check that both paths start with self.root
        if src.startswith(self.root) and dest_path.startswith(self.root):
            try:
                os.rename(src, dest_path)
                return f'message::{src} moved to {dest} successfully.'
            except Exception as e:
                return f'error::Unable to move {src} to {dest}. {str(e)}'
        else:
            return f'error::Invalid source or destination path.'

    def rename(self, old_name: str, new_name: str) -> str:
        """
        Renames a file or directory.
        
        Parameters:
        -----------
        old_name : str
            The current name of the file or directory.
        new_name : str
            The new name for the file or directory.
        
        Returns:
        --------
        str
            A message indicating the success or failure of the operation.
        """
        old_path = os.path.abspath(os.path.join(self.cwd, old_name)).replace('\\', '/')
        if '.' in os.path.basename(old_name):
            new_name_with_ext = new_name if '.' in new_name else f"{new_name}{os.path.splitext(old_name)[1]}"
        else:
            new_name_with_ext = new_name

        new_path = os.path.abspath(os.path.join(self.cwd, new_name_with_ext)).replace('\\', '/')

        if old_path.startswith(self.root) and new_path.startswith(self.root):
            try:
                os.rename(old_path, new_path)
                return f'message::{old_name} renamed to {new_name_with_ext} successfully.'
            except Exception as e:
                return f'error::Unable to rename {old_name} to {new_name_with_ext}. {str(e)}'
        else:
            return f'error::Invalid source or destination path.'

    def cp(self, src: str, dest: str) -> str:
        """
        Copies a file or directory.
        
        Parameters:
        -----------
        src : str
            The source file or directory to copy.
        dest : str
            The destination directory.
        
        Returns:
        --------
        str
            A message indicating the success or failure of the operation.
        """
        print(f"Copy {src} to {dest}")

        # Ensure src is an absolute path
        if not os.path.isabs(src):
            src = os.path.abspath(os.path.join(self.cwd, src)).replace('\\', '/')

        # Determine the destination path
        if dest != self.cwd:
            dest_path = os.path.abspath(os.path.join(self.cwd, dest)).replace('\\', '/')
        else:
            dest_path = os.path.abspath(os.path.join(dest, os.path.basename(src))).replace('\\', '/')

        print(f"From {src} to {dest_path}")

        # Check that both paths start with self.root
        if src.startswith(self.root) and dest_path.startswith(self.root):
            try:
                if os.path.isfile(src):
                    # If it's a file, copy directly
                    import shutil
                    shutil.copy2(src, dest_path)
                elif os.path.isdir(src):
                    # If it's a directory, copy with all its contents
                    import shutil
                    shutil.copytree(src, dest_path, dirs_exist_ok=True)
                return f'message::{src} copied to {dest} successfully.'
            except Exception as e:
                return f'error::Unable to copy {src} to {dest}. {str(e)}'
        else:
            return f'error::Invalid source or destination path.'