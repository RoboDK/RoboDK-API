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
# This is a RoboDK Apps toolbox for RoboDK API for Python.
# This toolbox includes checkable apps, app settings, etc.
#
# More information about the RoboDK API for Python here:
#     https://robodk.com/doc/en/RoboDK-API.html
#     https://robodk.com/doc/en/PythonAPI/index.html
# --------------------------------------------
"""
App/actions control utilities.

Use these to control your App's actions: run on click, run while checked, do not kill, etc.
"""

import sys
import time


class RunApplication:
    """Class to detect when the terminate signal is emitted to stop an action.

    .. code-block:: python

        run = RunApplication()
        while run.Run():
            # your main loop to run until the terminate signal is detected
            ...

    """
    time_last = -1
    param_name = None
    RDK = None

    def __init__(self, rdk=None):
        if rdk is None:
            from robodk.robolink import Robolink
            self.RDK = Robolink()
        else:
            self.RDK = rdk

        self.time_last = time.time()
        if len(sys.argv) > 0:
            import os
            path = sys.argv[0]
            folder = os.path.basename(os.path.dirname(path))
            file = os.path.basename(path)
            if file.endswith(".py"):
                file = file[:-3]
            elif file.endswith(".exe"):
                file = file[:-4]

            self.param_name = file + "_" + folder
            self.RDK.setParam(self.param_name, "1")  # makes sure we can run the file separately in debug mode

    def Run(self):
        """Run callback.

        :return: True as long as the App is permitted to run.
        :rtype: bool
        """
        time_now = time.time()
        if time_now - self.time_last < 0.1:
            return True
        self.time_last = time_now
        if self.param_name is None:
            # Unknown start
            return True

        keep_running = not (self.RDK.getParam(self.param_name) == 0)
        return keep_running


def Unchecked():
    """Verify if the command "Unchecked" is present. In this case it means the action was just unchecked from RoboDK (applicable to checkable actions only)."""
    if len(sys.argv) >= 2:
        if "Unchecked" in sys.argv[1:]:
            return True

    return False


def Checked():
    """Verify if the command "Checked" is present. In this case it means the action was just checked from RoboDK (applicable to checkable actions only)."""
    if len(sys.argv) >= 2:
        if "Checked" in sys.argv[1:]:
            return True

    return False


def KeepChecked():
    """Keep an action checked even if the execution of the script completed (this is applicable to Checkable actions only)"""
    print("App Setting: Keep checked")
    sys.stdout.flush()


def SkipKill():
    """For Checkable actions, this setting will tell RoboDK App loader to not kill the process a few seconds after the terminate function is called.
    This is needed if we want the user input to save the file. For example: The Record action from the Record App."""
    print("App Setting: Skip kill")
    sys.stdout.flush()


"""
General utilities
"""


def Str2FloatList(str_values, expected_nvalues=3):
    """Convert a string into a list of floats. It returns None if the array is smaller than the expected size.

    :param str_values: The string containing a list of floats
    :type str_values: list of str
    :param expected_nvalues: Expected number of values in the string list, defaults to 3
    :type expected_nvalues: int, optional
    :return: The list of floats
    :rtype: list of float
    """
    import re
    if str_values is None:
        return None

    values = re.findall("[-+]?\d+[\.]?\d*", str_values)
    valuesok = []
    for i in range(len(values)):
        try:
            valuesok.append(float(values[i]))
        except:
            return None

    if len(valuesok) < expected_nvalues:
        return None

    print('Read values: ' + repr(values))
    return valuesok


def Registry(varname, setvalue=None):
    """Read value from the registry or set a value. It will do so at HKEY_CURRENT_USER so no admin rights required."""
    from sys import platform as _platform
    if _platform == "linux" or _platform == "linux2":
        # Ubuntu, Linux or Debian
        return None
    elif _platform == "darwin":
        # MacOS
        #self.APPLICATION_DIR = "/Applications/RoboDK.app/Contents/MacOS/RoboDK"
        return None
    else:
        # Windows assumed
        if sys.version_info[0] < 3:
            import _winreg
        else:
            import winreg as _winreg

        def KeyExist(key, subkey, access) -> bool:
            try:
                hkey = _winreg.OpenKey(key, subkey, 0, access)
            except OSError as e:
                print(e)
                return None
            return hkey

        # Key settings
        access_flag = _winreg.KEY_READ if setvalue is None else _winreg.KEY_WRITE
        key = _winreg.HKEY_CURRENT_USER
        subkey = "SOFTWARE\\RoboDK"

        # Get the key or create a new one (unless we are reading the value)
        hKey = KeyExist(key, subkey, access_flag | _winreg.KEY_WOW64_64KEY)
        if hKey is None:
            hKey = KeyExist(key, subkey, access_flag | _winreg.KEY_WOW64_32KEY)
            if hKey is None and setvalue is not None:
                try:
                    hKey = _winreg.CreateKeyEx(key, subkey, 0, _winreg.KEY_WRITE | _winreg.KEY_WOW64_64KEY)
                except OSError as e:
                    print(e)
                    return None
            else:
                return None

        if setvalue is None:
            # Read the value.
            try:
                result = _winreg.QueryValueEx(hKey, varname)
                _winreg.CloseKey(hKey)
                return result[0]  # Return only the value from the resulting tuple (value, type_as_int).
            except _winreg.QueryValue as e:
                print(e)
                return None
        else:
            # Write the value
            try:
                _winreg.SetValueEx(hKey, varname, 0, _winreg.REG_SZ, str(setvalue))
                _winreg.CloseKey(hKey)
                return None
            except _winreg.SetValue as e:
                print(e)
                return None


