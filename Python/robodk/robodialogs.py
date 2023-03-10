# Copyright 2015-2022 - RoboDK Inc. - https://robodk.com/
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

import sys

# robodialogs is compatible with PySide2 and tkinter. At least one must be present.
ENABLE_QT = False
try:
    from PySide2 import QtWidgets, QtCore
    ENABLE_QT = True
except:
    pass

ENABLE_TK = False
try:
    if sys.version_info[0] < 3:
        import Tkinter as tkinter
        import tkFileDialog as filedialog
        import tkMessageBox as messagebox
    else:
        import tkinter
        from tkinter import filedialog
        from tkinter import messagebox
    ENABLE_TK = True
except:
    pass

if not ENABLE_TK and not ENABLE_QT:
    s = 'PySide2 and/or tkinter is not present on the system. Please install PySide2: "python -m pip install PySide2" or "python -m pip install robodk[apps]"'
    print(s)
    #raise ImportError(s)

FILE_TYPES_ALL = ('All Files', '.*')  #: File type filter for all files
FILE_TYPES_ROBODK = ('RoboDK Files', '.sld .rdk .robot .tool .rdka .rdkbak .rdkp .py')  #: File type filter for RoboDK files
FILE_TYPES_3D_OBJECT = ('3D Object Files', '.sld .stl .iges .igs .step .stp .obj .slp .3ds .dae .blend .wrl .wrml')  #: File type filter for 3D object files
FILE_TYPES_TEXT = ('Text Files', '.txt .csv')  #: File type filter for text files
FILE_TYPES_IMG = ('Image Files', '.png .jpg')  #: File type filter for image files
FILE_TYPES_CAM = ('CAM Files', '.cnc .nc .apt .gcode .ngc .nci .anc .dxf .aptsource .cls .acl .cl .clt .ncl .knc')  #: File type filter for CAD/CAM files
FILE_TYPES_ROBOT = ('Robot Files', '.mod .src .ls .jbi .prm .script .urp')  #: File type filter for robot files

DEFAULT_FOLDER = "C:/RoboDK/Library/"  # Default folder of dialogs
DEFAULT_FILE_EXT = '.*'  # Default file extension of dialogs
DEFAULT_FILE_TYPES = [FILE_TYPES_ALL, FILE_TYPES_ROBODK, FILE_TYPES_3D_OBJECT, FILE_TYPES_TEXT, FILE_TYPES_IMG, FILE_TYPES_CAM, FILE_TYPES_ROBOT]  # Default file type filter for dialogs


def getOpenFile(path_preference=DEFAULT_FOLDER, strfile='', strtitle='Open File', defaultextension=DEFAULT_FILE_EXT, filetypes=DEFAULT_FILE_TYPES):
    """
    .. deprecated:: 5.5
        Obsolete. Use :func:`~robodk.robodialogs.getOpenFileName` instead.

    Pop up a file dialog window to select a file to open.
    Returns a file object opened in read-only mode.
    Use returned value.name to retrieve the file path.

    :param str path_preference: The initial folder path, optional
    :param str strfile: The initial file name (with extension), optional
    :param str strtitle: The dialog title, optional
    :param str defaultextension: The initial file extension filter, e.g. '.*'
    :param filetypes: The available file type filters, e.g. '[('All Files', '.*'), ('Text Files', '.txt .csv')]'
    :type filetypes: list of tuples of str

    :return: An read-only handle to the file, or None if the user cancels
    :rtype: TextIOWrapper

    .. seealso:: :func:`~robodk.robodialogs.getOpenFileName`
    """
    if ENABLE_QT:
        file_path = DialogsQt.getOpenFileName(path_preference, strfile, strtitle, defaultextension, filetypes)
        if not file_path:
            return None
        return open(file_path, 'r')
    else:
        return DialogsTk.getOpenFile(path_preference, strfile, strtitle, defaultextension, filetypes)


def getSaveFile(path_preference=DEFAULT_FOLDER, strfile='', strtitle='Save As', defaultextension=DEFAULT_FILE_EXT, filetypes=DEFAULT_FILE_TYPES):
    """
    .. deprecated:: 5.5
        Obsolete. Use :func:`~robodk.robodialogs.getSaveFileName` instead.

    Pop up a file dialog window to select a file to save.
    Returns a file object opened in write-only mode.
    Use returned value.name to retrieve the file path.

    :param str path_preference: The initial folder path, optional
    :param str strfile: The initial file name (with extension), optional
    :param str strtitle: The dialog title, optional
    :param str defaultextension: The initial file extension filter, e.g. '.*'
    :param filetypes: The available file type filters, e.g. '[('All Files', '.*'), ('Text Files', '.txt .csv')]'
    :type filetypes: list of tuples of str

    :return: An write-only handle to the file, or None if the user cancels
    :rtype: TextIOWrapper

    .. seealso:: :func:`~robodk.robodialogs.getSaveFileName`
    """
    if ENABLE_QT:
        file_path = DialogsQt.getSaveFileName(path_preference, strfile, strtitle, defaultextension, filetypes)
        if not file_path:
            return None
        return open(file_path, 'w')
    else:
        return DialogsTk.getSaveFile(path_preference, strfile, strtitle, defaultextension, filetypes)


