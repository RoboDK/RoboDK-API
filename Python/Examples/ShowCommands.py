# Display available commands in RoboDK. Commands can be executed by passing arguments (example: RoboDK.exe -COMMAND=Value) or through the API by calling RDK.Command()
from robolink import *    # RoboDK API
from robodk import *      # Robot toolbox

# Start the RoboDK API
RDK = Robolink()

# Send an empty command: it returns all possible commands separated by tabs and new lines
list_cmd = RDK.Command("","")
print(list_cmd)

# Convert the string returnted by RoboDK as an HTML table
table_html = "<p>You can run commands using:<br>RDK.Command('Command', 'Parameter')</p><br><br>"
table_html += "<table><tr><td>" + list_cmd[:-4] + "</td></table>"# remove the last <br>
table_html = table_html.replace("\t","</td><td>")
table_html = table_html.replace("<br>","</td></tr><tr><td>")
RDK.ShowMessage(table_html)
