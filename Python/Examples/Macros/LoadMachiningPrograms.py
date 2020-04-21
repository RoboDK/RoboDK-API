from robolink import *
import os
import glob

# ---------------------------
# Start the RoboDK API    
RDK = Robolink()

# Avoid rendering after each step (faster)
RDK.Render(False)

# Select the first robot available
robot = RDK.Item('', ITEM_TYPE_ROBOT)

# ----------------------------------
# Path to look for files (automatically extracted):
# Path of the current Python file
#PATH_FOLDER = os.path.dirname(os.path.realpath(__file__))
# Path of the RDK file:
PATH_FOLDER = RDK.getParam("PATH_OPENSTATION")


def delete_item(name, type):
    """Function helper to easily delete an existing item"""
    item = RDK.Item(name, type)
    if item.Valid():
        program.Delete()    

main_program_name = "MainProgram"
# Hide instructions (faster if we are building programs)
delete_item(main_program_name, ITEM_TYPE_PROGRAM)
main_program = RDK.AddProgram(main_program_name)
# main_program.ShowInstructions(False)

# -------------------------------------------
toolpath_files = glob.glob(PATH_FOLDER + "/*.apt")
for file in toolpath_files:
    program_name = getFileName(file).replace(" ","_")
    milling_options_name = program_name + " settings"
    # Skip the file
    if len(program_name) == 0:
        continue
    
    # Delete previously generated items:
    delete_item(milling_options_name, ITEM_TYPE_MILLING)
    delete_item(program_name, ITEM_TYPE_PROGRAM)
    
    # Create a new robot machining project
    milling_options = RDK.AddMillingProject(milling_options_name)
    
    # Link the milling project to a tool item
    #milling_options.setPoseTool(tool_item)
    
    # Link the milling project to a reference frame
    #milling_options.setPoseFrame(base_item)
    
    # Load the cutter toolpath
    milling_options.setMillingParameters(file)
    
    # Generate the program inside RoboDK
    milling_program = milling_options.Update()
    
    # Add a program call to the main program
    main_program.RunCodeCustom(program_name, INSTRUCTION_CALL_PROGRAM)

    
# Show the instructions for the main program
main_program.ShowInstructions(True)
main_program.ShowTargets(False)

# Check collisions ON or OFF and update the program (recalculates the path and returns useful information)
check_collisions = COLLISION_OFF

# Update the program and check the "health" status of the program
update_result = program.Update(check_collisions)
n_insok = update_result[0]
time = update_result[1]
distance = update_result[2]
percent_ok = update_result[3]*100
str_problems = update_result[4]
if percent_ok < 100.0:
    msg_str = "WARNING! Problems with <strong>%s</strong> (%.1f):<br>%s" % (program_name, percent_ok, str_problems)
else:
    msg_str = "No problems found for program %s" % program_name
    
# Notify the user and ask if we want to generate the programs:
print(msg_str)
generate_progs = mbox(msg_str + "\n\nDo you want to generate all programs?")
if not generate_progs:
    # Terminate
    quit()
    
# Generate all programs available in the station
all_programs = RDK.ItemList(ITEM_TYPE_PROGRAM)
for prog in all_programs:
    file_location = '' # leave the file location to use the default program path and file name
    prog.MakeProgram(file_location)

# Close RoboDK    
# RDK.QuitRoboDK()