def getOpenFileName(path_preference=DEFAULT_FOLDER, strfile='', strtitle='Open File', defaultextension=DEFAULT_FILE_EXT, filetypes=DEFAULT_FILE_TYPES):
    """
    Pop up a file dialog window to select a file to open.
    Returns the file path as a string.

    :param str path_preference: The initial folder path, optional
    :param str strfile: The initial file name (with extension), optional
    :param str strtitle: The dialog title, optional
    :param str defaultextension: The initial file extension filter, e.g. '.*'
    :param filetypes: The available file type filters, e.g. '[('All Files', '.*'), ('Text Files', '.txt .csv')]'
    :type filetypes: list of tuples of str

    :return: The file path, or None if the user cancels
    :rtype: str

    .. seealso:: :func:`~robodk.robodialogs.getOpenFileNames`
    """
    if ENABLE_QT:
        return DialogsQt.getOpenFileName(path_preference, strfile, strtitle, defaultextension, filetypes)
    else:
        return DialogsTk.getOpenFileName(path_preference, strfile, strtitle, defaultextension, filetypes)


def getOpenFileNames(path_preference=DEFAULT_FOLDER, strfile='', strtitle='Open File(s)', defaultextension=DEFAULT_FILE_EXT, filetypes=DEFAULT_FILE_TYPES):
    """
    Pop up a file dialog window to select one or more file to open.
    Returns the file path as a list of string.

    :param str path_preference: The initial folder path, optional
    :param str strfile: The initial file name (with extension), optional
    :param str strtitle: The dialog title, optional
    :param str defaultextension: The initial file extension filter, e.g. '.*'
    :param filetypes: The available file type filters, e.g. '[('All Files', '.*'), ('Text Files', '.txt .csv')]'
    :type filetypes: list of tuples of str

    :return: A list of file path(s), or None if the user cancels
    :rtype: list of str

    .. seealso:: :func:`~robodk.robodialogs.getOpenFileName`
    """
    if ENABLE_QT:
        return DialogsQt.getOpenFileNames(path_preference, strfile, strtitle, defaultextension, filetypes)
    else:
        return DialogsTk.getOpenFileNames(path_preference, strfile, strtitle, defaultextension, filetypes)


def getSaveFileName(path_preference=DEFAULT_FOLDER, strfile='', strtitle='Save As', defaultextension=DEFAULT_FILE_EXT, filetypes=DEFAULT_FILE_TYPES):
    """
    Pop up a file dialog window to select a file to save.
    Returns the file path as a string.

    :param str path_preference: The initial folder path, optional
    :param str strfile: The initial file name (with extension), optional
    :param str strtitle: The dialog title, optional
    :param str defaultextension: The initial file extension filter, e.g. '.*'
    :param filetypes: The available file type filters, e.g. '[('All Files', '.*'), ('Text Files', '.txt .csv')]'
    :type filetypes: list of tuples of str

    :return: The file path, or None if the user cancels
    :rtype: str

    .. seealso:: :func:`~robodk.robodialogs.getOpenFileName`
    """
    if ENABLE_QT:
        return DialogsQt.getSaveFileName(path_preference, strfile, strtitle, defaultextension, filetypes)
    else:
        return DialogsTk.getSaveFileName(path_preference, strfile, strtitle, defaultextension, filetypes)


def getOpenFolder(path_preference=DEFAULT_FOLDER, strtitle='Open Folder'):
    """
    Pop up a folder dialog window to select a folder to open.
    Returns the path of the folder as a string.

    :param str path_preference: The initial folder path, optional
    :param str strtitle: The dialog title, optional

    :return: The folder path, or None if the user cancels
    :rtype: str

    .. seealso:: :func:`~robodk.robodialogs.getSaveFolder`
    """
    if ENABLE_QT:
        return DialogsQt.getOpenFolder(path_preference, strtitle)
    else:
        return DialogsTk.getOpenFolder(path_preference, strtitle)


