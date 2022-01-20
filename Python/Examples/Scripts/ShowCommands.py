# Display available commands in RoboDK. Commands can be executed by passing arguments (example: RoboDK.exe -COMMAND=Value) or through the API by calling RDK.Command()
from robodk.robolink import *  # RoboDK API

# Start the RoboDK API
RDK = Robolink()

# Send an empty command: it returns all possible commands separated by tabs and new lines
list_cmd = RDK.Command("", "")
print(list_cmd)

# Convert the string returnted by RoboDK as an HTML table
table_html = ''
table_html += "<style type=\"text/css\">"
table_html += "table.tbl {border-width: 1px;border-style: solid;border-color: gray;margin-top: 0px;margin-bottom: 0px;}"
table_html += "table.tbl td {padding: 1px;text-align: left}"
table_html += "table.tbl th {padding: 1px;}"
#table_html += "table.tbl td:nth-child(1){text-align:left;}"
table_html += "</style>"
table_html += '<p>You can run commands using:<br>'
table_html += '<font face="consolas">    RDK.Command("Command", "Parameter")</font></p><br><br>'
table_html += "<p>You can also pass commands through command line when starting RoboDK or when RoboDK is already running (add '-' to the command name). Example:<br>"
table_html += '<font face="consolas">    RoboDK -Threads=6 -CollisionHidden=1 "path-to-file"</font></p><br><br>'
table_html += "<table cellspacing='0' class='tbl'><tr><td>" + list_cmd[:-4] + "</td></table>"  # remove the last <br>
#table_html = table_html.replace("\t","</td><td>")
#table_html = table_html.replace("<br>","</td></tr><tr><td>")
#RDK.ShowMessage(table_html)
#quit()

list_cmd_item = RDK.ActiveStation().setParam("", "")
print(list_cmd_item)
table_html += "<br><br><br><p>You can also pass commands or set values for items. Example:<br>"
table_html += '<font face="consolas">    item = RDK.Item("My Item")</font><br><font face="consolas">    item.setParam("ItemCommand", "ItemParameter")</font></p><br><br>'
table_html += "<table  cellspacing='0' class='tbl'><tr><td>" + list_cmd_item[:-4] + "</td></table>"  # remove the last <br>
table_html = table_html.replace("\t", "</td><td>")
table_html = table_html.replace("<br>", "</td></tr><tr><td>")
RDK.ShowMessage(table_html)
