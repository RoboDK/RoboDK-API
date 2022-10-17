# Copyright 2015-2021 - RoboDK Inc. - https://robodk.com/
# Licensed under the Apache License, Version 2.0 (the "License")
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# --------------------------------------------
# --------------- DESCRIPTION ----------------
#
# This is a dialog toolbox for RoboDK API for Python
# This toolbox includes user prompts, open file dialogs, messages, etc.
#
# More information about the RoboDK API for Python here:
#     https://robodk.com/doc/en/RoboDK-API.html
#     https://robodk.com/doc/en/PythonAPI/index.html
#
# --------------------------------------------

_tkinter_available = True
import sys
if sys.version_info[0] < 3:
    # Python 2.X only:
    try:
        import Tkinter as tkinter
        import tkFileDialog as filedialog
        import tkMessageBox as messagebox
    except:
        _tkinter_available = False
else:
    # Python 3.x only
    try:
        import tkinter
        from tkinter import filedialog
        from tkinter import messagebox
    except ModuleNotFoundError:
        _tkinter_available = False

if _tkinter_available:

    def getOpenFile(path_preference="C:/RoboDK/Library/", strfile='', strtitle='Open file ...', defaultextension='.txt', filetypes=[('All files', '.*'), ('Text files', '.txt')]):
        """Pop up a file dialog window to select a file to open. Returns a file object opened in read-only mode. Use returned value.name to retrieve the file path."""
        options = {}
        options['initialdir'] = path_preference
        options['title'] = strtitle
        options['defaultextension'] = defaultextension  #'.txt'
        options['filetypes'] = filetypes  # [('all files', '.*'), ('text files', '.txt')]
        options['initialfile'] = strfile
        root = tkinter.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        file_path = filedialog.askopenfilename(**options)
        # same as: file_path = tkinter.filedialog.askopenfilename()
        return file_path

    def getSaveFile(path_preference="C:/RoboDK/Library/", strfile='file.txt', strtitle='Save file as ...', defaultextension='.txt', filetypes=[('All files', '.*'), ('Text files', '.txt')]):
        """Pop up a file dialog window to select a file to save. Returns a file object opened in write-only mode. Use returned value.name to retrieve the file path."""
        options = {}
        options['initialdir'] = path_preference
        options['title'] = strtitle
        options['defaultextension'] = defaultextension  #'.txt'
        options['filetypes'] = filetypes  # [('all files', '.*'), ('text files', '.txt')]
        options['initialfile'] = strfile
        #options['parent'] = root
        root = tkinter.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        file_path = filedialog.asksaveasfile(**options)
        #same as: file_path = tkinter.filedialog.asksaveasfile(**options)
        return file_path

    def getOpenFileName(path_preference="C:/RoboDK/Library/", strfile='', strtitle='Open file ...', defaultextension='.txt', filetypes=[('All files', '.*'), ('Text files', '.txt')]):
        """Pop up a file dialog window to select a file to open. Returns the file path as a string."""
        options = {}
        options['initialdir'] = path_preference
        options['title'] = strtitle
        options['defaultextension'] = defaultextension  #'.txt'
        options['filetypes'] = filetypes  # [('all files', '.*'), ('text files', '.txt')]
        options['initialfile'] = strfile
        root = tkinter.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        file_path = filedialog.askopenfilename(**options)
        # same as: file_path = tkinter.filedialog.askopenfilename()
        return file_path

    def getSaveFileName(path_preference="C:/RoboDK/Library/", strfile='file.txt', strtitle='Save file as ...', defaultextension='.txt', filetypes=[('All files', '.*'), ('Text files', '.txt')]):
        """Pop up a file dialog window to select a file to save. Returns the file path as a string."""
        options = {}
        options['initialdir'] = path_preference
        options['title'] = strtitle
        options['defaultextension'] = defaultextension  #'.txt'
        options['filetypes'] = filetypes  # [('all files', '.*'), ('text files', '.txt')]
        options['initialfile'] = strfile
        #options['parent'] = root
        root = tkinter.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        file_path = filedialog.asksaveasfilename(**options)
        #same as: file_path = tkinter.filedialog.asksaveasfile(**options)
        return file_path

    def getSaveFolder(path_programs='/', popup_msg='Select a directory to save your program'):
        """Ask the user to select a folder to save a program or other file. Returns the path of the folder as a string."""
        root = tkinter.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        dirname = filedialog.askdirectory(initialdir=path_programs, title=popup_msg)
        if len(dirname) < 1:
            dirname = None

        return dirname

    def getOpenFolder(path_preference="C:/RoboDK/Library/", strtitle='Open folder ...'):
        """Pop up a folder dialog window to select a folder to open. Returns the path of the folder as a string."""
        options = {}
        options['title'] = strtitle
        options['initialdir'] = path_preference
        root = tkinter.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        file_path = filedialog.askdirectory(**options)
        return file_path

    def ShowMessage(msg, title=None):
        """Show a blocking message"""
        print(msg)
        if title is None:
            title = msg

        root = tkinter.Tk()
        root.overrideredirect(1)
        root.withdraw()
        root.attributes("-topmost", True)
        result = messagebox.showinfo(title, msg)  #, icon='warning')#, parent=texto)
        root.destroy()
        return result

    def ShowMessageYesNo(msg, title=None):
        """Show a blocking message and let the user answer Yes or No"""
        print(msg)
        if title is None:
            title = msg

        root = tkinter.Tk()
        root.overrideredirect(1)
        root.withdraw()
        root.attributes("-topmost", True)
        result = messagebox.askyesno(title, msg)  #, icon='warning')#, parent=texto)
        root.destroy()
        return result

    def ShowMessageYesNoCancel(msg, title=None):
        """Show a blocking message and let the user answer Yes, No or Cancel"""
        print(msg)
        if title is None:
            title = msg

        root = tkinter.Tk()
        root.overrideredirect(1)
        root.withdraw()
        root.attributes("-topmost", True)
        result = messagebox.askyesnocancel(title, msg)  #, icon='warning')#, parent=texto)
        root.destroy()
        return result

    class MessageBox(object):

        def __init__(self, msg, b1, b2, frame, t, entry):

            root = self.root = tkinter.Tk()
            root.title('Input')
            self.msg = str(msg)
            # ctrl+c to copy self.msg
            root.bind('<Control-c>', func=self.to_clip)
            # remove the outer frame if frame=False
            if not frame:
                root.overrideredirect(True)
            # default values for the buttons to return
            self.b1_return = True
            self.b2_return = False
            # if b1 or b2 is a tuple unpack into the button text & return value
            if isinstance(b1, tuple):
                b1, self.b1_return = b1
            if isinstance(b2, tuple):
                b2, self.b2_return = b2
            # main frame
            frm_1 = tkinter.Frame(root)
            frm_1.pack(ipadx=2, ipady=2)
            # the message
            message = tkinter.Label(frm_1, text=self.msg)
            message.pack(padx=8, pady=8)
            # if entry=True create and set focus
            if entry is not None:
                if entry == True:
                    entry = ''
                self.entry = tkinter.Entry(frm_1)
                self.entry.pack()
                self.entry.insert(0, entry)
                self.entry.focus_set()
            # button frame
            frm_2 = tkinter.Frame(frm_1)
            frm_2.pack(padx=4, pady=4)
            # buttons
            btn_1 = tkinter.Button(frm_2, width=8, text=b1)
            btn_1['command'] = self.b1_action
            btn_1.pack(side='left')
            if not entry:
                btn_1.focus_set()
            btn_2 = tkinter.Button(frm_2, width=8, text=b2)
            btn_2['command'] = self.b2_action
            btn_2.pack(side='left')
            # the enter button will trigger the focused button's action
            btn_1.bind('<KeyPress-Return>', func=self.b1_action)
            btn_2.bind('<KeyPress-Return>', func=self.b2_action)
            # roughly center the box on screen
            # for accuracy see: http://stackoverflow.com/a/10018670/1217270
            root.update_idletasks()
            xp = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
            yp = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
            geom = (root.winfo_width(), root.winfo_height(), xp, yp)
            root.geometry('{0}x{1}+{2}+{3}'.format(*geom))
            # call self.close_mod when the close button is pressed
            root.protocol("WM_DELETE_WINDOW", self.close_mod)
            # a trick to activate the window (on windows 7)
            #root.deiconify()
            # if t is specified: call time_out after t seconds
            if t:
                root.after(int(t * 1000), func=self.time_out)

        def b1_action(self, event=None):
            try:
                x = self.entry.get()
            except AttributeError:
                self.returning = self.b1_return
                self.root.quit()
            else:
                if x:
                    self.returning = x
                    self.root.quit()

        def b2_action(self, event=None):
            self.returning = self.b2_return
            self.root.quit()

        # remove this function and the call to protocol
        # then the close button will act normally
        def close_mod(self):
            pass

        def time_out(self):
            try:
                x = self.entry.get()
            except AttributeError:
                self.returning = None
            else:
                self.returning = x
            finally:
                self.root.quit()

        def to_clip(self, event=None):
            self.root.clipboard_clear()
            self.root.clipboard_append(self.msg)

    def mbox(msg, b1='OK', b2='Cancel', frame=True, t=False, entry=None):
        """Create an instance of MessageBox, and get data back from the user.

        :param msg: string to be displayed
        :type msg: str
        :param b1: left button text, or a tuple (<text for button>, <to return on press>)
        :type b1: str, tuple
        :param b2: right button text, or a tuple (<text for button>, <to return on press>)
        :type b2: str, tuple
        :param frame: include a standard outerframe: True or False
        :type frame: bool
        :param t: time in seconds (int or float) until the msgbox automatically closes
        :type t: int, float
        :param entry: include an entry widget that will provide its contents returned. Provide text to fill the box
        :type entry: None, bool, str

        Example:

            .. code-block:: python

                name = mbox('Enter your name', entry=True)
                name = mbox('Enter your name', entry='default')
                if name:
                    print("Value: " + name)

                value = mbox('Male or female?', ('male', 'm'), ('female', 'f'))
                mbox('Process done')

        """
        msgbox = MessageBox(msg, b1, b2, frame, t, entry)

        try:
            from robodk.robolink import getPathIcon
            iconpath = getPathIcon()
            msgbox.root.iconbitmap(iconpath)
        except:
            print("RoboDK's Robolink module not found")

        msgbox.root.attributes("-topmost", True)
        msgbox.root.mainloop()
        # the function pauses here until the mainloop is quit
        msgbox.root.destroy()
        return msgbox.returning


if __name__ == "__main__":
    pass