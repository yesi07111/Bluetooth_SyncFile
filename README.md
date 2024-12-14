# 📁 Bluetooth Folder Synchronizer

## 🚀 Overview
This project is a Bluetooth-based folder synchronizer that allows two devices to share and manage a common directory. The interface is command-line based, simulating common Linux commands such as `ls`, `cd`, `mv`, `rm`, `cp`, `mkdir` and `rename`. Additionally, it includes `get` and `send` commands to copy files between the shared directories. Also includes `pwd` command that shows the current working directory.

## 🛠️ Features
- **ls**: List the contents of the current directory.
- **cd**: Change the current working directory.
- **get**: Copy a file from the shared directory to your local directory.
- **send**: Send a file from your local directory to the shared directory.
- **rm**: Remove a file or directory.
- **mv**: Move a file or directory.
- **rename**: Rename a file or directory.
- **cp**: Copy a file or directory.
- **mkdir**: Create a new directory or file if an extension is provided.
- **pwd**: Show the current working directory.

## 📦 Requirements
- **📱 Operating System**: Both devices must be paired via Bluetooth in the operating system.
- **📚 Libraries**: All libraries used are native and do not require installation.

## 📝 Usage
### 📱 Pairing Devices
1. **Pair Devices**: Ensure both devices are paired via Bluetooth in your operating system settings.
2. **Get MAC Addresses**:
   - **Linux**: Use the `hcitool` command to list paired devices.
     ```
     hcitool dev
     ```
   - **Windows**: Go to `Settings > Devices > Bluetooth & other devices` and note the MAC address of the paired device.
   - **macOS**: Go to `System Preferences > Bluetooth` and note the MAC address of the paired device.
3. **Copy your MAC address and the other device MAC address in** `main` **on** `bt_manager.py`:
```python
if __name__ == '__main__':
    s = BTFileSystem('my_MAC_address', 'other_MAC_address',  'path/to/shared/folder')
```
### 🏃 Running the Script
1. **Navigate to the Project Directory**:
   ```sh
   cd path/to/your/project
   ```

2. **Run the Script**:
   ```sh
   python bt_manager.py
   ```

### 📜 Commands
- **ls**: List the contents of the current directory.
  ```sh
  ls
  ```

- **cd**: Change the current working directory.
  ```sh
  cd /path/to/directory
  ```

- **get**: Copy a file from the shared directory to your local directory. Use `filename.ext` for the file.
  ```sh
  get filename.ext
  ```

- **send**: Send a file from your local directory to the shared directory. Use `filename.ext` for the file.
  ```sh
  send filename.ext
  ```

- **rm**: Remove a file or directory. Use `filename.ext` for files and `directory_name` for directories.
  ```sh
  rm filename.ext
  ```

- **mv**: Move a file or directory. Use `filename.ext` for files and `directory_name` for directories.
  ```sh
  mv filename.ext new_directory/
  ```

- **rename**: Rename a file or directory. Use `old_name.ext` for the old file and `new_name.ext` for the new file.
  ```sh
  rename old_name.ext new_name.ext
  ```

- **cp**: Copy a file or directory. Use `filename.ext` for files and `directory_name` for directories.
  ```sh
  cp filename.ext new_directory/
  ```

- **mkdir**: Create a new directory or file if an extension is provided.
  ```sh
  mkdir new_directory
  mkdir new_file.txt
  ```

- **pwd**: Show the current working directory.
  ```sh
  pwd
  ```

## 📝 Notes
- **File Size Limit**: There is no size limit for files to be copied or sent, but the process can be slow depending on the file size and Bluetooth transfer speed.
- **Current Working Directory**: The `cd` command changes the current working directory, and all other commands are relative to this directory.