def getSaveFolder(path_preference=DEFAULT_FOLDER, strtitle='Save to Folder'):
    """
    Pop up a folder dialog window to select a folder to save into.
    Returns the path of the folder as a string.

    :param str path_preference: The initial folder path, optional
    :param str strtitle: The dialog title, optional

    :return: The folder path, or None if the user cancels
    :rtype: str

    .. seealso:: :func:`~robodk.robodialogs.getOpenFolder`
    """
    if ENABLE_QT:
        return DialogsQt.getSaveFolder(path_preference, strtitle)
    else:
        return DialogsTk.getSaveFolder(path_preference, strtitle)


def ShowMessage(msg, title=None):
    """
    Show a blocking message, with an 'OK' button.

    :param str msg: The message to be displayed
    :param str title: The window title, optional

    :return: True
    :rtype: bool

    .. seealso:: :func:`~robodk.robodialogs.ShowMessageOkCancel`
    """
    if ENABLE_QT:
        return DialogsQt.ShowMessage(msg, title)
    else:
        return DialogsTk.ShowMessage(msg, title)


def ShowMessageOkCancel(msg, title=None):
    """
    Show a blocking message, with 'OK' and 'Cancel' buttons.

    :param str msg: The message to be displayed
    :param str title: The window title, optional

    :return: True if the user clicked 'OK', false for everything else
    :rtype: bool

    .. seealso:: :func:`~robodk.robodialogs.ShowMessage`
    """
    if ENABLE_QT:
        return DialogsQt.ShowMessageOkCancel(msg, title)
    else:
        return DialogsTk.ShowMessageOkCancel(msg, title)


def ShowMessageYesNo(msg, title=None):
    """
    Show a blocking message, with 'Yes' and 'No' buttons.

    :param str msg: The message to be displayed
    :param str title: The window title, optional

    :return: True if the user clicked 'Yes', false for everything else
    :rtype: bool

    .. seealso:: :func:`~robodk.robodialogs.ShowMessageYesNoCancel`, :func:`~robodk.robodialogs.ShowMessageOkCancel`
    """
    if ENABLE_QT:
        return DialogsQt.ShowMessageYesNo(msg, title)
    else:
        return DialogsTk.ShowMessageYesNo(msg, title)


def ShowMessageYesNoCancel(msg, title=None):
    """
    Show a blocking message, with 'Yes', 'No' and 'Cancel' buttons.

    :param str msg: The message to be displayed
    :param str title: The window title, optional

    :return: True for 'Yes', false for 'No', and None for 'Cancel'
    :rtype: bool

    .. seealso:: :func:`~robodk.robodialogs.ShowMessageYesNo`
    """
    if ENABLE_QT:
        return DialogsQt.ShowMessageYesNoCancel(msg, title)
    else:
        return DialogsTk.ShowMessageYesNoCancel(msg, title)


def mbox(msg, b1='OK', b2='Cancel', frame=True, t=False, entry=None, *args, **kwargs):
    """
    .. deprecated:: 5.5
        Obsolete. Use :func:`~robodk.robodialogs.InputDialog` instead.

    Create an instance of MessageBox, and get data back from the user.

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

    .. seealso:: :func:`~robodk.robodialogs.InputDialog`
    """
    if ENABLE_QT and b1 == 'OK' and b2 == 'Cancel' and frame and t is False and entry is not None:
        return DialogsQt.InputDialog(msg=msg, value=entry, title='Input')
    else:
        return DialogsTk.mbox(msg, b1, b2, frame, t, entry)