"""
UI utilities (Qt and Tkinter utilities).

Use these to easily create GUI Apps, settings forms, using either Tkinter or Qt (PySide2).
"""

# Default to Qt and revert to tkinter if it fails.
ENABLE_QT = True
if ENABLE_QT:
    try:
        from robodk.robolink import import_install
        import_install("PySide2")
        from PySide2 import QtCore, QtGui, QtWidgets
    except:
        # Can't install Qt, fallback to tkinter
        ENABLE_QT = False

import sys
if sys.version_info[0] < 3:
    # Python 2.X only:
    import Tkinter as tkinter
else:
    # Python 3.x only
    import tkinter


def get_robodk_theme(RDK=None):
    """Get RoboDK's active theme (Options->General->Theme)"""
    if RDK is None:
        from robodk.robolink import Robolink
        RDK = Robolink()

    # These are indexes in the Theme dropdown of RoboDK (in case they change)
    themes = {
        0: 'Dark',  # default is dark theme
        1: 'Light',
        2: 'Dark',
        3: 'Windows',
        4: 'Windows XP',
        5: 'Windows Vista',
        6: 'Mac',
        7: 'Fusion',
        8: 'Android',
    }

    theme_idx = RDK.Command('Theme', '')
    return themes[int(theme_idx)]


"""
PySide2 / Qt utilities
"""
if ENABLE_QT:

    def set_qt_theme(app, RDK=None):
        """Set a Qt application theme to match RoboDK's theme."""

        # RoboDK theme : Qt theme
        qt_theme_map = {
            #'Light': None,  # light is default Qt theme
            'Dark': 'Fusion',  # fusion with dark mode
            'Windows': 'Windows',
            'Windows XP': 'windowsxp',
            'Windows Vista': 'windowsvista',
            'Fusion': 'Fusion',
        }

        rdk_theme = get_robodk_theme(RDK)
        qt_themes = QtWidgets.QStyleFactory.keys()

        if rdk_theme in qt_theme_map and qt_theme_map[rdk_theme] in qt_themes:
            qt_theme = qt_theme_map[rdk_theme]
        #elif qt_themes:
        #    qt_theme = qt_themes[0]
        else:
            return

        app.setStyle(QtWidgets.QStyleFactory.create(qt_theme))

        if rdk_theme == 'Dark':
            darkPalette = QtGui.QPalette()
            darkColor = QtGui.QColor(45, 45, 45)
            disabledColor = QtGui.QColor(127, 127, 127)
            darkPalette.setColor(QtGui.QPalette.ColorRole.Window, darkColor)
            darkPalette.setColor(QtGui.QPalette.ColorRole.WindowText, QtGui.QColor("white"))
            darkPalette.setColor(QtGui.QPalette.ColorRole.Base, QtGui.QColor(18, 18, 18))
            darkPalette.setColor(QtGui.QPalette.ColorRole.AlternateBase, darkColor)
            darkPalette.setColor(QtGui.QPalette.ColorRole.ToolTipBase, QtGui.QColor("white"))
            darkPalette.setColor(QtGui.QPalette.ColorRole.ToolTipText, QtGui.QColor("white"))
            darkPalette.setColor(QtGui.QPalette.ColorRole.Text, QtGui.QColor("white"))
            darkPalette.setColor(QtGui.QPalette.ColorGroup.Disabled, QtGui.QPalette.ColorRole.Text, disabledColor)
            darkPalette.setColor(QtGui.QPalette.ColorRole.Button, darkColor)
            darkPalette.setColor(QtGui.QPalette.ColorRole.ButtonText, QtGui.QColor("white"))
            darkPalette.setColor(QtGui.QPalette.ColorGroup.Disabled, QtGui.QPalette.ColorRole.ButtonText, disabledColor)
            darkPalette.setColor(QtGui.QPalette.ColorRole.BrightText, QtGui.QColor("red"))
            darkPalette.setColor(QtGui.QPalette.ColorRole.Link, QtGui.QColor(42, 130, 218))
            darkPalette.setColor(QtGui.QPalette.ColorRole.Highlight, QtGui.QColor(42, 130, 218))
            darkPalette.setColor(QtGui.QPalette.ColorRole.HighlightedText, QtGui.QColor("black"))
            darkPalette.setColor(QtGui.QPalette.ColorGroup.Disabled, QtGui.QPalette.ColorRole.HighlightedText, disabledColor)
            app.setPalette(darkPalette)

    def value_to_qt_widget(value):
        """
        Get a Qt Widget based on a value. For instance, a float into a QDoubleSpinBox, a bool into a QCheckBox.
        Returns a widget and a function to retrieve the widget's value.
        """
        widget = None
        func = []
        value_type = type(value)

        if value_type is float:
            widget = QtWidgets.QDoubleSpinBox()
            import decimal
            decimals = abs(decimal.Decimal(str(value)).as_tuple().exponent)
            widget.setDecimals(max(4, decimals))
            widget.setRange(-9999999., 9999999.)
            widget.setValue(value)
            func = [widget.value]

        elif value_type is int:
            widget = QtWidgets.QSpinBox()
            widget.setRange(-9999999, 9999999)
            widget.setValue(value)
            func = [widget.value]

        elif value_type is str:
            widget = QtWidgets.QLineEdit()
            widget.setText(value)
            func = [widget.text]

        elif value_type is bool:
            widget = QtWidgets.QCheckBox("Activate")
            widget.setChecked(value)
            func = [widget.isChecked]

        # List or tuple of PODs
        elif value_type in [list, tuple] and len(value) > 0 and all(isinstance(n, (float, int, str, bool)) for n in value):
            h_layout = QtWidgets.QHBoxLayout()
            h_layout.setSpacing(0)
            h_layout.setContentsMargins(0, 0, 0, 0)
            for v in value:
                f_widget, f_func = value_to_qt_widget(v)
                func.append(f_func[0])
                h_layout.addWidget(f_widget)
            widget = QtWidgets.QWidget()
            widget.setLayout(h_layout)

        # ComboBox with specified index as int [1, ['First line', 'Second line', 'Third line']]
        elif value_type is list and (len(value) == 2) and isinstance(value[0], int) and all(isinstance(n, str) for n in value[1]):
            index = value[0]
            options = value[1]
            widget = QtWidgets.QComboBox()
            widget.addItems(options)
            widget.setCurrentIndex(index)
            func = [widget.currentIndex]

        # ComboBox with specified index as str ['Second line', ['First line', 'Second line', 'Third line']]
        elif value_type is list and (len(value) == 2) and isinstance(value[0], str) and all(isinstance(n, str) for n in value[1]) and value[0] in value[1]:
            index = value[1].index(value[0])
            options = value[1]
            widget = QtWidgets.QComboBox()
            widget.addItems(options)
            widget.setCurrentIndex(index)
            #widget.itemText(widget.currentIndex)
            func = [widget.currentIndex]  # str index will be replaced with int index once saved

        return widget, func


