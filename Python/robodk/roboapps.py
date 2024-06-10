# Copyright 2015-2024 - RoboDK Inc. - https://robodk.com/
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
"""This module is a toolbox for RoboDK Add-ins and the RoboDK API for Python.
This toolbox helps create checkable actions in RoboDK Add-ins, automatic Add-in settings UI, etc.

More information about the RoboDK API for Python here:

* https://robodk.com/doc/en/RoboDK-API.html
* https://robodk.com/doc/en/PythonAPI/index.html
* https://robodk.com/doc/en/PythonAPI/robodk.html#roboapps-py
* https://robodk.com/doc/en/Add-ins.html
"""
# --------------------------------------------
import sys
import time
from robodk import robodialogs, robolink

if sys.version_info.major >= 3 and sys.version_info.minor >= 5:
    # Python 3.5+ type hints. Type hints are stripped for <3.5
    from typing import List, Union, Any, Tuple, Dict

if robodialogs.ENABLE_QT:
    from PySide2 import QtWidgets, QtCore, QtGui

if robodialogs.ENABLE_TK:
    if sys.version_info[0] < 3:
        import Tkinter as tkinter
        import tkFileDialog as filedialog
        import tkMessageBox as messagebox
    else:
        import tkinter
        from tkinter import filedialog
        from tkinter import messagebox
"""
App/actions control utilities.

Use these to control your App's actions: run on click, run while checked, do not kill, etc.
"""


class RunApplication:
    """
    Class to detect when the terminate signal is emitted to stop an action.

    .. code-block:: python

        RUN = RunApplication()
        while RUN.Run():
            # your main loop to run until the terminate signal is detected
            ...

    """
    time_last = -1
    param_name = None
    RDK = None

    def __init__(self, rdk: robolink.Robolink = None):
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

    def Run(self) -> bool:
        """
        Run callback.

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


def Unchecked() -> bool:
    """
    Verify if the command "Unchecked" is present. In this case it means the action was just unchecked from RoboDK (applicable to checkable actions only).

    Example for a 'Checkable Action':

    .. code-block:: python

        def runmain():
            if roboapps.Unchecked():
                ActionUnchecked()
            else:
                roboapps.SkipKill()  # Optional, prevents RoboDK from force-killing the action after 2 seconds
                ActionChecked()

    .. seealso:: :func:`~robodk.roboapps.Checked`, :func:`~robodk.roboapps.SkipKill`, :func:`~robodk.roboapps.KeepChecked`
    """
    if len(sys.argv) >= 2:
        if "Unchecked" in sys.argv[1:]:
            return True

    return False


def Checked() -> bool:
    """
    Verify if the command "Checked" is present. In this case it means the action was just checked from RoboDK (applicable to checkable actions only).

    Example for a 'Checkable Action':

    .. code-block:: python

        def runmain():
            if roboapps.Unchecked():
                ActionUnchecked()
            else:
                roboapps.SkipKill()  # Optional, prevents RoboDK from force-killing the action after 2 seconds
                ActionChecked()

    .. seealso:: :func:`~robodk.roboapps.Unchecked`, :func:`~robodk.roboapps.SkipKill`, :func:`~robodk.roboapps.KeepChecked`
    """
    if len(sys.argv) >= 2:
        if "Checked" in sys.argv[1:]:
            return True

    return False


def KeepChecked():
    """
    Keep an action checked even if the execution of the script completed (applicable to checkable actions only).

    Example for a 'Checkable Option':

    .. code-block:: python

        def runmain():
            if roboapps.Unchecked():
                ActionUnchecked()
            else:
                roboapps.KeepChecked()  # Important, prevents RoboDK from unchecking the action after it has completed
                ActionChecked()

    .. seealso:: :func:`~robodk.roboapps.Unchecked`, :func:`~robodk.roboapps.SkipKill`, :func:`~robodk.roboapps.KeepChecked`
    """
    print("App Setting: Keep checked")
    sys.stdout.flush()


def SkipKill():
    """
    For Checkable actions, this setting will tell RoboDK App loader to not kill the process a few seconds after the terminate function is called.
    This is needed if we want the user input to save the file. For example: The Record action from the Record App.

    Example for a 'Momentary Action':

    .. code-block:: python

        def runmain():
            if roboapps.Unchecked():
                roboapps.Exit()  # or sys.exit()
            else:
                roboapps.SkipKill()  # Optional, prevents RoboDK from force-killing the action after 2 seconds
                ActionChecked()

    .. seealso:: :func:`~robodk.roboapps.Unchecked`, :func:`~robodk.roboapps.Checked`, :func:`~robodk.roboapps.KeepChecked`
    """
    print("App Setting: Skip kill")
    sys.stdout.flush()


def Exit(exit_code: int = 0):
    """
    Exit/close the action gracefully. If an error code is provided, RoboDK will display a trace to the user.
    """
    sys.exit(exit_code)


"""
General utilities
"""


def Str2FloatList(str_values: str, expected_nvalues: int = 3) -> List[float]:
    """
    Convert a string into a list of floats. It returns None if the array is smaller than the expected size.

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