def InputDialog(msg, value, title=None, default_button=False, default_value=None, embed=False, actions=None, *args, **kwargs):
    """
    Show a blocking input dialog, with 'OK' and 'Cancel' buttons.

    The input field is automatically created for supported types:
        - Base types: bool, int, float, str
        - list or tuple of base types
        - dropdown formatted as [int, [str, str, ...]]. e.g. [1, ['Option #1', 'Option #2']] where 1 means the default selected option is Option #2.
        - dictionary of supported types, where the key is the field's label. e.g. {'This is a bool!' : True}.

    :param str msg: Message to the user (describes what to enter)
    :param value: Initial value of the input (see supported types)
    :param str title: Window title, optional
    :param default_button: Show a button to reinitialize the input to default, defaults to false
    :param default_value: Default values to restore. If not provided, the original values will be used
    :param embed title: Embed the window inside RoboDK, defaults to false
    :param actions: List of optional action callbacks to add as buttons, formatted as [(str, callable), ...]. e.g. [("Button #1", action_1), ("Button #2", action_2)]
    :type actions: list of tuples of str, callable

    :return: The user input if the user clicked 'OK', None for everything else
    :rtype: See supported types

    Example:

        .. code-block:: python

            print(InputDialog('This is as input dialog.\\n\\nEnter an integer:', 0))
            print(InputDialog('This is as input dialog.\\n\\nEnter a float:', 0.0))
            print(InputDialog('This is as input dialog.\\n\\nEnter text:', ''))
            print(InputDialog('This is as input dialog.\\n\\nSet a boolean:', False))
            print(InputDialog('This is as input dialog.\\n\\nSelect from a dropdown:', [0, ['RoboDK is the best', 'I love RoboDK!', "Can't hate it, can I?"]]))
            print(InputDialog('This is as input dialog.\\n\\nSet multiple entries:', {
                'Enter an integer:': 0,
                'Enter a float:': 0.0,
                'Set a boolean:': False,
                'Enter text:': '',
                'Select from a dropdown:': [0, ['RoboDK is the best!', 'I love RoboDK!', "Can't hate it, can I?"]],
                'Edit int list:': [0, 0, 0],
                'Edit float list:': [0., 0.],
            }))

    """
    if ENABLE_QT:
        return DialogsQt.InputDialog(msg=msg, value=value, title=title, default_button=default_button, default_value=default_value, embed=embed, actions=actions, *args, **kwargs)
    else:
        return DialogsTk.InputDialog(msg=msg, value=value, title=title, default_button=default_button, default_value=default_value, embed=embed, actions=actions, *args, **kwargs)


def _message_to_window_title(message):
    return message.split('\n', 1)[0].split('.', 1)[0].split(':', 1)[0]