"""
Tkinter utilities
"""


def value_to_tk_widget(value, frame):
    """
    Get a Tkinter Widget based on a value. For instance, a float into a Spinbox, a bool into a Checkbutton.
    Returns a widget and a function to retrieve the widget's value.
    """
    widget = None
    func = []
    value_type = type(value)

    if value_type is float:
        tkvar = tkinter.DoubleVar(value=value)
        func = [tkvar.get]
        widget = tkinter.Spinbox(frame, from_=-9999999, to=9999999, textvariable=tkvar, format="%.2f")

    elif value_type is int:
        tkvar = tkinter.IntVar(value=value)
        func = [tkvar.get]
        widget = tkinter.Spinbox(frame, from_=-9999999, to=9999999, textvariable=tkvar)

    elif value_type is str:
        tkvar = tkinter.StringVar(value=value)
        func = [tkvar.get]
        widget = tkinter.Entry(frame, textvariable=tkvar)

    elif value_type is bool:
        tkvar = tkinter.BooleanVar(value=value)
        func = [tkvar.get]
        widget = tkinter.Checkbutton(frame, text="Activate", variable=tkvar)

    # List or tuple of PODs
    elif value_type in [list, tuple] and len(value) > 0 and all(isinstance(n, (float, int, str, bool)) for n in value):
        widget = tkinter.Frame(frame)  # simple sub-container
        idcol = -1
        for v in value:
            idcol += 1
            f_widget, f_func = value_to_tk_widget(v, widget)
            f_widget.grid(row=0, column=idcol, sticky=tkinter.NSEW)
            func.append(f_func[0])
            widget.grid_columnconfigure(idcol, weight=1)

    # ComboBox with specified index as int [1, ['First line', 'Second line', 'Third line']]
    elif value_type is list and (len(value) == 2) and isinstance(value[0], int) and all(isinstance(n, str) for n in value[1]):
        index = value[0]
        options = value[1]
        tkvar = tkinter.StringVar(value=options[index])
        widget = tkinter.OptionMenu(frame, tkvar, *options)
        func = [tkvar.get]

    # ComboBox with specified index as str ['Second line', ['First line', 'Second line', 'Third line']]
    elif value_type is list and (len(value) == 2) and isinstance(value[0], str) and all(isinstance(n, str) for n in value[1]) and value[0] in value[1]:
        index = value[0].index(value[0])
        options = value[1]
        tkvar = tkinter.StringVar(value=options[index])
        widget = tkinter.OptionMenu(frame, tkvar, *options)
        func = [tkvar.get]

    return widget, func


