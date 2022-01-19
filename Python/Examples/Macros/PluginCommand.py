# This script allows you to create a program instruction called PluginCommand(command, value)
# And trigger a specific plugin command from a program
#
# Type help("robodk.robolink") or help("robodk.robomath") for more information
# Press F5 to run the script
# Documentation: https://robodk.com/doc/en/RoboDK-API.html
# Reference:     https://robodk.com/doc/en/PythonAPI/index.html
# Note: It is not required to keep a copy of this file, your python script is saved with the station

# Specify a plugin name (if you leave it empty it will send the command to all the loaded plugins
plugin_name = ""

import sys
from robodk.robolink import *

# Start the RoboDK API:
RDK = Robolink()

# Check that we have 2 arguments (0th index is the name of the file)
if len(sys.argv) >= 3:
    from robodk.robolink import *    # RoboDK API
    plugin_command = sys.argv[1]
    plugin_value = sys.argv[2]
    RDK.ShowMessage("Running plugin command: " + plugin_command + "=" + plugin_value, True)

    # The same command will be sent to all plugins unless a plugin name is specified
    RDK.PluginCommand(plugin_name, plugin_command, plugin_value)

else:
    RDK.ShowMessage("Non supported entry: " + str(sys.argv), False)