if ENABLE_TK:

    from robodk.roboapps import get_tk_app, value_to_tk_widget, widget_to_value

    class DialogsTk:

        @staticmethod
        def getOpenFile(path_preference=DEFAULT_FOLDER, strfile='', strtitle='Open File', defaultextension=DEFAULT_FILE_EXT, filetypes=DEFAULT_FILE_TYPES):
            options = {}
            options['initialdir'] = path_preference
            options['title'] = strtitle
            options['defaultextension'] = defaultextension
            options['filetypes'] = filetypes
            options['initialfile'] = strfile
            root = get_tk_app()
            root.withdraw()
            root.attributes("-topmost", True)
            file_path = filedialog.askopenfile(**options)
            return file_path

        @staticmethod
        def getSaveFile(path_preference=DEFAULT_FOLDER, strfile='', strtitle='Save As', defaultextension=DEFAULT_FILE_EXT, filetypes=DEFAULT_FILE_TYPES):
            options = {}
            options['initialdir'] = path_preference
            options['title'] = strtitle
            options['defaultextension'] = defaultextension
            options['filetypes'] = filetypes
            options['initialfile'] = strfile
            root = get_tk_app()
            root.withdraw()
            root.attributes("-topmost", True)
            file_path = filedialog.asksaveasfile(**options)
            return file_path

        @staticmethod
        def getOpenFileName(path_preference=DEFAULT_FOLDER, strfile='', strtitle='Open File', defaultextension=DEFAULT_FILE_EXT, filetypes=DEFAULT_FILE_TYPES):
            options = {}
            options['initialdir'] = path_preference
            options['title'] = strtitle
            options['defaultextension'] = defaultextension
            options['filetypes'] = filetypes
            options['initialfile'] = strfile
            root = get_tk_app()
            root.withdraw()
            root.attributes("-topmost", True)
            file_path = filedialog.askopenfilename(**options)
            return file_path

        @staticmethod
        def getOpenFileNames(path_preference=DEFAULT_FOLDER, strfile='', strtitle='Open File(s)', defaultextension=DEFAULT_FILE_EXT, filetypes=DEFAULT_FILE_TYPES):
            options = {}
            options['initialdir'] = path_preference
            options['title'] = strtitle
            options['defaultextension'] = defaultextension
            options['filetypes'] = filetypes
            options['initialfile'] = strfile
            root = get_tk_app()
            root.withdraw()
            root.attributes("-topmost", True)
            file_path = filedialog.askopenfilenames(**options)
            return file_path

        @staticmethod
        def getSaveFileName(path_preference=DEFAULT_FOLDER, strfile='', strtitle='Save As', defaultextension=DEFAULT_FILE_EXT, filetypes=DEFAULT_FILE_TYPES):
            options = {}
            options['initialdir'] = path_preference
            options['title'] = strtitle
            options['defaultextension'] = defaultextension
            options['filetypes'] = filetypes
            options['initialfile'] = strfile
            root = get_tk_app()
            root.withdraw()
            root.attributes("-topmost", True)
            file_path = filedialog.asksaveasfilename(**options)
            return file_path

        @staticmethod
        def getOpenFolder(path_preference=DEFAULT_FOLDER, strtitle='Open Folder'):
            options = {}
            options['title'] = strtitle
            options['initialdir'] = path_preference
            root = get_tk_app()
            root.withdraw()
            root.attributes("-topmost", True)
            file_path = filedialog.askdirectory(**options)
            return file_path

        @staticmethod
        def getSaveFolder(path_preference=DEFAULT_FOLDER, strtitle='Save to Folder'):
            options = {}
            options['title'] = strtitle
            options['initialdir'] = path_preference
            root = get_tk_app()
            root.withdraw()
            root.attributes("-topmost", True)
            file_path = filedialog.askdirectory(**options)
            return file_path

        @staticmethod
        def ShowMessage(msg, title=None):
            print(msg)
            if title is None:
                title = _message_to_window_title(msg)

            root = get_tk_app()
            root.overrideredirect(True)
            root.withdraw()
            root.attributes("-topmost", True)
            result = messagebox.showinfo(title, msg)
            root.destroy()
            return result == 'ok'

        @staticmethod
        def ShowMessageOkCancel(msg, title=None):
            print(msg)
            if title is None:
                title = _message_to_window_title(msg)

            root = get_tk_app()
            root.overrideredirect(True)
            root.withdraw()
            root.attributes("-topmost", True)

            result = messagebox._show(title, msg, messagebox.INFO, messagebox.OKCANCEL)
            root.destroy()
            return result == 'ok'

        @staticmethod
        def ShowMessageYesNo(msg, title=None):
            print(msg)
            if title is None:
                title = _message_to_window_title(msg)

            root = get_tk_app()
            root.overrideredirect(True)
            root.withdraw()
            root.attributes("-topmost", True)
            result = messagebox.askyesno(title, msg)
            root.destroy()
            return result

        @staticmethod
        def ShowMessageYesNoCancel(msg, title=None):
            print(msg)
            if title is None:
                title = _message_to_window_title(msg)

            root = get_tk_app()
            root.overrideredirect(True)
            root.withdraw()
            root.attributes("-topmost", True)
            result = messagebox.askyesnocancel(title, msg)
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

        class InputDialogTk(tkinter.Toplevel):

            def __init__(self, msg, value, actions=None, default=False, default_value=None, title=None, parent=None):
                super().__init__(master=parent)

                # Set the window title
                if title is None:
                    title = _message_to_window_title(msg)
                self.title(title)

                # Store the default value to use when clicking on 'Restore Defaults'
                self.default_value = value
                if default_value is not None:
                    self.default_value = default_value

                self.bind("<Escape>", self.reject)

                # Add the global message
                body = tkinter.Frame(self)
                body.pack(padx=5, pady=5)
                if msg:
                    label = tkinter.Label(body, text=msg)
                    label.grid(row=0, padx=5, sticky=tkinter.W)

                # Create the widget holding the value
                self.widget, self.funcs = value_to_tk_widget(value, body)
                if self.widget is None:
                    raise Exception(f"Invalid or unsupported input type: {value}")
                self.widget.grid(row=1, padx=5, sticky=tkinter.W + tkinter.E)

                # Add the custom button(s)
                if actions:
                    button_box_actions = tkinter.Frame(body)
                    for (button_text, button_action) in actions:
                        button = tkinter.Button(button_box_actions, text=button_text, command=button_action)
                        button.pack(side=tkinter.TOP, padx=5, pady=5)
                    button_box_actions.grid(row=2, sticky=tkinter.N + tkinter.S)

                # Add the 'Restore Defaults' button
                button_box = tkinter.Frame(body)
                if default:
                    w = tkinter.Button(button_box, text="Restore Defaults", width=15, command=self.reset)
                    w.pack(side=tkinter.LEFT, padx=5, pady=5)

                # Add the static buttons
                w = tkinter.Button(button_box, text="Cancel", width=10, command=self.reject)
                w.pack(side=tkinter.RIGHT, padx=5, pady=5)
                w = tkinter.Button(button_box, text="OK", width=10, command=self.accept, default=tkinter.ACTIVE)
                w.pack(side=tkinter.RIGHT, padx=5, pady=5)
                button_box.grid(row=3 if actions else 2, sticky=tkinter.W + tkinter.E)
                body.pack()

                self.body = body

                self.exit_code = 0

            def accept(self, event=None):
                self.exit_code = 1
                self.quit()

            def reject(self, event=None):
                self.exit_code = 0
                self.quit()

            def reset(self):
                self.widget.destroy()

                self.widget, self.funcs = value_to_tk_widget(self.default_value, self.body)
                self.widget.grid(row=1, padx=5, sticky=tkinter.W + tkinter.E)

            def mainloop(self, n=0):
                super().mainloop(n)
                return self.exit_code

        @staticmethod
        def InputDialog(msg, value, title=None, default_button=False, default_value=None, embed=False, actions=None, *args, **kwargs):

            app = get_tk_app()
            app.attributes("-topmost", True)
            dialog = DialogsTk.InputDialogTk(msg=msg, value=value, title=title, default=default_button, default_value=default_value, actions=actions, parent=app)

            if embed:
                from robodk.robolink import EmbedWindow
                EmbedWindow(dialog.title())

            ret = dialog.mainloop()
            if not ret:
                dialog.destroy()
                app.destroy()
                return None

            values = widget_to_value(dialog.funcs, value)

            dialog.destroy()
            app.destroy()

            return values

        @staticmethod
        def mbox(msg, b1='OK', b2='Cancel', frame=True, t=False, entry=None):

            msgbox = DialogsTk.MessageBox(msg, b1, b2, frame, t, entry)

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