def Registry(varname: str, setvalue: str = None):
    """
    Read value from the registry or set a value. It will do so at HKEY_CURRENT_USER so no admin rights required.
    """
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


def value_to_widget(value: Any, parent: Any) -> Any:
    """
    Convert a value to a widget (Tkinter or Qt).

    The widget is automatically created for supported types:
    - Base types: bool, int, float, str
    - list or tuple of base types
    - dropdown formatted as [int, [str, str, ...]]. e.g. [1, ['Option #1', 'Option #2']] where 1 means the default selected option is Option #2.
    - dictionary of supported types, where the key is the field's label. e.g. {'This is a bool!' : True}.

    :param value: The value to convert as a widget, and the initial value of the widget
    :type value: see supported types
    :param parent: Parent of the widget (Qt/Tkinter)

    :return: (widget, funcs) the widget, and a list of 'get' functions to retrieve the value of the widget
    :rtype: tuple of widget (Qt/Tkinter), callable

    .. seealso:: :func:`~robodk.roboapps.widget_to_value`
    """
    if robodialogs.ENABLE_QT:
        return value_to_qt_widget(value, parent)
    else:
        return value_to_tk_widget(value, parent)


def widget_to_value(funcs: List, original_value: Any) -> Any:
    """
    Retrieve the value from a widget's list of get functions.
    The original value is required to recreate the original format.

    :param funcs: list of get functions, see :func:`~robodk.roboapps.value_to_widget`
    :type funcs: list of callable
    :param original_value: The original value, see :func:`~robodk.roboapps.value_to_widget`

    :return: The value

    .. seealso:: :func:`~robodk.roboapps.value_to_widget`
    """
    value_list = [func() if callable(func) else func for func in funcs]

    def is_pod(value):
        # Plain old data (POD)
        return isinstance(value, (float, int, str, bool))

    def is_pod_list(value):
        # List or tuple of PODs
        if isinstance(value, list) and len(value) > 0 and all(is_pod(n) for n in value):
            return True
        return False

    def is_pod_tuple(value):
        # List or tuple of PODs
        if isinstance(value, tuple) and len(value) > 0 and all(is_pod(n) for n in value):
            return True
        return False

    def is_dropdown(value):
        # Dropdown with specified index as int [1, ['First line', 'Second line', 'Third line']] # NOTE: Removed the "value[0] in range(len(value[1]))" check, as developer can remove choices
        # Dropdown with specified index as str ['Second line', ['First line', 'Second line', 'Third line']] # NOTE: Removed the "value[0] in value[1]" check, as developer can remove choices
        if type(value) is list and (len(value) == 2) and isinstance(value[0], (int, str)) and isinstance(value[1], list) and all(isinstance(n, str) for n in value[1]):
            return True

        return False

    def is_pod_dict(value):
        # Dictionary of supported types, does not supported nested dictionaries
        if isinstance(value, dict):
            if len(value.keys()) > 0:
                if all(is_pod(n) or is_pod_list(n) or is_pod_tuple(n) or is_dropdown(n) for n in value.values()):
                    return True
        return False

    if is_pod(original_value):
        return value_list[0]

    elif is_pod_list(original_value):
        return list(value_list)

    elif is_pod_tuple(original_value):
        return tuple(value_list)

    elif is_dropdown(original_value):
        new_value = original_value
        new_value[0] = value_list[0]
        return new_value

    elif isinstance(original_value, dict):

        def parse_dict(original_value, value_list):
            new_value = original_value
            for key, old_value in original_value.items():
                if is_pod(old_value):
                    new_value[key] = value_list[0]
                    value_list.pop(0)

                elif is_pod_list(old_value):
                    new_value[key] = value_list[0:len(old_value)]
                    value_list = value_list[len(old_value):]

                elif is_pod_tuple(old_value):
                    new_value[key] = tuple(value_list[0:len(old_value)])
                    value_list = value_list[len(old_value):]

                elif is_dropdown(old_value):
                    new_value[key] = old_value
                    new_value[key][0] = value_list[0]
                    value_list.pop(0)

                elif is_pod_dict(old_value):
                    new_value[key] = parse_dict(old_value, value_list)

            return new_value

        return parse_dict(original_value, value_list)

    return value_list


