# This script shows an example to integrate an extruder with RoboDK
# We need to add this script to the RoboDK project ot trigger sending the E value (Extruder parameter)
# This script meant to work when we are running 3D printing with the driver ("Run on robot" option)

# Send the E_Value over Ethernet (ASCII numbers)
EXTRUDER_IP = '10.10.10.12'  # The IP of the extruder
EXTRUDER_PORT = 100  # The same port as used by the Extruder server

from robodk import *  # required for mbox

E_Value = None
# Check if we are running this program inside another program and passing arguments
import sys
if len(sys.argv) > 1:
    E_Value = float(sys.argv[1])

# If no value is provided, display a message to turn the extruder ON or OFF
if E_Value is None:
    print('Note: This macro can be called as Extruder(0) to turn it ON or Extruder(-1) to turn it OFF')
    entry = mbox('Turn Extruder ON or OFF', ('On', '1'), ('Off', '-1'))
    if not entry:
        quit()

    E_Value = int(entry)

## Optionally, ignore sending the command if we are running in simulation mode
#from robolink import *    # API to communicate with RoboDK
#RDK = Robolink()

# stop if we in simulation mode
#if RDK.RunMode() == RUNMODE_SIMULATE:
#    quit()

# Implement socket communication to send the E_Value over Ethernet/socket
import socket

BUFFER_SIZE = 1024

# Build the byte array to send
bytes2send = bytes(str(E_Value) + '\0', 'ascii')

print("Sending: " + str(bytes2send))
print("Connecting to %s:%i" % (EXTRUDER_IP, EXTRUDER_PORT))

# Connect to the extruder and send byte array
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((EXTRUDER_IP, EXTRUDER_PORT))
s.send(bytes2send)

# Read response:
bytes_recv = s.recv(BUFFER_SIZE)
str_recv = bytes_recv.decode('ascii')
s.close()
print("Response: " + str_recv)