if ENABLE_QT:

    from robodk.roboapps import get_qt_app, value_to_qt_widget, widget_to_value

    class DialogsQt:

        @staticmethod
        def convert_filetypes(filetypes, defaultextension=None):
            """Converts a Tkinter format for file types to a Qt format"""
            # From: defaultextension='.txt',              filetypes=[('All files', '.*'), ('Text files', '.txt')
            # To:   defaultextension="All files (*.*)",   filetypes="All files (*.*);;Text files (*.txt)"
            filetypes_qt = []
            defaultextension_qt = None
            for (name, exts) in filetypes:
                exts = exts.split(' ')
                exts_str = "*" + " *".join(exts)
                f = f"{name} ({exts_str.strip()})"
                filetypes_qt.append(f)
                if defaultextension in exts:
                    defaultextension_qt = f

            return ';;'.join(filetypes_qt), defaultextension_qt

        @staticmethod
        def getOpenFileName(path_preference=DEFAULT_FOLDER, strfile='', strtitle='Open File', defaultextension=DEFAULT_FILE_EXT, filetypes=DEFAULT_FILE_TYPES):
            app = get_qt_app()
            filetypes, defaultextension = DialogsQt.convert_filetypes(filetypes, defaultextension)
            file, ext = QtWidgets.QFileDialog.getOpenFileName(None, strtitle, path_preference if not strfile else path_preference + "/" + strfile, filetypes, defaultextension)
            return file if file else None

        @staticmethod
        def getOpenFileNames(path_preference=DEFAULT_FOLDER, strfile='', strtitle='Open File(s)', defaultextension=DEFAULT_FILE_EXT, filetypes=DEFAULT_FILE_TYPES):
            app = get_qt_app()
            filetypes, defaultextension = DialogsQt.convert_filetypes(filetypes, defaultextension)
            file, ext = QtWidgets.QFileDialog.getOpenFileNames(None, strtitle, path_preference if not strfile else path_preference + "/" + strfile, filetypes, defaultextension)
            return file if file else None

        @staticmethod
        def getSaveFileName(path_preference=DEFAULT_FOLDER, strfile='', strtitle='Save As', defaultextension=DEFAULT_FILE_EXT, filetypes=DEFAULT_FILE_TYPES):
            app = get_qt_app()
            filetypes, defaultextension = DialogsQt.convert_filetypes(filetypes, defaultextension)
            file, ext = QtWidgets.QFileDialog.getSaveFileName(None, strtitle, path_preference if not strfile else path_preference + "/" + strfile, filetypes, defaultextension)
            return file if file else None

        @staticmethod
        def getOpenFolder(path_preference=DEFAULT_FOLDER, strtitle='Open Folder'):
            app = get_qt_app()
            file = QtWidgets.QFileDialog.getExistingDirectory(None, strtitle, path_preference, QtWidgets.QFileDialog.ShowDirsOnly)
            return file if file else None

        @staticmethod
        def getSaveFolder(path_preference=DEFAULT_FOLDER, strtitle='Save to Folder'):
            app = get_qt_app()
            file = QtWidgets.QFileDialog.getExistingDirectory(None, strtitle, path_preference, QtWidgets.QFileDialog.ShowDirsOnly)
            return file if file else None

        @staticmethod
        def ShowMessage(msg, title=None):
            print(msg)
            if title is None:
                title = _message_to_window_title(msg)

            app = get_qt_app()

            msg_box = QtWidgets.QMessageBox()
            msg_box.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.MSWindowsFixedSizeDialogHint | QtCore.Qt.WindowStaysOnTopHint)
            msg_box.setWindowTitle(title)
            msg_box.setIcon(QtWidgets.QMessageBox.Information)
            msg_box.setText(msg)
            msg_box.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Ok)
            msg_box.setDefaultButton(QtWidgets.QMessageBox.StandardButton.Ok)

            ret = msg_box.exec()
            return ret == QtWidgets.QMessageBox.StandardButton.Ok

        @staticmethod
        def ShowMessageOkCancel(msg, title=None):
            print(msg)
            if title is None:
                title = _message_to_window_title(msg)

            app = get_qt_app()

            msg_box = QtWidgets.QMessageBox()
            msg_box.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.MSWindowsFixedSizeDialogHint | QtCore.Qt.WindowStaysOnTopHint)
            msg_box.setWindowTitle(title)
            msg_box.setIcon(QtWidgets.QMessageBox.Information)
            msg_box.setText(msg)
            msg_box.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Ok | QtWidgets.QMessageBox.StandardButton.Cancel)
            msg_box.setDefaultButton(QtWidgets.QMessageBox.StandardButton.Ok)

            ret = msg_box.exec()
            return ret == QtWidgets.QMessageBox.StandardButton.Ok

        @staticmethod
        def ShowMessageYesNo(msg, title=None):
            print(msg)
            if title is None:
                title = _message_to_window_title(msg)

            app = get_qt_app()

            msg_box = QtWidgets.QMessageBox()
            msg_box.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.MSWindowsFixedSizeDialogHint | QtCore.Qt.WindowStaysOnTopHint)
            msg_box.setWindowTitle(title)
            msg_box.setIcon(QtWidgets.QMessageBox.Question)
            msg_box.setText(msg)
            msg_box.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No)
            msg_box.setDefaultButton(QtWidgets.QMessageBox.StandardButton.Yes)

            ret = msg_box.exec()
            return ret == QtWidgets.QMessageBox.StandardButton.Yes

        @staticmethod
        def ShowMessageYesNoCancel(msg, title=None):
            print(msg)
            if title is None:
                title = _message_to_window_title(msg)

            app = get_qt_app()

            msg_box = QtWidgets.QMessageBox()
            msg_box.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.MSWindowsFixedSizeDialogHint | QtCore.Qt.WindowStaysOnTopHint)
            msg_box.setWindowTitle(title)
            msg_box.setIcon(QtWidgets.QMessageBox.Question)
            msg_box.setText(msg)
            msg_box.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No | QtWidgets.QMessageBox.StandardButton.Cancel)
            msg_box.setDefaultButton(QtWidgets.QMessageBox.StandardButton.Yes)

            ret = msg_box.exec()
            if ret == QtWidgets.QMessageBox.StandardButton.Cancel:
                return None
            return ret == QtWidgets.QMessageBox.StandardButton.Yes

        class InputDialogQt(QtWidgets.QDialog):

            def __init__(self, msg, value, title=None, default_button=False, default_value=None, actions=None, parent=None, f=QtCore.Qt.Dialog):
                super().__init__(parent, f)

                # Set the window title
                if title is None:
                    title = _message_to_window_title(msg)
                self.setWindowTitle(title)

                # Store the default value to use when clicking on 'Restore Defaults'
                self.default_value = value
                if default_value is not None:
                    self.default_value = default_value

                # Add the global message
                if msg:
                    label = QtWidgets.QLabel(msg, self)
                    label.setWordWrap(True)
                    label.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)

                # Create the widget holding the value
                self.widget, self.funcs = value_to_qt_widget(value)
                if self.widget is None:
                    raise Exception(f"Invalid or unsupported input type: {value}")

                # Add the static buttons
                button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.StandardButton.Ok | QtWidgets.QDialogButtonBox.StandardButton.Cancel, QtCore.Qt.Horizontal, self)
                QtCore.QObject.connect(button_box, QtCore.SIGNAL('accepted()'), self, QtCore.SLOT('accept()'))
                QtCore.QObject.connect(button_box, QtCore.SIGNAL('rejected()'), self, QtCore.SLOT('reject()'))

                # Add the 'Restore Defaults' button
                if default_button:
                    button = button_box.addButton(QtWidgets.QDialogButtonBox.StandardButton.RestoreDefaults)
                    button.clicked.connect(self.reset)

                # Add the custom button(s)
                max_h_actions = 1
                if actions:
                    if len(actions) > max_h_actions:
                        button_box_actions = QtWidgets.QDialogButtonBox(QtCore.Qt.Vertical, self)
                        for (button_text, button_action) in actions:
                            button = button_box_actions.addButton(button_text, QtWidgets.QDialogButtonBox.ButtonRole.ActionRole)
                            button.clicked.connect(button_action)
                    else:
                        for (button_text, button_action) in actions:
                            button = button_box.addButton(button_text, QtWidgets.QDialogButtonBox.ButtonRole.ActionRole)
                            button.clicked.connect(button_action)

                # Add a scrollbar for dictionaries, as they may get very big!
                self.has_scroll = type(value) is dict and len(value.keys()) > 10
                if self.has_scroll:
                    self.scroll_widget = QtWidgets.QScrollArea()
                    self.scroll_widget.setFrameShape(QtWidgets.QFrame.NoFrame)
                    self.scroll_widget.setWidgetResizable(True)
                    self.scroll_widget.setWidget(self.widget)
                    self.scroll_widget.setMinimumWidth(self.widget.minimumWidth() + 20)

                # Create the main layout
                layout = QtWidgets.QVBoxLayout(self)
                layout.setSizeConstraint(QtWidgets.QLayout.SetMinAndMaxSize)
                if msg:
                    layout.addWidget(label)
                layout.addWidget(self.scroll_widget if self.has_scroll else self.widget)
                layout.addSpacing(10)
                if actions and len(actions) > max_h_actions:
                    layout.addWidget(button_box_actions, alignment=QtCore.Qt.AlignmentFlag.AlignHCenter | QtCore.Qt.AlignmentFlag.AlignBottom)
                layout.addWidget(button_box)

            def reset(self):
                widget, self.funcs = value_to_qt_widget(self.default_value)
                if self.has_scroll:
                    self.scroll_widget.takeWidget()
                    self.scroll_widget.setWidget(widget)
                else:
                    self.layout().replaceWidget(self.widget, widget, QtCore.Qt.FindChildOption.FindChildrenRecursively)
                self.widget.deleteLater()
                self.widget = widget

            def showEvent(self, arg__1):
                if self.has_scroll:
                    self.resize(self.sizeHint().expandedTo(self.widget.sizeHint()).boundedTo(self.screen().availableSize() * 2 / 3))
                super().showEvent(arg__1)

        @staticmethod
        def InputDialog(msg, value, title=None, default_button=False, default_value=None, embed=False, actions=None, *args, **kwargs):

            app = get_qt_app()

            dialog = DialogsQt.InputDialogQt(msg=msg, value=value, title=title, default_button=default_button, default_value=default_value, actions=actions, f=QtCore.Qt.Dialog | QtCore.Qt.WindowStaysOnTopHint)

            if embed:
                from robodk.robolink import EmbedWindow
                size = dialog.sizeHint()
                EmbedWindow(dialog.windowTitle(), size_w=size.width(), size_h=size.height())

            ret = dialog.exec()
            if not ret:
                return None

            return widget_to_value(dialog.funcs, value)


