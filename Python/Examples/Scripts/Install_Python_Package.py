# This file allows you to easily install required packages for Python

import subprocess
import os
import sys
import io

from robodk import *
from robolink import *


package_name = mbox("Python Package name to install", entry="")
if not package_name:
    quit()

cmd_list = []
cmd_list.append(sys.executable + " -m pip uninstall -y " + package_name)
cmd_list.append(sys.executable + " -m pip install " + package_name)

print("Installing package " + package_name)

RDK = Robolink()

#RDK.ShowMessage(str(os.environ))
#quit()

for cmd in cmd_list:
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for line in io.TextIOWrapper(p.stdout, encoding="utf-8"):  # or another encoding
        # display line output
        line = line.strip()
        # print(line)
        RDK.ShowMessage(line, False)

RDK.ShowMessage("Done installing " + package_name, False)
