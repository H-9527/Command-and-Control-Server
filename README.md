# Command and Control (C2) Server: A Python Project for Penetration Testing

## Disclaimer:
__This project is intended solely for educational and ethical purposes. The C2 server is designed to showcase Python programming skills and to aid in understanding the concepts of penetration testing and red team operations. The development of this project was inspired by concepts learned in a Udemy course, Design Command and Control using Python 3. Unauthorized use of this software on systems without explicit permission is strictly prohibited and may violate laws and regulations. This tool is provided "as is," without warranty of any kind, either expressed or implied. The author assumes no liability or responsibility for any misuse or damage caused by this software. Always use this tool in compliance with applicable laws and only in controlled environments or with explicit authorization.__

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
