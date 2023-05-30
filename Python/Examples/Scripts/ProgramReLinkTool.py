# This script shows how you can change the program links to a tool from one tool object to another
# More information here: https://robodk.com/doc/en/PythonAPI/examples.html#modify-program-instructions

# Type help("robolink") or help("robodk") for more information
# Press F5 to run the script
# Or visit: http://www.robodk.com/doc/PythonAPI/
from robolink import *    # API to communicate with RoboDK
from robodk import *      # basic matrix operations
RDK = Robolink()

# Select the tool to look for
toolA = RDK.ItemUserPick('Select a tool to look for', ITEM_TYPE_TOOL)
if not toolA.Valid():
    quit()

# Select the tool to replace
toolB = RDK.ItemUserPick('Select a tool to replace', ITEM_TYPE_TOOL)    
if not toolB.Valid():
    quit()
    
if toolA == toolB:
    ShowMessage("Both tools are the same")
    quit()
    
# Retrieve tool names, they are needed to operate with instructions
# They should be unique names!
toolA_name = str(toolA.Name())
toolB_name = str(toolB.Name())

# Retrieve all programs and iterate through all programs
programs = RDK.ItemList(ITEM_TYPE_PROGRAM)
for prog in programs:
    RDK.ShowMessage("Modifying program: " + prog.Name(), False)
    nInstructions = prog.InstructionCount()
    for i in range(nInstructions):
        ins_data = prog.setParam(i)
        print("Instruction: " + str(i))
        print(ins_data)
        if ins_data['Type'] == INS_TYPE_CHANGETOOL and ins_data['ToolName'] == toolA_name:
            ins_data["ToolName"] = toolB_name
            prog.setParam(i, ins_data)
        
        if i > 500:
            # Prevent iterating over large robot machining projects that have many points
            break


RDK.ShowMessage("Done", False)