class AppSettings:
    """Generic application settings class to save and load settings to a RoboDK station with a built-in UI."""

    def __init__(self, settings_param='App-Settings'):
        self._ATTRIBS_SAVE = None
        self._FIELDS_UI = None
        self._SETTINGS_PARAM = settings_param

        self._UI_READ_FIELDS = None
        self._UI_RELOAD_FIELDS = None

    def CopyFrom(self, other):
        """Copy settings from another instance"""
        attr = self.getAttribs()
        for a in attr:
            if hasattr(other, a):
                setattr(self, a, getattr(other, a))

    def SetDefaults(self):
        # List untouched variables for default settings
        list_untouched = []

        # save in local variables
        for var in list_untouched:
            exec('%s=self.%s' % (var, var))

        defaults = type(self)()
        self.CopyFrom(defaults)

        # restore from local vars
        for var in list_untouched:
            exec('self.%s=%s' % (var, var))

    def getAttribs(self):
        """Get the list of attributes"""
        return [a for a in dir(self) if (not callable(getattr(self, a)) and not a.startswith("_"))]

    def _getAttribsSave(self):
        """Get list of attributes to save (list of strings)"""
        if type(self._ATTRIBS_SAVE) is list:
            return self._ATTRIBS_SAVE
        return self.getAttribs()

    def _getFieldsUI(self):
        """Get dictionary fields to be displayed in the UI"""
        from collections import OrderedDict
        if type(self._FIELDS_UI) is dict or type(self._FIELDS_UI) is OrderedDict:
            return self._FIELDS_UI

        attribs = None
        if type(self._FIELDS_UI) is list:
            attribs = self._FIELDS_UI
        else:
            attribs = self.getAttribs()

        fields = OrderedDict()
        for a in attribs:
            fields[a] = a.replace('_', ' ')

        return fields

    def get(self, attrib, default_value=None):
        """Get attribute value by key, otherwise it returns None"""
        if hasattr(self, attrib):
            return getattr(self, attrib)
        return default_value

    def Save(self, rdk=None, autorecover=False):
        """Save the class attributes as a RoboDK binary parameter"""
        # Save the class attributes as a string
        # Use a dictionary and the str/eval buit-in conversion
        attribs_list = self._getAttribsSave()
        if len(attribs_list) <= 0:
            print("Saving skipped")
            return

        print("Saving data to RoboDK station...")
        dict_data = {}

        # Important! We must save this but not show it in the UI
        for key in attribs_list:
            dict_data[key] = getattr(self, key)

        # Protocol tips: https://docs.python.org/3/library/pickle.html
        import pickle
        bytes_data = pickle.dumps(dict_data, protocol=2)  # protocol=2: bynary, compatible with python 2.3 and later
        if rdk is None:
            from robodk.robolink import Robolink
            rdk = Robolink()

        param_val = self._SETTINGS_PARAM
        param_backup = param_val + "-Backup"

        if autorecover:
            rdk.setParam(param_backup, bytes_data)

        else:
            rdk.setParam(param_val, bytes_data)
            rdk.setParam(param_backup, b'')

    def Load(self, rdk=None):  #, stream_data=b''):
        """Load the class attributes from a RoboDK binary parameter"""
        # Use a dictionary and the str/eval buit-in conversion
        attribs_list = self._getAttribsSave()
        #if len(attribs_list) == 0:
        #    print("Load settings: No attributes to load")
        #    return False

        print("Loading data from RoboDK station...")
        if rdk is None:
            from robodk.robolink import Robolink
            rdk = Robolink()

        param_backup = self._SETTINGS_PARAM
        param_backup += "-Backup"

        bytes_data = rdk.getParam(param_backup, False)
        if len(bytes_data) > 0:
            from robodk.robodialogs import ShowMessageYesNoCancel
            result = ShowMessageYesNoCancel("Something went wrong with the last settings.\nRecover lost data?", "Auto recover")
            if result is None:
                return False

            elif not result:
                bytes_data = b''

            # Clear backup data
            rdk.setParam(param_backup, b'', False)

        if len(bytes_data) <= 0:
            bytes_data = rdk.getParam(self._SETTINGS_PARAM, False)

        if len(bytes_data) <= 0:
            print("Load settings: No data for " + self._SETTINGS_PARAM)
            return False

        import pickle
        saved_dict = pickle.loads(bytes_data)
        for key in saved_dict.keys():
            if key == '_FIELDS_UI':
                continue

            # if we have a list of attributes that we want, load it only if it is in the list
            if len(attribs_list) == 0 or (key not in attribs_list and key != '_FIELDS_UI'):
                print("Obsolete variable saved (will be deleted): " + key)

            else:
                value = saved_dict[key]
                setattr(self, key, value)

        return True

    def ShowUI(self, windowtitle='Settings', embed=False, wparent=None, callback_frame=None, show_default_button=False):
        """Show the Apps Settings in a GUI, using tkinter or Qt depending on availability."""
        if ENABLE_QT:
            self.__ShowUIPyQt(windowtitle, embed, wparent, callback_frame, show_default_button)
        else:
            self.__ShowUITkinter(windowtitle, embed, wparent, callback_frame, show_default_button)

    def __ShowUIPyQt(self, windowtitle='Settings', embed=False, wparent=None, callback_frame=None, show_default_button=False):
        """Open settings window"""

        from PySide2 import QtCore, QtGui, QtWidgets

        app = QtWidgets.QApplication.instance()
        if app is None:
            app = QtWidgets.QApplication([])  # No need to create a new one

        layoutQtWidgetGrid = QtWidgets.QVBoxLayout()
        layoutQtWidgetGrid.setContentsMargins(10, 10, 10, 10)

        content = QtWidgets.QWidget()
        big_form = QtWidgets.QFormLayout(content)
        big_form.setVerticalSpacing(1)
        big_form.setHorizontalSpacing(15)
        big_form.setSizeConstraint(QtWidgets.QLayout.SizeConstraint.SetMinimumSize)

        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(content)
        layoutQtWidgetGrid.addWidget(scroll)

        windowQt = QtWidgets.QWidget(wparent)
        windowQt.setLayout(layoutQtWidgetGrid)

        obj = self
        TEMP_ENTRIES = {}

        def add_fields():
            """Creates the UI from the field stored in the variable"""

            for fkey, field in self._getFieldsUI().items():
                # Iterate for each key and add the variable to the UI
                if not field is list:
                    field = [field]

                fname = field[0]
                is_section = fname.endswith('$') and fname.startswith('$')
                fvalue = fname if is_section else getattr(self, fkey)
                ftype = type(fvalue)

                # Convert None to double
                if ftype is None:
                    ftype = float
                    fvalue = -1.0

                print(fkey + ' = ' + str(fvalue))

                if is_section:
                    # Section seperator
                    widget = QtWidgets.QLabel()
                    widget.setText(f'[  {fname[1:-1]}  ]'.upper())
                    widget.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignBottom)
                    widget.adjustSize()
                    if big_form.rowCount() > 0:
                        widget.setMinimumHeight(widget.height() * 1.75)
                    big_form.addRow(widget)
                    continue

                widget, func = value_to_qt_widget(fvalue)
                if widget is not None:
                    big_form.addRow(QtWidgets.QLabel(fname), widget)
                    TEMP_ENTRIES[fkey] = (field, func)
                else:
                    big_form.addRow(QtWidgets.QLabel(fname), QtWidgets.QLabel('Unsupported'))

        def read_fields():
            print("Values entered:")
            for fkey in TEMP_ENTRIES:
                entry = TEMP_ENTRIES[fkey]
                funcs = entry[1]
                values = [value() for value in funcs]  # tuple needs to be casted below

                for value in values:
                    if type(value) == str:
                        value = value.strip()

                if len(values) == 1:
                    values = values[0]

                # Comboboxes
                last_value = getattr(obj, fkey)
                if (type(last_value) is list) and (len(last_value) == 2) and isinstance(last_value[0], (int, str)) and isinstance(last_value[1], list) and all(isinstance(n, str) for n in last_value[1]):
                    newvalue = last_value
                    newvalue[0] = value
                    values = newvalue

                # Tuples
                if type(last_value) is tuple:
                    values = tuple(values)

                if type(last_value) != type(values):
                    print('Warning! Type change detected (old:new): %s:%s' % (str(last_value), str(values)))
                    new_type = type(last_value)
                    values = new_type(values)
                print(fkey + " = " + str(values))
                setattr(obj, fkey, values)

        def command_ok():
            read_fields()
            self.Save()
            command_quit()

        def command_cancel():
            r = QtWidgets.QMessageBox.warning(windowQt, "Save settings?", "Do you want to save the current settings before closing?", QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No)
            if r == QtWidgets.QMessageBox.StandardButton.Yes:
                read_fields()
                self.Save()
            command_quit()

        def command_defaults():
            r = QtWidgets.QMessageBox.warning(windowQt, "Apply default settings?", "Do you want to discard the current settings and load the default settings?", QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No)
            if r == QtWidgets.QMessageBox.StandardButton.Yes:
                while big_form.rowCount():
                    big_form.removeRow(0)
                self.SetDefaults()
                add_fields()

        def command_reload():
            while big_form.rowCount():
                big_form.removeRow(0)
            add_fields()

        def command_quit():
            self._UI_READ_FIELDS = None
            self._UI_RELOAD_FIELDS = None
            windowQt.window().close()

        add_fields()

        self._UI_READ_FIELDS = read_fields
        self._UI_RELOAD_FIELDS = command_reload

        if callback_frame is not None:
            callback_frame(windowQt)

        if show_default_button:
            buttonDefaults = QtWidgets.QPushButton('Set defaults')
            buttonDefaults.clicked.connect(command_defaults)
            layoutQtWidgetGrid.addWidget(buttonDefaults)

        # Creating the Cancel button
        buttonCancel = QtWidgets.QPushButton(windowQt)
        buttonCancel.setText("Discard")
        buttonCancel.clicked.connect(command_cancel)

        # Creating the OK button
        buttonOk = QtWidgets.QPushButton(windowQt)
        buttonOk.setText('Save')
        buttonOk.clicked.connect(command_ok)

        OkCancelLayout = QtWidgets.QHBoxLayout()
        OkCancelLayout.addWidget(buttonOk)
        OkCancelLayout.addWidget(buttonCancel)
        layoutQtWidgetGrid.addLayout(OkCancelLayout)

        import os
        from robodk.robolink import getPathIcon
        iconpath = getPathIcon()
        if os.path.exists(iconpath):
            windowQt.setWindowIcon(QtGui.QIcon(iconpath))

        # Set the window style
        set_qt_theme(app)

        # Important! Ensures we apply the theme and resize the window correctly
        windowQt.update()
        content.adjustSize()
        scroll.setMinimumWidth(min(900, content.minimumWidth() + 20))
        windowQt.adjustSize()

        if embed:
            # Embed the window in RoboDK
            mainWindow = QtWidgets.QMainWindow()
            mainWindow.setCentralWidget(windowQt)
            mainWindow.setWindowTitle(windowtitle)
            mainWindow.update()
            mainWindow.show()

            from robodk.robolink import EmbedWindow
            EmbedWindow(windowtitle)
        else:
            windowQt.setWindowTitle(windowtitle)
            windowQt.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

        if wparent is None:
            # Important for unchecking the action in RoboDK
            app.lastWindowClosed.connect(command_quit)
            windowQt.show()
            app.exec_()

    def __ShowUITkinter(self, windowtitle='Settings', embed=False, wparent=None, callback_frame=None, show_default_button=False):
        """Open settings window using tkinter"""

        import sys
        if sys.version_info[0] < 3:
            # Python 2.X only:
            import Tkinter as tkinter
        else:
            # Python 3.x only
            import tkinter

        windowTk = None
        if wparent is not None:
            windowTk = tkinter.Toplevel(wparent)
        else:
            windowTk = tkinter.Tk()

        frame = tkinter.Frame(windowTk)

        obj = self
        TEMP_ENTRIES = {}

        def add_fields():
            """Creates the UI from the field stored in the variable"""
            sticky = tkinter.NSEW
            idrow = -1

            for fkey, field in self._getFieldsUI().items():
                idrow += 1

                # Iterate for each key and add the variable to the UI
                if not field is list:
                    field = [field]

                fname = field[0]
                if not hasattr(self, fkey):
                    continue
                fvalue = getattr(self, fkey)
                ftype = type(fvalue)

                # Convert None to double
                if ftype is None:
                    ftype = float
                    fvalue = -1.0

                print(fkey + ' = ' + str(fvalue))

                if fname.endswith('$') and fname.startswith('$'):
                    # Section seperator
                    widget = tkinter.Label(frame, text=f'[  {fname[1:-1]}  ]'.upper(), anchor='w')
                    widget.grid(row=idrow, columnspan=2, sticky=sticky)
                    continue

                widget, func = value_to_tk_widget(fvalue, frame)
                label_name = tkinter.Label(frame, text=fname, anchor='w')
                label_name.grid(row=idrow, column=0, sticky=sticky)

                if widget is not None:
                    _sticky = sticky
                    if type(widget) is tkinter.Checkbutton:
                        _sticky = tkinter.W
                    widget.grid(row=idrow, column=1, sticky=_sticky)

                    TEMP_ENTRIES[fkey] = (field, func)
                else:
                    label_unsupported = tkinter.Label(frame, text='Unsupported')
                    label_unsupported.grid(row=idrow, column=1, sticky=sticky)

                frame.grid_rowconfigure(idrow, weight=1)
                frame.grid_columnconfigure(0, weight=1)
                frame.grid_columnconfigure(1, weight=1)

            frame.pack(side=tkinter.TOP, fill=tkinter.X, padx=1, pady=1)

        def read_fields():
            print("Values entered:")
            for fkey in TEMP_ENTRIES:
                entry = TEMP_ENTRIES[fkey]
                funcs = entry[1]
                values = [value() for value in funcs]  # tuple needs to be casted below

                for value in values:
                    if type(value) == str:
                        value = value.strip()

                if len(values) == 1:
                    values = values[0]

                # Comboboxes
                last_value = getattr(obj, fkey)
                if (type(last_value) is list) and (len(last_value) == 2) and isinstance(last_value[0], (int, str)) and all(isinstance(n, str) for n in last_value[1]):
                    newvalue = last_value
                    newvalue[0] = value
                    values = newvalue

                # Tuples
                if type(last_value) is tuple:
                    values = tuple(values)

                if type(last_value) != type(values):
                    print('Warning! Type change detected (old:new): %s:%s' % (str(last_value), str(values)))
                    new_type = type(last_value)
                    values = new_type(values)
                print(fkey + " = " + str(values))
                setattr(obj, fkey, values)

        def command_ok():
            read_fields()
            self.Save()
            command_quit()

        def command_cancel():
            r = tkinter.messagebox.askyesno("Save settings?", "Do you want to save the current settings before closing?")
            if r:
                read_fields()
                self.Save()
            command_quit()

        def command_defaults():
            r = tkinter.messagebox.askyesno("Apply default settings?", "Do you want to discard the current settings and load the default settings?")
            if r:
                for widget in frame.winfo_children():
                    widget.destroy()
                self.SetDefaults()
                add_fields()

        def command_reload():
            for widget in frame.winfo_children():
                widget.destroy()
            add_fields()

        def command_quit():
            self._UI_READ_FIELDS = None
            self._UI_RELOAD_FIELDS = None
            windowTk.destroy()

        add_fields()

        self._UI_READ_FIELDS = read_fields
        self._UI_RELOAD_FIELDS = command_reload

        # Everything after the callframe will be added after whatever is added to the frame
        if callback_frame is not None:
            callback_frame(windowTk)

        row = tkinter.Frame(windowTk)
        id_row = 0
        if show_default_button:
            b_defaults = tkinter.Button(row, text='Set defaults', command=command_defaults)
            b_defaults.grid(row=id_row, column=0, columnspan=2, sticky=tkinter.NSEW)
            id_row += 1

        # Creating the Cancel button
        b_cancel = tkinter.Button(row, text='Discard', command=command_cancel)
        b_cancel.grid(row=id_row, column=1, sticky=tkinter.NSEW)

        # Creating the OK button
        b_ok = tkinter.Button(row, text='Save', command=command_ok)
        b_ok.grid(row=id_row, column=0, sticky=tkinter.NSEW)

        row.grid_columnconfigure(0, weight=1)
        row.grid_columnconfigure(1, weight=1)
        row.pack(side=tkinter.BOTTOM, fill=tkinter.X, padx=5, pady=5)

        windowTk.title(windowtitle)

        import os
        from robodk.robolink import getPathIcon

        iconpath = getPathIcon()
        if os.path.exists(iconpath):
            windowTk.iconbitmap(iconpath)

        # Embed the window in RoboDK
        if embed:
            from robodk.robolink import EmbedWindow
            EmbedWindow(windowtitle)
        else:
            # If not, make sure to make the window stay on top
            windowTk.attributes("-topmost", True)

        if wparent is None:
            # Important for unchecking the action in RoboDK
            windowTk.protocol("WM_DELETE_WINDOW", command_quit)
            windowTk.mainloop()

        else:
            print("Settings window: using parent loop")