def get_robodk_theme(RDK: robolink.Robolink = None) -> str:
    """
    Get RoboDK's active theme (Options->General->Theme)
    """
    if RDK is None:
        from robodk.robolink import Robolink
        RDK = Robolink()

    # These are indexes in the Theme dropdown of RoboDK (in case they change)
    themes = {
        0: 'Light',  # default is OS based
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

if robodialogs.ENABLE_QT:

    def get_qt_app(robodk_icon: bool = True, robodk_theme: bool = True, RDK: robolink.Robolink = None) -> QtWidgets.QApplication:
        """
        Get the QApplication instance.

        Note: If RoboDK is not running, The RoboDK theme is not applied.

        :param robodk_icon: Applies the RoboDK logo, defaults to True
        :type robodk_icon: bool
        :param robodk_theme: Applies the current RoboDK theme, defaults to True
        :type robodk_theme: bool
        :param RDK: Link to the running RoboDK instance for the theme, defaults to None
        :type RDK: robolink.Robolink

        :return: The QApplication instance
        :rtype: :class:`PySide2.QtWidgets.QApplication`
        """

        app = QtWidgets.QApplication.instance()
        if app is None:
            QtWidgets.QApplication.setAttribute(QtCore.Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
            QtWidgets.QApplication.setAttribute(QtCore.Qt.ApplicationAttribute.AA_DisableWindowContextHelpButton, True)
            app = QtWidgets.QApplication([])

        if robodk_icon:
            from robodk import robolink
            icon_path = robolink.getPathIcon()
            from os import path
            if path.exists(icon_path):
                if sys.platform.startswith('win'):
                    import ctypes
                    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(str(app))  # Enable the taskbar icon
                app_icon = QtGui.QIcon(icon_path)
                app.setWindowIcon(app_icon)

        if robodk_theme:
            if RDK is None:
                RDK = robolink.Robolink(robodk_path='')  # If no running instance of RoboDK is found, do not instantiate RoboDK
            try:
                if RDK._is_connected():
                    set_qt_theme(app, RDK)
            except:
                pass

        return app

    def set_qt_theme(app: QtWidgets.QApplication, RDK: robolink.Robolink = None):
        """Set a Qt application theme to match RoboDK's theme.

        :param app: The QApplication
        :type app: :class:`PySide2.QtWidgets.QApplication`
        """
        # RoboDK theme : Qt theme
        qt_theme_map = {
            #'Light': None,  # light is default Qt theme
            'Dark': 'Fusion',
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
            darkPalette.setColor(QtGui.QPalette.ColorRole.ToolTipBase, QtGui.QColor("black"))
            darkPalette.setColor(QtGui.QPalette.ColorRole.ToolTipText, QtGui.QColor("white"))
            darkPalette.setColor(QtGui.QPalette.ColorRole.Text, QtGui.QColor("white"))
            darkPalette.setColor(QtGui.QPalette.ColorRole.BrightText, QtGui.QColor("white"))
            darkPalette.setColor(QtGui.QPalette.ColorRole.Button, darkColor)
            darkPalette.setColor(QtGui.QPalette.ColorRole.ButtonText, QtGui.QColor("white"))
            darkPalette.setColor(QtGui.QPalette.ColorRole.Link, QtGui.QColor(42, 130, 218))
            darkPalette.setColor(QtGui.QPalette.ColorRole.Highlight, QtGui.QColor(42, 130, 218))
            darkPalette.setColor(QtGui.QPalette.ColorRole.HighlightedText, QtGui.QColor("black"))

            darkPalette.setColor(QtGui.QPalette.ColorGroup.Disabled, QtGui.QPalette.ColorRole.Text, disabledColor)
            darkPalette.setColor(QtGui.QPalette.ColorGroup.Disabled, QtGui.QPalette.ColorRole.ButtonText, disabledColor)
            darkPalette.setColor(QtGui.QPalette.ColorGroup.Disabled, QtGui.QPalette.ColorRole.HighlightedText, disabledColor)
            darkPalette.setColor(QtGui.QPalette.ColorGroup.Disabled, QtGui.QPalette.ColorRole.WindowText, disabledColor)

            app.setPalette(darkPalette)

    def get_qt_robodk_icon(icon_name: str, RDK: robolink.Robolink = None) -> QtGui.QImage:
        """
        Retrieve a RoboDK icon by name, such as robot, tool and frame icons (requires Qt module).

        :param icon_name: The name of the icon
        :type icon_name: str
        :return: a QImage of the icon if it succeeds, else None
        :rtype: :class:`PySide2.QtGui.QImage`

        .. seealso:: :func:`~robodk.roboapps.get_qt_robodk_icons`
        """
        if RDK is None:
            from robodk.robolink import Robolink
            RDK = Robolink()

        if 'Addin Manager' in RDK.Command('PluginsList'):
            img_hex = RDK.PluginCommand('Addin Manager', 'IconGet', icon_name)
        else:
            img_hex = RDK.PluginCommand('App Loader', 'IconGet', icon_name)
        if type(img_hex) is not str or img_hex == '':
            return None

        byte_array = QtCore.QByteArray.fromHex(img_hex.encode())
        image = QtGui.QImage()  # QImage does not require a QApplication instance, as appose to QPixmap
        if not image.loadFromData(byte_array):
            return None
        return image

    def get_qt_robodk_icons(RDK: robolink.Robolink = None) -> QtGui.QImage:
        """
        Retrieve a dictionary of available RoboDK icons, such as robot, tool and frame icons (requires Qt module).

        :return: a dictionary of QImage of available icons
        :rtype: dict of :class:`PySide2.QtGui.QImage`

        .. seealso:: :func:`~robodk.roboapps.get_qt_robodk_icon`
        """
        if RDK is None:
            from robodk.robolink import Robolink
            RDK = Robolink()

        tree_icons = [
            "station",
            "frame",
            "object",
            "robot",
            'mechanism',
            "tcp",
            "target",
            "targetjoint",
            "nodeprogram",
            "nodemachining",
            "nodemachining_printing",
            "nodemachining_curves",
            "nodemachining_milling",
            "nodemachining_points",
            "python",
            "folder",
            "notes",
            "curve",
            "point",
            "surface",
        ]

        sim_icons = [
            'play',
            'pause',
            'stop',
            'fastfwd',
            'start',
            'end',
        ]

        edit_icons = [
            'edit-copy',
            'edit-cut',
            'edit-paste',
            'edit',
            'loopno',
            'loopyes',
            'redo',
            'undo',
            'save',
            'saveas',
            'config',
            'configure',
            'newfile',
            'newfile_online',
            'newstation',
        ]

        mouse_icons = [
            'cursormoveframe',
            'cursormoveobject',
            'cursorpan',
            'cursorselectrectangle',
            'cursorsnone',
            'cursorsrotate',
            'cursorzoom',
        ]

        program_icons = [
            'inschangespeed',
            'inschangezone',
            'inscode',
            'inscomment',
            'insevent',
            'insmanageio',
            'insmoveC',
            'insmoveJ',
            'insmoveL',
            'insprint',
            'insprogcall',
            'instimer',
        ]

        view_icons = [
            'view-axometric',
            'view-bottom',
            'view-front',
            'view-fullscreen',
            'view-isometric',
            'view-left',
            'view-rear',
            'view-right',
            'view-rotate-left',
            'view-rotate-right',
            'view-top',
        ]

        action_icons = [
            'add',
            'plus',
            'minus',
            'yes',
            'no',
            'close',
            'replace',
            'information',
            'questionmark',
            'warning',
            'snapshot',
            'workspace',
            'anchor',
            'connect',
            'export',
            'package',
        ]

        icons = {}
        for name in tree_icons + sim_icons + edit_icons + mouse_icons + program_icons + view_icons + action_icons:
            icon = get_qt_robodk_icon(name, RDK)
            if not icon:
                continue
            icons[name] = icon
        return icons

    def value_to_qt_widget(value: Any, parent: QtWidgets.QWidget = None) -> Tuple[QtWidgets.QWidget, List]:
        """
        Convert a value to a widget. For instance, a float into a QDoubleSpinBox, a bool into a QCheckBox.

        The widget is automatically created for supported types:
        - bool, int, float, str (base types)
        - list or tuple of base types
        - dropdown formatted as [int, [str, str, ...]] i.e. [1, ['Option #1', 'Option #2']] where 1 means the default selected option is Option #2.
        - dictionary of supported values, formatted as {label:value}

        :return: (widget, funcs) the widget, and a list of get functions to retrieve the value of the widget
        """
        widget = None
        func = []
        value_type = type(value)

        if value_type is float:
            widget = QtWidgets.QDoubleSpinBox(parent)
            import decimal
            decimals = min(6, max(3, abs(decimal.Decimal(str(value)).as_tuple().exponent)))
            widget.setDecimals(decimals)
            widget.setRange(-9999999., 9999999.)
            widget.setValue(value)
            func = [widget.value]

        elif value_type is int:
            widget = QtWidgets.QSpinBox(parent)
            widget.setRange(-9999999, 9999999)
            widget.setValue(value)
            func = [widget.value]

        elif value_type is str:
            widget = QtWidgets.QLineEdit(parent)
            widget.setText(value)
            func = [widget.text]

        elif value_type is bool:
            widget = QtWidgets.QCheckBox("Activate", parent)
            widget.setChecked(value)
            func = [widget.isChecked]

        # List or tuple of PODs
        elif value_type in [list, tuple] and len(value) > 0 and all(isinstance(n, (float, int, str, bool)) for n in value):
            h_layout = QtWidgets.QHBoxLayout()
            h_layout.setSpacing(0)
            h_layout.setContentsMargins(0, 0, 0, 0)
            h_layout.setSizeConstraint(QtWidgets.QLayout.SetMinAndMaxSize)
            for v in value:
                f_widget, f_func = value_to_qt_widget(v, None)
                func.extend(f_func)
                h_layout.addWidget(f_widget)
            widget = QtWidgets.QWidget(parent)
            widget.setLayout(h_layout)

        # Dropdown with specified index as int [1, ['First line', 'Second line', 'Third line']] # NOTE: Removed the "value[0] in range(len(value[1]))" check, as developer can remove choices
        # Dropdown with specified index as str ['Second line', ['First line', 'Second line', 'Third line']] # NOTE: Removed the "value[0] in value[1]" check, as developer can remove choices
        elif value_type is list and (len(value) == 2) and isinstance(value[0], (int, str)) and isinstance(value[1], list) and all(isinstance(n, str) for n in value[1]):
            index = value[0]
            if isinstance(index, str):
                index = value[1].index(value[0])
            options = value[1]
            widget = QtWidgets.QComboBox(parent)
            widget.addItems(options)
            widget.setCurrentIndex(max(0, min(len(options) - 1, index)))
            func = [widget.currentIndex]  # str index will be replaced with int index once saved

        # Dictionary of label:value
        elif value_type is dict:
            f_layout = QtWidgets.QFormLayout()
            f_layout.setVerticalSpacing(1)
            f_layout.setHorizontalSpacing(10)
            f_layout.setContentsMargins(0, 0, 0, 0)
            f_layout.setSizeConstraint(QtWidgets.QLayout.SetMinAndMaxSize)

            for key, val in value.items():

                if key.endswith('$') and key.startswith('$'):
                    # Section separator
                    label = QtWidgets.QLabel()
                    label.setText(f'[  {key[1:-1]}  ]'.upper())
                    label.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignBottom)
                    spacing = 0
                    if f_layout.rowCount() > 0:
                        spacing += 15
                    label.setContentsMargins(0, spacing, 0, 5)
                    func.extend([key])
                    f_layout.addRow(label)
                    continue

                label = QtWidgets.QLabel(key)
                f_widget, f_func = value_to_qt_widget(val)
                func.extend(f_func)
                f_layout.addRow(label, f_widget)

            widget = QtWidgets.QWidget(parent)
            widget.setLayout(f_layout)

        return widget, func


"""
Tkinter utilities
"""

if robodialogs.ENABLE_TK:

    def get_tk_app(robodk_icon: bool = True, robodk_theme: bool = True, RDK: robolink.Robolink = None) -> tkinter.Tk:
        """
        Get the QApplication instance.

        :param robodk_icon: Applies the RoboDK logo, defaults to True
        :type robodk_icon: bool
        :param robodk_theme: Applies the current RoboDK theme, defaults to True
        :type robodk_theme: bool
        :param RDK: Link to the running RoboDK instance for the theme, defaults to None
        :type RDK: robolink.Robolink

        :return: The QApplication instance
        :rtype: :class:`PySide2.QtWidgets.QApplication`
        """

        app = tkinter.Tk()
        app.withdraw()  # Use app.deiconify() to show the app, if needed

        # Center the app in the screen
        app.update_idletasks()
        xp = (app.winfo_screenwidth() // 2) - (app.winfo_width() // 2)
        yp = (app.winfo_screenheight() // 2) - (app.winfo_height() // 2)
        app.geometry(f'+{xp}+{yp}')
        app.update_idletasks()

        if robodk_icon:
            from robodk import robolink
            icon_path = robolink.getPathIcon()
            from os import path
            if path.exists(icon_path):
                if sys.platform.startswith('win'):
                    import ctypes
                    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(str(app))  # Enable the taskbar icon
                app.iconbitmap(default=icon_path)

        if robodk_theme:
            pass  # TODO: Use tkk to apply styling globally

        return app

    def value_to_tk_widget(value: Any, frame: tkinter.Widget) -> tkinter.Widget:
        """
        Convert a value to a widget. For instance, a float into a Spinbox, a bool into a Checkbutton.

        The widget is automatically created for supported types:
        - bool, int, float, str (base types)
        - list or tuple of base types
        - dropdown formatted as [int, [str, str, ...]] i.e. [1, ['Option #1', 'Option #2']] where 1 means the default selected option is Option #2.
        - dictionary of supported values, formatted as {label:value}

        :return: (widget, funcs) the widget, and a list of get functions to retrieve the value of the widget
        """
        widget = None
        func = []
        value_type = type(value)

        if value_type is float:
            tkvar = tkinter.DoubleVar(value=value)
            func = [tkvar.get]
            import decimal
            decimals = min(6, max(3, abs(decimal.Decimal(str(value)).as_tuple().exponent)))
            widget = tkinter.Spinbox(frame, from_=-9999999, to=9999999, textvariable=tkvar, format=f"%.{decimals}f")

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
                func.extend(f_func)
                widget.grid_columnconfigure(idcol, weight=1)

        # Dropdown with specified index as int [1, ['First line', 'Second line', 'Third line']] # NOTE: Removed the "value[0] in  range(len(value[1]))" check, as developer can remove choices
        # Dropdown with specified index as str ['Second line', ['First line', 'Second line', 'Third line']] # NOTE: Removed the "value[0] in value[1]" check, as developer can remove choices
        elif value_type is list and (len(value) == 2) and isinstance(value[0], (int, str)) and isinstance(value[1], list) and all(isinstance(n, str) for n in value[1]):
            index = value[0]
            if isinstance(index, str):
                index = value[1].index(value[0])
            options = value[1]
            tkvar = tkinter.StringVar(value=options[max(0, min(len(options) - 1, index))])
            widget = tkinter.OptionMenu(frame, tkvar, *options)
            func = [tkvar.get]

        # Dictionary of label:value
        elif value_type is dict:

            widget = tkinter.Frame(frame)  # simple sub-container
            for i, (key, val) in enumerate(value.items()):

                if key.endswith('$') and key.startswith('$'):
                    # Section separator
                    label = tkinter.Label(widget, text=f'[  {key[1:-1]}  ]'.upper(), anchor='w')
                    label.grid(row=i, columnspan=2, sticky=tkinter.W + tkinter.S)
                    func.extend([key])
                    continue

                label_name = tkinter.Label(widget, text=key, anchor='w')
                label_name.grid(row=i, column=0, sticky=tkinter.NSEW)
                f_widget, f_func = value_to_tk_widget(val, widget)
                f_widget.grid(row=i, column=1, sticky=tkinter.W if type(f_widget) is tkinter.Checkbutton else tkinter.NSEW)
                func.extend(f_func)

        return widget, func


class AppSettings:
    """
    Generic application settings class to save and load settings to a RoboDK station with a built-in UI.

    :param settings_param: RoboDK parameter used to store this app settings. It should be unique if you have more than one App setting.
    :type settings_param: str

    Example:

        .. code-block:: python

            class Settings(AppSettings):

                def __init__(self, settings_param='My-App-Settings'):
                    super().__init__(settings_param=settings_param)

                    # List the variable names you would like to save and their default values.
                    # Variables that start with underscore (_) will not be saved.
                    self.BOOL = True
                    self.INT = 123456
                    self.FLOAT = 0.123456789
                    self.STRING = 'Text'
                    self.INT_LIST = [1, 2, 3]
                    self.FLOAT_LIST = [1.0, 2.0, 3.0]
                    self.STRING_LIST = ['First line', 'Second line', 'Third line']
                    self.MIXED_LIST = [False, 1, '2']
                    self.INT_TUPLE = (1, 2, 3)
                    self.DROPDOWN = [1, ['First line', 'Second line', 'Third line']]
                    self.DICT = {'This is a string': 'Text', 'This is a float': 0.0}

                    # Variable names when displayed on the user interface (detailed descriptions).
                    # Create this dictionary in the same order that you want to display it.
                    # If AppSettings._FIELDS_UI is not provided, all variables of this class will be used displayed with their attribute name.
                    # Fields within dollar signs (i.e. $abc$) are used as section headers.
                    from collections import OrderedDict
                    self._FIELDS_UI = OrderedDict()
                    self._FIELDS_UI['SECTION_1'] = '$This is a section$'
                    self._FIELDS_UI['BOOL'] = 'This is a bool'
                    self._FIELDS_UI['INT'] = 'This is an int'
                    self._FIELDS_UI['FLOAT'] = 'This is a float'
                    self._FIELDS_UI['STRING'] = 'This is a string'
                    self._FIELDS_UI['INT_LIST'] = 'This is an int list'
                    self._FIELDS_UI['FLOAT_LIST'] = 'This is a float list'
                    self._FIELDS_UI['STRING_LIST'] = 'This is a string list'
                    self._FIELDS_UI['MIXED_LIST'] = 'This is a mixed list'
                    self._FIELDS_UI['INT_TUPLE'] = 'This is an int tuple'
                    self._FIELDS_UI['SECTION_2'] = '$This is another section$'
                    self._FIELDS_UI['DROPDOWN'] = 'This is a dropdown'
                    self._FIELDS_UI['DICT'] = 'This is a dictionary'

                S = Settings()
                S.Load()  # Load previously saved settings from RoboDK
                S.ShowUI('Settings for my App')

                print(S.BOOL)

    """

    def __init__(self, settings_param: str = 'App-Settings'):
        self._ATTRIBS_SAVE = None  #: Optional, specific list of attributes names to save (default use all attributes that does not start with "_")
        self._FIELDS_UI = None  #: Optional, specific list of attributes description for the UI (default use attribute names)
        self._SETTINGS_PARAM = settings_param  #: Optional, settings name (any settings with the same name will override the other on save)
        self._ATTRIBS_SKIP_DEFAULT = []  #: Optional, specific list of attributes not to restore when restoring defaults (default use all attributes that does not start with "_")

    def CopyFrom(self, other: 'AppSettings'):
        """
        Copy settings from another AppSettings instance.

        :param other: The other AppSettings instance
        :type other: robodk.roboapps.AppSettings
        """
        attr = self.getAttribs()
        for a in attr:
            if hasattr(other, a):
                setattr(self, a, getattr(other, a))

    def SetDefaults(self):
        """
        Set defaults settings.
        Attributes in 'AppSettings._ATTRIBS_SKIP_DEFAULT', if defined, are ignored.
        """
        # save in local variables
        for var in self._ATTRIBS_SKIP_DEFAULT:
            exec('%s=self.%s' % (var, var))

        defaults = type(self)()
        self.CopyFrom(defaults)

        # restore from local vars
        for var in self._ATTRIBS_SKIP_DEFAULT:
            exec('self.%s=%s' % (var, var))

    def GetDefaults(self) -> Dict:
        """Get the default settings."""
        base = type(self)()
        defaults = {}
        for a in self.getAttribs():
            if hasattr(base, a):
                defaults[a] = getattr(base, a)
        return defaults

    def getAttribs(self) -> List[str]:
        """
        Get the list of all attributes (settings).
        Attributes that starts with '_' are ignored.

        :return: all attributes
        :rtype: list of str
        """
        return [a for a in dir(self) if (not callable(getattr(self, a)) and not a.startswith("_"))]

    def _getAttribsSave(self) -> List[str]:
        """
        Get the list of savable attributes (savable settings).
        Attributes not in 'AppSettings._ATTRIBS_SAVE', if defined, are ignored.

        :return: savable attributes
        :rtype: list of str
        """
        if type(self._ATTRIBS_SAVE) is list:
            return [a for a in self._ATTRIBS_SAVE if hasattr(self, a)]
        return self.getAttribs()

    def _getFieldsUI(self) -> Dict:
        """
        Get dictionary fields to be displayed in the UI.
        Fields in 'AppSettings._FIELDS_UI', if defined, are used in priority.
        Otherwise, the attribute name is used.

        :return: dictionary of field label and their value
        :rtype: dict
        """
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

    def get(self, attrib: str, default_value: Any = None) -> Any:
        """Get attribute value by key, otherwise it returns None"""
        if hasattr(self, attrib):
            return getattr(self, attrib)
        return default_value

    def Save(self, rdk: robolink.Robolink = None, autorecover: bool = False):
        """
        Save the class attributes as a RoboDK binary parameter in the specified station.
        If the station is not provided, it uses the active station.

        :param rdk: Station to save to, defaults to None
        :type rdk: Robolink, optional
        :param autorecover: Create a backup in the station, defaults to False
        :type autorecover: bool, optional
        """
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

    def Load(self, rdk: robolink.Robolink = None) -> bool:
        """
        Load the class attributes from a RoboDK binary parameter.
        If the station is not provided, it uses the active station.

        :param rdk: Station to load from, defaults to None
        :type rdk: Robolink, optional

        :return: True if it succeeds, else false.
        """
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

    def Erase(self, rdk: robolink.Robolink = None):
        """Completely erase the stored settings and its backup from RoboDK."""

        print("Erasing data from RoboDK station...")
        if rdk is None:
            from robodk.robolink import Robolink
            rdk = Robolink()

        param_val = self._SETTINGS_PARAM
        param_backup = param_val + "-Backup"
        rdk.setParam(param_val, b'')
        rdk.setParam(param_backup, b'')

    def ShowUI(self, windowtitle: str = None, embed: bool = False, show_default_button: bool = True, actions: List[Tuple[str, Any]] = None, *args, **kwargs):
        """
        Show the Apps Settings in a GUI.

        :param windowtitle: Window title, defaults to the Settings name
        :type windowtitle: str
        :param embed: Embed the settings window in RoboDK, defaults to False
        :type embed: bool
        :param show_default_button: Set to true to add a Default button to reset the fields, defaults to True
        :type show_default_button: bool
        :param actions: List of optional action callbacks to add as buttons, formatted as [(str, callable), ...]. e.g. [("Button #1", action_1), ("Button #2", action_2)]
        :type actions: list of tuples of str, callable

        :return: False if the user cancelled, else True.
        """
        from robodk.robodialogs import InputDialog

        if not windowtitle:
            windowtitle = self._SETTINGS_PARAM

        # Attributes to be displayed, as specified by the user.
        # This will either be field's description, or field's values
        attrib_desc = self._getFieldsUI()

        # Get the values of the attributes to display
        attrib_value = {}
        for attrib, desc in attrib_desc.items():
            if desc.endswith('$') and desc.startswith('$'):
                # Section header
                attrib_value[attrib] = desc
            elif hasattr(self, attrib):
                attrib_value[attrib] = getattr(self, attrib)
            else:
                print(f"Unable to find attribute {attrib}")

        # Get the default values of the class, if the user tries to restore them
        attrib_defaults = self.GetDefaults()

        # Put everything in the expected format for InputDialog
        desc_value = {attrib_desc[attrib]: attrib_value[attrib] for attrib in attrib_value}
        desc_default = {attrib_desc[attrib]: attrib_defaults[attrib] if attrib in attrib_defaults else attrib_value[attrib] for attrib in attrib_value}

        # Show the dialog to the user
        fields_value = InputDialog(msg='', value=desc_value, title=windowtitle, default_button=show_default_button, default_value=desc_default, embed=embed, actions=actions)
        if fields_value is None:
            # User cancelled
            return False

        # Apply the new values
        desc_value_inv = {v: k for k, v in attrib_desc.items()}
        for desc, value in fields_value.items():
            if desc.endswith('$') and desc.startswith('$'):
                # Section header
                continue
            attrib = desc_value_inv[desc]
            setattr(self, attrib, value)

        # And store them to the station
        self.Save()
        return True


def ShowExample():

    class SettingsExample(AppSettings):

        def __init__(self, settings_param='App-Settings-Example'):
            super(SettingsExample, self).__init__(settings_param=settings_param)

            # List the variable names you would like to save and their default values.
            # Variables that start with underscore (_) will not be saved.
            # Important: Try to avoid default None type! If None is used as default value, it will attempt to treat it as a float with a value of -1.
            self.BOOL = True
            self.INT = 123456
            self.FLOAT = 0.123456789
            self.STRING = 'Text'
            self.INT_LIST = [1, 2, 3]  # 3 numbers minimum!
            self.FLOAT_LIST = [1.0, 2.0, 3.0]  # 3 numbers minimum!
            self.STRING_LIST = ['First line', 'Second line', 'Third line']
            self.MIXED_LIST = [False, 1, '2']
            self.INT_TUPLE = (1, 2, 3)
            self.DROPDOWN = [1, ['First line', 'Second line', 'Third line']]
            self.DICT = {'This is a string': 'Text', 'This is a float': 0.0}

            # Variable names when displayed on the user interface (detailed descriptions).
            # Create this dictionary in the same order that you want to display it.
            # If AppSettings._FIELDS_UI is not provided, all variables of this class will be used and displayed as is (unless they start with '_').
            # Fields within dollar signs (i.e. $abc$) are used as section headers.
            from collections import OrderedDict
            self._FIELDS_UI = OrderedDict()
            self._FIELDS_UI['SECTION_1'] = '$This is a section$'
            self._FIELDS_UI['BOOL'] = 'This is a bool'
            self._FIELDS_UI['INT'] = 'This is an int'
            self._FIELDS_UI['FLOAT'] = 'This is a float'
            self._FIELDS_UI['STRING'] = 'This is a string'
            self._FIELDS_UI['INT_LIST'] = 'This is an int list'
            self._FIELDS_UI['FLOAT_LIST'] = 'This is a float list'
            self._FIELDS_UI['STRING_LIST'] = 'This is a string list'
            self._FIELDS_UI['MIXED_LIST'] = 'This is a mixed list'
            self._FIELDS_UI['INT_TUPLE'] = 'This is an int tuple'
            self._FIELDS_UI['SECTION_2'] = '$This is another section$'
            self._FIELDS_UI['DROPDOWN'] = 'This is a dropdown'
            self._FIELDS_UI['DICT'] = 'This is a dictionary'

        def ShowUI(self, *args, **kwargs):

            def showMessage():
                from robodk import robodialogs
                robodialogs.ShowMessageYesNo('Are you enjoying RoboDK?')

            def showIcons():
                icons = get_qt_robodk_icons()
                if icons:
                    icon_widget = QtWidgets.QWidget()
                    icon_layout = QtWidgets.QFormLayout(icon_widget)
                    for icon_name, icon_image in icons.items():
                        icon_label = QtWidgets.QLabel(icon_name)
                        icon_label.setPixmap(QtGui.QPixmap.fromImage(icon_image).scaledToHeight(32, QtCore.Qt.TransformationMode.SmoothTransformation))
                        icon_layout.addRow(icon_name, icon_label)
                    icon_widget.adjustSize()

                    scroll_widget = QtWidgets.QScrollArea()
                    scroll_widget.setFrameShape(QtWidgets.QFrame.NoFrame)
                    scroll_widget.setWidgetResizable(True)
                    scroll_widget.setWidget(icon_widget)
                    scroll_widget.setMinimumWidth(icon_widget.minimumWidth() + 20)

                    icon_window = QtWidgets.QDialog()
                    icon_window.setWindowTitle('RoboDK Icons')
                    icon_window.setWindowFlag(QtCore.Qt.WindowType.WindowStaysOnTopHint, True)
                    icon_window.setLayout(QtWidgets.QVBoxLayout())
                    icon_window.layout().addWidget(scroll_widget)
                    icon_window.exec_()
                else:
                    from robodk import robodialogs
                    robodialogs.ShowMessage('No icons to display! Is the plug-in enabled?')

            actions = [("Show a Yes/No Message", showMessage), ("Show RoboDK Icons", showIcons)]

            return super(SettingsExample, self).ShowUI(actions=actions, *args, **kwargs)

    S = SettingsExample()
    S.Load()  # Load previously stored settings in the station
    S.ShowUI('App Settings Example')  # Show the UI to the user. It would automatically save/discard on close
    S.INT = -123456  # Manually change a value
    S.Save()  # Manually save it
    S.Erase()  # Remove all data from the station


if __name__ == "__main__":

    def RunExample():
        ShowExample()

        if robodialogs.ENABLE_QT:
            robodialogs.ENABLE_QT = False
            ShowExample()

    #RunExample()
