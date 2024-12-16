# Command and Control (C2) Server: A Python Project for Penetration Testing

## Disclaimer:
__This project is intended solely for educational and ethical purposes. The C2 server is designed to showcase Python programming skills and to aid in understanding the concepts of penetration testing and red team operations. The development of this project was inspired by concepts learned in a Udemy course, Design Command and Control using Python 3. Unauthorized use of this software on systems without explicit permission is strictly prohibited and may violate laws and regulations. This tool is provided "as is," without warranty of any kind, either expressed or implied. The author assumes no liability or responsibility for any misuse or damage caused by this software. Always use this tool in compliance with applicable laws and only in controlled environments or with explicit authorization.__
## Demonstration
Some domenstrations of the C2 server function with pictures:

[Demonstration.md](https://github.com/H-9527/Command-and-Control-Server/blob/main/Demonstration.md)
## How to use
1. Download server.py, setting.py, encryption.py.
2. Download linux_client.py or win_client.py according to your OS.
3. setup server ip adn listening port in the seting.py.
4. run the server.py.
5. run the client on your target machine.
## Key Features of the C2 Server
1. **Session Management**:
    - Tracks and manages multiple client sessions.
    - Allows switching between active sessions seamlessly.
2. **Command Execution**:
    - Execute shell commands on connected clients.
    - Supports background execution of commands on the client side.
3. **File Management**:
    - Securely upload and download files to/from the server.
    - Encrypt and zip files for secure transfer.
    - Decrypt and unzip files on the server or client.
4. **Remote Control Capabilities**:
    - Capture client screenshots.
    - Retrieve client clipboard content.
    - Simulate keyboard input on the client.
5. **Interactive Features**:
    - Display images or play sounds on the client system.
    - Manipulate client displays (e.g., flip screen, rotate screen).
6. **Client Monitoring**:
    - Keylogger functionality to capture keystrokes.
    - Adjustable client reconnection delay.
7. **Server Utilities**:
    - Directory listing and navigation on the server.
    - Shell access for server-side tasks.
    - Built-in commands for server management, such as exiting or listing sessions.
8. **Secure Communication**:
    - All data transmissions are encrypted using custom encryption methods.
    - Handles HTTP GET, POST, and PUT requests with appropriate security checks.
9. **Customization and Extensibility**:
    - Configurable settings, such as input timeouts and keep-alive commands.
    - Modular design makes it easy to add new features.
10. **Cross-Platform Compatibility**:
	- Supports both Windows and Linux clients for most functionalities.

## Technology Stack
1. **Networking**:
    - **`http.server.BaseHTTPRequestHandler`** and **`http.server.ThreadingHTTPServer`**: For creating a custom multi-threaded HTTP server to handle requests and responses.
    - **`requests`**: Provides streamlined HTTP methods (**`get`, `post`, `put`**) for handling client-server communication.
2. **Encryption and Security**:
    - **`encryption.cipher`**: A custom encryption module for securing communication between the server and clients.
    - **`pyzipper.AESZipFile`**: Used for creating encrypted ZIP files using AES encryption and LZMA compression.
3. **File and Directory Management**:
    - **`os.listdir`, `os.mkdir`, `os.path`, `os.getcwd`, `os.chdir`**: Manage files and directories on the server, including navigation and storage.
4. **Process Management**:
    - **`multiprocessing.Process`**: Enables concurrent execution of tasks in separate processes for enhanced performance.
    - **`subprocess.run`, `subprocess.PIPE`, `subprocess.STDOUT`, `subprocess.Popen`**: Facilitate executing shell commands and capturing their outputs.
5. **Input Handling and Timing**:
    - **`inputimeout` and `TimeoutOccurred`**: Handle user input with a timeout to maintain server responsiveness.
    - **`time.sleep` and `time.time`**: Used for implementing delays and measuring durations.
6. **System and Shell Integration**:
    - **`os.system`**: Executes shell commands on the server directly.
    - **`setting.SHELL`**: Allows running a server shell for additional control.
    - **`os.getenv`**: Accesses environment variables for system information.
7. **User Interaction and Clipboard Management**:
    - **`pyperclip.paste`**: Interacts with the clipboard for transferring text or data.
    - **`pynput.keyboard.Listener`, `pynput.keyboard.Key`, `pynput.keyboard.Controller`**: Used for monitoring and simulating keyboard input.
8. **Graphical and Display Interaction**:
    - **`PIL.ImageGrab` and `PIL.Image`**: Capture screenshots and manage image processing.
    - **`rotatescreen.get_display`**: Access display rotation settings.
9. **Audio Features**:
	- **`winsound.playsound`** and **`winsound.SND_ASYNC`**: Play audio files or system sounds asynchronously.
10. **Configuration and Settings**:
	- **`setting` module**: Provides centralized configuration for critical parameters like encryption keys, proxy settings, and server delays.
11. **Date and Time Management**:
	- **`datetime.datetime`**: Tracks and logs important server events with precise timestamps.
12. **String and URL Parsing**:
	- **`email.utils.unquote`** and **`urllib.parse.unquote_plus`**: Decode and parse encoded strings and URLs in HTTP requests.
## **Available Server Commands**

These commands are executed on the server to manage pwned sessions, files, and server operations:

- **`server show clients`**: Display all active client sessions and the currently controlled session.
- **`server control [ID]`**: Switch control to the client session with the specified ID.
- **`server unzip [FILENAME]`**: Decrypt and extract a file from the incoming directory on the server.
- **`server zip [FILENAME]`**: Encrypt and compress a file into the outgoing directory on the server.
- **`server list [DIRECTORY]`**: List the contents of the specified directory on the server.
- **`server shell`**: Launch a shell session directly on the server.
- **`server exit`**: Safely shut down the server.
- **`server help`**: Display detailed information about server commands.

## **Available Client Commands**

These commands are executed to interact with the controlled client:

- **`client kill`**: Terminate the current client session.
- **`client download [FILENAME]`**: Fetch a file from the server to the client.
- **`client upload [FILENAME]`**: Send a file from the client to the server.
- **`client zip [FILENAME]`**: Encrypt and compress a file on the client.
- **`client unzip [FILENAME]`**: Decrypt and extract a file on the client.
- **`client delay [SECONDS]`**: Configure the delay between reconnection attempts.
- **`client get clipboard`**: Retrieve the current clipboard contents from the client.
- **`client screenshot`**: Capture a screenshot of the client’s screen.
- **`client type [TEXT]`**: Simulate typing the specified text on the client (works on Windows or Linux with X server or `uinput`).
- **`client keylogger on / off`**: Start or stop the keylogger on the client (Windows or Linux with X server or `uinput`).
- **`client display [image_file]`**: Display an image on the client’s screen.
- **`client flip screen`**: Invert the client’s screen orientation (Windows only).
- **`client max volume`**: Set the client’s audio volume to maximum (Windows or Linux with X server or `uinput`).
- **`client play [sound.wav]`**: Play a `.wav` sound file on the client (Windows only).
- **`[command] &`**: Execute a command in the background on the client.
