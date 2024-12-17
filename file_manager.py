import os
import base64
from typing import Iterable


FILE_CHUNK_SIZE = 512

class FileManager:
    def __init__(self, root: str) -> None:
        self.root = self.cwd = root
    
    def execute(self, command, *args) -> Iterable[str]:
        func = getattr(self, command)

        try:
            response = func(*args)
            if isinstance(response, str):
                return [response,]
            return response
        except Exception as e:
            print(f'An error ocured: {e}')
    
    def ls(self):
        dirs = os.listdir(self.cwd)
        all_dirs = '\n'.join(dirs)
        return f'message::{all_dirs}'

    def cd(self, dir):
        new_path = str(os.path.abspath(os.path.join(self.cwd, dir))).replace('\\', '/')
        
        if os.path.isdir(new_path) and new_path.startswith(self.root):
            self.cwd = new_path
            new_path = new_path.replace(self.root, '//')
            return f'message::Changed directory to {self.cwd}'
        else:
            return f'error::{dir} is not a valid directory'
    
    def get(self, filename):
        filepath = os.path.abspath(os.path.join(self.cwd, filename)).replace('\\', '/')

        if os.path.isfile(filepath) and filepath.startswith(self.root):
            with open(filepath, 'rb') as file:
                # Leer el archivo en bloques de 1 KB
                file_data = file.read()
                chunks = [base64.b64encode(file_data[i:i + FILE_CHUNK_SIZE]).decode()  # Fragmentos de 1KB
                        for i in range(0, len(file_data), FILE_CHUNK_SIZE)]
                
                # Enviar cada fragmento con un índice
                total_chunks = len(chunks)
                for idx, chunk in enumerate(chunks):
                    yield f'file::{filename}::{total_chunks}::{idx+1}::{chunk}'

        else:
            return f'error::{filename} not found.'

    def send(self, filename):
        return self.get(filename)
    
    def pwd(self):
        return f'message::{self.cwd}'

    def rm(self, target):
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


    def mkdir(self, name):
        path = os.path.abspath(os.path.join(self.cwd, name)).replace('\\', '/')

        if '.' in os.path.basename(name):  # Tiene extensión, crear archivo
            if path.startswith(self.root):
                try:
                    with open(path, 'w') as file:
                        pass
                    return f'message::File {name} created successfully.'
                except Exception as e:
                    return f'error::Unable to create file {name}. {str(e)}'
            else:
                return f'error::Invalid path {name}.'
        else:  # No tiene extensión, crear carpeta
            if path.startswith(self.root):
                try:
                    os.makedirs(path, exist_ok=True)
                    return f'message::Directory {name} created successfully.'
                except Exception as e:
                    return f'error::Unable to create directory {name}. {str(e)}'
            else:
                return f'error::Invalid directory path {name}.'

    def mv(self, src, dest):
        # Asegurarse de que src sea una ruta absoluta
        if not os.path.isabs(src):
            src = os.path.abspath(os.path.join(self.cwd, src)).replace('\\', '/')

        # Determinar la ruta de destino
        if dest != self.cwd:
            dest_path = os.path.abspath(os.path.join(self.cwd, dest, os.path.basename(src))).replace('\\', '/')
        else:
            dest_path = os.path.abspath(os.path.join(dest, os.path.basename(src))).replace('\\', '/')

        # Comprobar que ambas rutas comiencen con self.root
        if src.startswith(self.root) and dest_path.startswith(self.root):
            try:
                os.rename(src, dest_path)
                return f'message::{src} moved to {dest} successfully.'
            except Exception as e:
                return f'error::Unable to move {src} to {dest}. {str(e)}'
        else:
            return f'error::Invalid source or destination path.'
        
    def rename(self, old_name, new_name):
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
    
    def cp(self, src, dest):
        print(f"Copy {src} to {dest}")

        # Asegurarse de que src sea una ruta absoluta
        if not os.path.isabs(src):
            src = os.path.abspath(os.path.join(self.cwd, src)).replace('\\', '/')

        # Determinar la ruta de destino
        if dest != self.cwd:
            dest_path = os.path.abspath(os.path.join(self.cwd, dest)).replace('\\', '/')
        else:
            dest_path = os.path.abspath(os.path.join(dest, os.path.basename(src))).replace('\\', '/')

        print(f"From {src} to {dest_path}")

        # Comprobar que ambas rutas comiencen con self.root
        if src.startswith(self.root) and dest_path.startswith(self.root):
            try:
                if os.path.isfile(src):
                    # Si es un archivo, copiar directamente
                    import shutil
                    shutil.copy2(src, dest_path)
                elif os.path.isdir(src):
                    # Si es un directorio, copiar con todo su contenido
                    import shutil
                    shutil.copytree(src, dest_path, dirs_exist_ok=True)
                return f'message::{src} copied to {dest} successfully.'
            except Exception as e:
                return f'error::Unable to copy {src} to {dest}. {str(e)}'
        else:
            return f'error::Invalid source or destination path.'