if __name__ == "__main__":

    def ShowDialogs():
        print(getOpenFileName())
        print(getOpenFileNames())
        print(getSaveFileName())
        print(getOpenFolder())
        print(getSaveFolder())

        print(ShowMessage('Hello there!\nThis is an informative message.'))
        print(ShowMessageOkCancel('Hello there!\nThis is an informative message, with a cancel option.'))
        print(ShowMessageYesNo('Hello there!\nThis is a question, right?'))
        print(ShowMessageYesNoCancel('Hello there!\nThis is a question, with a cancel option. Right?'))

        print(InputDialog('This is as input dialog.\n\nEnter an integer:', 0))
        print(InputDialog('This is as input dialog.\n\nEnter a float:', 0.0))
        print(InputDialog('This is as input dialog.\n\nEnter text:', ''))
        print(InputDialog('This is as input dialog.\n\nSet a boolean:', False))
        print(InputDialog('This is as input dialog.\n\nSelect from a dropdown:', [0, ['RoboDK is the best', 'I love RoboDK!', "Can't hate it, can I?"]]))
        print(InputDialog('This is as input dialog.\n\nSet multiple entries:', {
            'Enter an integer:': 0,
            'Enter a float:': 0.0,
            'Set a boolean:': False,
            'Enter text:': '',
            'Select from a dropdown:': [0, ['RoboDK is the best!', 'I love RoboDK!', "Can't hate it, can I?"]],
            'Edit int list:': [0, 0, 0],
            'Edit float list:': [0., 0.],
        }))

    ShowDialogs()