def runmain():
    #------------------------------------------------------------------------
    # Using custom call backs with SettingsExample
    class SettingsExample(AppSettings):
        """Example of AppSettings using custom call backs"""

        # List the variable names you would like to save and their default values.
        # Variables that start with underscore (_) will not be saved.
        # Important: Try to avoid default None type!!
        # If None is used as default value it will attempt to treat it as a float and None = -1
        Boolean = True
        Int_Value = 123456
        Float_Value = 0.123456789
        String_Value = 'String test'
        Int_List = [1, 2, 3]  # 3 numbers minimum!
        Float_List = [1.0, 2.0, 3.0]  # 3 numbers minimum!
        String_List = ['First line', 'Second line', 'Third line']
        Mixed_List = [False, 1, '2']
        Int_Tuple = (1, 2, 3)
        Dropdown = ['Second line', ['First line', 'Second line', 'Third line']]
        Dropdown2 = [1, ['First line', 'Second line', 'Third line']]
        Unsupported = {}
        _HiddenUnsavedBool = True
        HiddenSavedBool = True

        # Variable names when displayed on the user interface (detailed descriptions).
        # Create this dictionary in the same order that you want to display it.
        # If AppSettings._FIELDS_UI is not provided, all variables of this class will be used and displayed as is (unless they start with '_').
        # Fields within dollar signs (i.e. $abc$) are used as section headers.
        from collections import OrderedDict
        __FIELDS_UI = OrderedDict()
        __FIELDS_UI['Section'] = '$This is a section$'
        __FIELDS_UI['Boolean'] = 'This is a bool'
        __FIELDS_UI['Int_Value'] = 'This is an int'
        __FIELDS_UI['Float_Value'] = 'This is a float'
        __FIELDS_UI['String_Value'] = 'This is a string'
        __FIELDS_UI['Int_List'] = 'This is an int list'
        __FIELDS_UI['Float_List'] = 'This is a float list'
        __FIELDS_UI['String_List'] = 'This is a string list'
        __FIELDS_UI['Mixed_List'] = 'This is a mixed list'
        __FIELDS_UI['Int_Tuple'] = 'This is an int tuple'
        __FIELDS_UI['Dropdown'] = 'This is a dropdown'
        __FIELDS_UI['Dropdown2'] = 'This is a dropdown too'
        __FIELDS_UI['Unsupported'] = 'This is unsupported'

        def __init__(self, settings_param='App-Settings'):
            # customize the initialization section if needed
            super(SettingsExample, self).__init__(settings_param=settings_param)
            self._FIELDS_UI = self.__FIELDS_UI

        def ShowUI(self, windowtitle='Settings', embed=False, wparent=None, callback_frame=None, show_default_button=False):
            # Show the UI for these settings including a custom frame with utility functions

            def showMessage():
                from robodk import robodialogs
                if robodialogs.ShowMessageYesNo('Toggle "This is a bool"?'):
                    self._UI_READ_FIELDS()  # Ensure we read the UI fields to have the latest value
                    self.Boolean = not self.Boolean
                    self._UI_RELOAD_FIELDS()  # Reload the UI fields with the latest changes

            def openFolder():
                from robodk import robodialogs
                r = robodialogs.getOpenFolder(strtitle='Open a folder and store its path to "This is a string"')
                if r:
                    self._UI_READ_FIELDS()  # Ensure we read the UI fields to have the latest value
                    self.String_Value = r
                    self._UI_RELOAD_FIELDS()  # Reload the UI fields with the latest changes

            def itemPick():
                from robodk.robolink import Robolink
                item = Robolink().ItemUserPick('Select an Item and store it to "This is a string"')
                if item.Valid():
                    self._UI_READ_FIELDS()  # Ensure we read the UI fields to have the latest value
                    self.String_Value = item.Name()
                    self._UI_RELOAD_FIELDS()  # Reload the UI fields with the latest changes

            if not ENABLE_QT:

                def custom_frame(w):

                    sticky = tkinter.NSEW
                    frame = tkinter.LabelFrame(w)

                    label = tkinter.Label(frame, text=f"This a custom callback frame for {self._SETTINGS_PARAM}.", anchor='w')
                    label.grid(row=0, column=0, sticky=sticky)

                    customButton0 = tkinter.Button(frame, text="Show a Yes/No Message", command=showMessage)
                    customButton1 = tkinter.Button(frame, text="Open a folder", command=openFolder)
                    customButton2 = tkinter.Button(frame, text="Pick an Item", command=itemPick)
                    customButton0.grid(row=1, column=0, sticky=sticky)
                    customButton1.grid(row=2, column=0, sticky=sticky)
                    customButton2.grid(row=3, column=0, sticky=sticky)

                    frame.grid_columnconfigure(0, weight=1)
                    frame.pack(side=tkinter.TOP, fill=tkinter.X, padx=5, pady=5)

            else:

                def custom_frame(w: QtWidgets.QWidget):

                    grpBox = QtWidgets.QGroupBox()
                    vLayout = QtWidgets.QVBoxLayout(grpBox)
                    vLayout.addWidget(QtWidgets.QLabel(f"This a custom callback frame for {self._SETTINGS_PARAM}."))

                    customButton0 = QtWidgets.QPushButton("Show a Yes/No Message")
                    customButton0.clicked.connect(showMessage)
                    customButton1 = QtWidgets.QPushButton("Open a folder")
                    customButton1.clicked.connect(openFolder)
                    customButton2 = QtWidgets.QPushButton("Pick an Item")
                    customButton2.clicked.connect(itemPick)

                    vLayout.addWidget(customButton0)
                    vLayout.addWidget(customButton1)
                    vLayout.addWidget(customButton2)

                    layout = w.layout()
                    layout.addWidget(grpBox)

            super(SettingsExample, self).ShowUI(windowtitle=windowtitle, embed=embed, wparent=wparent, callback_frame=custom_frame, show_default_button=show_default_button)

    #------------------------------------------------------------------------
    S = SettingsExample(settings_param='S Settings')
    #S.Load()
    print('S._HiddenUnsavedBool: ' + str(S._HiddenUnsavedBool))
    print('S.HiddenSavedBool: ' + str(S.HiddenSavedBool))
    S.ShowUI(show_default_button=True)
    S._HiddenUnsavedBool = not S._HiddenUnsavedBool
    S.HiddenSavedBool = not S.HiddenSavedBool
    S.Save()

    #------------------------------------------------------------------------
    # Using the AppSettings as is
    A = AppSettings(settings_param='A Settings')

    # List the variable names you would like to save and their default values.
    # Variables that start with underscore (_) will not be saved.
    # Important: Try to avoid default None type!!
    # If None is used as default value it will attempt to treat it as a float and None = -1
    A.Boolean = True
    A.Int_Value = 123456
    A.Float_Value = 0.123456789
    A.String_Value = 'String test'
    A.Int_List = [1, 2, 3]  # 3 numbers minimum!
    A.Float_List = [1.0, 2.0, 3.0]  # 3 numbers minimum!
    A.String_List = ['First line', 'Second line', 'Third line']
    A.Mixed_List = [False, 1, '2']
    A.Int_Tuple = (1, 2, 3)
    A.Dropdown = ['Second line', ['First line', 'Second line', 'Third line']]
    A.Dropdown2 = [1, ['First line', 'Second line', 'Third line']]
    A.Unsupported = {}
    A._HiddenUnsavedBool = True
    A.HiddenSavedBool = True

    # Variable names when displayed on the user interface (detailed descriptions).
    # Create this dictionary in the same order that you want to display it.
    # If AppSettings._FIELDS_UI is not provided, all variables of this class will be used and displayed as is (unless they start with '_').
    # Fields within dollar signs (i.e. $abc$) are used as section headers.
    from collections import OrderedDict
    A._FIELDS_UI = OrderedDict()
    A._FIELDS_UI['Section'] = '$This is a section$'
    A._FIELDS_UI['Boolean'] = 'This is a bool'
    A._FIELDS_UI['Int_Value'] = 'This is an int'
    A._FIELDS_UI['Float_Value'] = 'This is a float'
    A._FIELDS_UI['String_Value'] = 'This is a string'
    A._FIELDS_UI['Float_List'] = 'This is a float list'
    A._FIELDS_UI['Int_List'] = 'This is an int list'
    A._FIELDS_UI['String_List'] = 'This is a string list'
    A._FIELDS_UI['Mixed_List'] = 'This is a mixed list'
    A._FIELDS_UI['Int_Tuple'] = 'This is an int tuple'
    A._FIELDS_UI['Dropdown'] = 'This is a dropdown'
    A._FIELDS_UI['Dropdown2'] = 'This is a dropdown too'
    A._FIELDS_UI['Unsupported'] = 'This is unsupported'

    #A.Load()
    print('A._HiddenUnsavedBool: ' + str(A._HiddenUnsavedBool))
    print('A.HiddenSavedBool: ' + str(A.HiddenSavedBool))
    A.ShowUI(show_default_button=True)
    A._HiddenUnsavedBool = not A._HiddenUnsavedBool
    A.HiddenSavedBool = not A.HiddenSavedBool
    A.Save()


if __name__ == "__main__":
    runmain()
