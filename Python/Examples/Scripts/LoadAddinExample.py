# This example shows how to enable or disable an Add-in using the Add-in Manager API

plugin_identifier = "com.robodk.app.progutilities"
plugin_action = "enable" # or "disable" ?

from robodk import robolink    # RoboDK API
from robodk import robomath    # Robot toolbox
RDK = robolink.Robolink()

import json

# Request list of current addins
# "mode":
# ExportMinimal       = 0,
# ExportStandard      = 1,
# ExportDetails       = 2,
# ExportEverything    = 3,
StatusEnabled = 2
StatusDisabled = 1

request = {
    "mode": 0
}

print("Make sure the addin manager is loaded:")
print(RDK.PluginLoad("AddinManager", 1))

resultstr = RDK.PluginCommand("Addin Manager", "AddinListJson", json.dumps(request))
# TODO: Process the result (JSON data)
result = json.loads(resultstr)
# print(json.dumps(result, indent=4))
# quit()

plugin_path = None
for p in result:
    if p["identifier"] == plugin_identifier:
        # Warning: there could be different versions of the same addin installed
        print("Plugin found. Details:")
        print(p)
        plugin_path = p["path"]
        if p["status"] == StatusEnabled:
            if plugin_action == "enable":
                print("Plugin already enabled")
                quit()
        
        
        break
        
if plugin_path is None:
    print("Plugin not installed: " + plugin_identifier)
    quit()

print("Udating plugin status to " + plugin_action + ":")
print(plugin_identifier)
print("Plugin path:")
print(plugin_path)


# Enable Add-in by path (by identifier it is not possible as there could be versioons of the same addin, with the same identifier)
request = {
    "path": plugin_path,
    "operation": plugin_action
}
resultstr = RDK.PluginCommand("Addin Manager", "AddinControlJson", json.dumps(request))
result = json.loads(resultstr)
if result["error"] != 0:
    print(json.dumps(result, indent=4))
    raise Exception("Failed to enable addin " + str(result))
