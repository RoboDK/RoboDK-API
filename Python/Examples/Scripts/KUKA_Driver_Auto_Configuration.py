import sys
import ipaddress
import subprocess
import os
import tempfile
from robolink import *
from robodk import *
from robodk.robodialogs import *


def runmain():
    RDK = Robolink()
    robots = [x for x in RDK.ItemList(ITEM_TYPE_ROBOT) if x.setParam('NativeName').lower().startswith('kuka')]
    if not robots:
        ShowMessage("The station does not contain any KUKA robots. Load a KUKA robot first", "Warning")
        return

    robot = robots[0] if len(robots) == 1 else RDK.ItemUserPick("Pick a robot", robots)
    if not robot:
        return

    print("Using robot: ")
    print(robot.Name())

    # Make sure we are using the KUKA bridge driver:
    print("Current driver:")
    print(robot.setParam("PathDriver")) # Requires latest version (2022-11-21 or later)
    robot.setParam("PathDriver", "kukabridge")
    print("Updated driver path")

    connection_params = robot.ConnectionParams()

    try:
        ip = ipaddress.ip_address(connection_params[0])
        if ip.version != 4:
            raise ValueError('IPv6 is not supported')
    except:
        ShowMessage("Incorrect IP address, check your robot's connection settings.", "Error")
        return

    port = connection_params[1]
    if port < 1 or port > 65535:
        ShowMessage("Incorrect port number, the port must be between 1 and 65535.", "Error")
        return

    options = {}
    options['reconnectLimit'] = 0
    options['connectTimeout'] = 2000
    options['dataTimeout'] = 0
    options['keepAliveInterval'] = 5000

    with tempfile.NamedTemporaryFile(mode='wt', delete=False) as file:
        script = file.name
        for key, value in options.items():
            file.write(f"OPTION {key} {value}\n")
        file.write(f"CONNECT {ip} {port}\n")
        file.write("CONFIGURE FORCE\n")
        file.close()

    if not script:
        ShowMessage("Unable to create temporary script file.", "Error")
        return

    path_rdk = RDK.getParam("PATH_ROBODK")
    os.environ["PATH"] += os.pathsep + os.path.abspath(path_rdk + "/bin")
    path_kukabridge = os.path.abspath(path_rdk + "/api/Robot/kukabridge")

    output = ''
    retcode = -1
    with subprocess.Popen([path_kukabridge, "-s", script], stdout=subprocess.PIPE, bufsize=1, universal_newlines=True) as process:
        process.wait()
        output = process.stdout.read()
        retcode = process.returncode

    if len(output) > 0:
        if retcode == 0:
            ShowMessage("Auto-configuration completed successfully.", "Success")
        else:
            output = output.replace("\n\n", "\n");
            ShowMessage(output, "Error during auto-configuration");
    else:
        ShowMessage("Unable to run KUKA driver.", "Error")

    os.unlink(script)


if __name__ == "__main__":
    runmain()
