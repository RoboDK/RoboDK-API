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
"""This module provides file operations utilities for the RoboDK API.
This toolbox includes FTP transfer functions, CSV import/export,
file operations, etc.

FTP transfers to a robot controller are available through :class:`~robodk.robofileio.RobotFTP` and :func:`~robodk.robofileio.UploadFTP`.

More information about the RoboDK API for Python here:

* https://robodk.com/doc/en/RoboDK-API.html
* https://robodk.com/doc/en/PythonAPI/robodk.html#robofileio-py
* https://robodk.com/doc/en/Add-ins.html
"""
# --------------------------------------------
import sys
import time
import os.path
from robodk import robomath

if sys.version_info.major >= 3 and sys.version_info.minor >= 5:
    # Python 3.5+ type hints. Type hints are stripped for <3.5
    from typing import List, Union, Tuple, Dict

#----------------------------------------------------
#--------      Generic file usage     ---------------


def searchfiles(pattern: str = 'C:\\RoboDK\\Library\\*.rdk') -> List[str]:
    """List the files in a directory with a given extension"""
    import glob
    return glob.glob(pattern)


#def CurrentFile(file = __file__):
#    """Returns the current Python file being executed"""
#    return os.path.realpath(file)


def getFileDir(filepath: str) -> str:
    """Returns the directory of a file path"""
    return os.path.dirname(filepath)


def getBaseName(filepath: str) -> str:
    """Returns the file name and extension of a file path"""
    return os.path.basename(filepath)


def getFileName(filepath: str) -> str:
    """Returns the file name (with no extension) of a file path"""
    return os.path.splitext(os.path.basename(filepath))[0]


def DateModified(filepath: str, stringformat: bool = False) -> Union[float, str]:
    """Returns the time that a file was modified"""
    time_in_s = os.path.getmtime(filepath)
    if stringformat:
        return time.ctime(time_in_s)
    else:
        return time_in_s


def DateCreated(filepath: str, stringformat: bool = False) -> Union[float, str]:
    """Returns the time that a file was created"""
    time_in_s = os.path.getctime(filepath)
    if stringformat:
        return time.ctime(time_in_s)
    else:
        return time_in_s


def DirExists(folder: str) -> bool:
    """Returns true if the folder exists"""
    return os.path.isdir(folder)


def FileExists(file: str) -> bool:
    """Returns true if the file exists"""
    return os.path.exists(file)


def FilterName(namefilter: str, safechar: str = 'P', reserved_names: List[str] = None, max_len: int = -1, space_to_underscore: bool = False, invalid_chars: str = ' .-[]/\\;,><&*:%=+@!#^|?^') -> str:
    """
    Get a safe program or variable name that can be used for robot programming.
    Removes invalid characters (such as .-[]/;,><&*:%=+@!#^|?), remove non-english characters, etc.

    :param namefilter: The name to filter
    :type namefilter: str
    :param safechar: Safe character to start a name with, in case the first character is a digit. Defaults to 'P'
    :type safechar: str, optional
    :param reserved_names: List of reserved names. A number is appended at the end if it already exists. The new name is added to the list. Defaults to None
    :type reserved_names: list of str, optional
    :param max_len: Maximum length of the name (number of characters), -1 means no maximum. Defaults to -1
    :type max_len: int, optional
    :param space_to_underscore: Replace whitespaces with underscores
    :type space_to_underscore: bool, optional
    :param invalid_chars: string containing all invalid character to remove. Defaults to r' .-[]/;,><&*:%=+@!#^|?^'
    :type invalid_chars: str, optional

    :return: The filtered name
    :rtype: str
    """
    if space_to_underscore and not '_' in invalid_chars:
        namefilter = namefilter.replace(' ', '_')

    # Remove non accepted characters
    for c in invalid_chars:
        namefilter = namefilter.replace(c, '')

    # Remove non english characters
    namefilter = ''.join((c for c in namefilter if 0 < ord(c) < 127))

    # Make sure we have a non empty string
    if len(namefilter) <= 0:
        namefilter = safechar

    # Make sure we don't start with a number
    if namefilter[0].isdigit():
        namefilter = safechar + namefilter

    # Some controllers have a limit of characters
    if max_len > 0:
        namefilter = namefilter[:max_len]

    # Make sure we are not using a reserved name
    if reserved_names:
        reserved_names_lower = [n.lower() for n in reserved_names]

        cnt = 1  # Count current instance as 1, subsequent is 2
        while namefilter.lower() in reserved_names_lower:
            if len(namefilter) == max_len:
                namefilter = namefilter[:-1]
            if cnt > 1:
                if max_len > 0:
                    namefilter = namefilter[:min(max_len - len(str(cnt)), len(namefilter))]
                namefilter = namefilter + "%i" % cnt
            cnt += 1

        # Add the name to reserved names
        if type(reserved_names) is list:
            reserved_names.append(namefilter)
        else:
            reserved_names.add(namefilter)

    return namefilter


def FilterNumber(number: float, fixed_points: int = 6, strip_zeros: bool = True, round_number: bool = True) -> str:
    """
    Get a formatted numerical number (float or int) as a string.

    :param number: The number
    :type number: float or int
    :param fixed_points: Maximum number of decimals, defaults to 6
    :type fixed_points: int, optional
    :param strip_zeros: Remove trailing zeros, including the decimal point. Defaults to True
    :type strip_zeros: bool, optional
    :param round_number: Round the number instead of cropping it. Defaults to True
    :type round_number: bool, optional

    :return: The formatted number
    :rtype: str
    """
    fixed_points = max(0, fixed_points)
    if round_number:
        s = format(number, '.%if' % fixed_points)  # format automatically rounds
    else:
        s = format(number, '.%if' % (fixed_points + 1))
        s = s[:-1]
    if strip_zeros:
        s = s.rstrip('0').rstrip('.')
    return s


def RobotPostFunction(r, data_json: Union[Dict, str], err_msg: str = "Unable to process this function. Please contact us at info@robodk.com."):
    """
    Post processor callback for custom functions.

    :param r: The robot post processor instance
    :type r: RobotPost
    :param data_json: The function callback name is specified by the 'fcn' key. The dictionary is passed as an argument to the callback function.
    :type data_json: dict
    :param err_msg: The error message to display to the user, defaults to "Unable to process this function. Please contact us at info@robodk.com."
    :type err_msg: str, optional
    """
    data_dict = data_json
    if isinstance(data_json, str):
        import json
        data_dict = json.loads(data_json)

    if not "fcn" in data_dict.keys():
        raise Exception(err_msg)
    fcn = data_dict["fcn"]

    if isinstance(fcn, str):
        try:
            fcn_ptr = getattr(r, fcn)
            fcn_ptr(data_dict)

        except Exception as e:
            try:
                r.RunMessage(err_msg, True)
                r.addlog(err_msg)

            except Exception:
                raise Exception(err_msg + "\n" + str(e))


#-------------------------------------------------------
# CSV tools
def LoadList(strfile: str, separator: str = ',', codec: str = 'utf-8') -> List:
    """Load data from a CSV file or a TXT file to a Python list (list of list of numbers)

    .. seealso:: :func:`~robodk.robofileio.SaveList`, :func:`~robodk.robofileio.LoadMat`

    Example:

        .. code-block:: python

            csvdata = LoadList(strfile, ',')
            values = []
            for i in range(len(csvdata)):
                print(csvdata[i])
                values.append(csvdata[i])

            # We can also save the list back to a CSV file
            # SaveList(csvdata, strfile, ',')

    """

    def todecimal(value):
        try:
            return float(value)
        except ValueError:
            return value

    import csv
    import codecs
    # Read all CSV data:
    csvdata = []
    #with open(strfile) as csvfile:
    with codecs.open(strfile, "r", codec) as csvfile:
        csvread = csv.reader(csvfile, delimiter=separator, quotechar='|')
        for row in csvread:
            row_nums = [todecimal(i) for i in row]
            csvdata.append(row_nums)
    return csvdata


def SaveList(list_variable: List, strfile: str, separator: str = ','):
    """Save a list or a list of lists as a CSV or TXT file.

    .. seealso:: :func:`~robodk.robofileio.LoadList`, :func:`~robodk.robofileio.LoadMat`"""

    robomath.Mat(list_variable).tr().SaveMat(strfile, separator)


def LoadMat(strfile: str, separator: str = ',') -> robomath.Mat:
    """Load data from a CSV file or a TXT file to a :class:`.Mat` Matrix

    .. seealso:: :func:`~robodk.robofileio.LoadList`

    """
    return robomath.Mat(LoadList(strfile, separator))


#-------------------------------------------------------
# FTP TRANSFER Tools


class RobotFTP:
    """FTP client to transfer robot programs (files or folders) to a robot controller, or to any FTP server.

    The connection is owned by the object: use it as a context manager (or call :func:`~robodk.robofileio.RobotFTP.Disconnect`) to make sure the connection is always closed.
    It connects when it is needed, or when :func:`~robodk.robofileio.RobotFTP.Connect` is called explicitly (local files are validated before connecting).
    Progress and errors are reported in the console, including ``POPUP:`` messages to display the progress in RoboDK.

    Example:

    .. code-block:: python

        from robodk.robofileio import RobotFTP

        with RobotFTP('192.168.0.1', 'robot', 'password') as ftp:
            ftp.Upload(['C:/RoboDK/Prog1.src', 'C:/RoboDK/Prog2.src'], '/program')

    .. seealso:: :func:`~robodk.robofileio.UploadFTP`
    """

    TIMEOUT: float = 30  #: Default timeout, in seconds, to connect and for each FTP operation
    MAX_DEPTH: int = 32  #: Maximum folder depth of recursive operations

    def __init__(self, server_ip: str, username: str = '', password: str = '', timeout: float = TIMEOUT):
        self.server_ip = server_ip  #: IP or name of the FTP server (the robot controller)
        self.username = username  #: FTP user name
        self.password = password  #: FTP password
        self.timeout = timeout  #: Timeout, in seconds, to connect and for each FTP operation
        self.ftp = None  #: ftplib.FTP connection, None if it is not connected

    #----------------------------------------------
    # Connection

    def __enter__(self) -> 'RobotFTP':
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.Disconnect()

    @staticmethod
    def FromConnection(ftp: 'ftplib.FTP') -> 'RobotFTP':
        """Create a RobotFTP object from an existing ftplib.FTP connection"""
        robotftp = RobotFTP('')
        robotftp.ftp = ftp
        return robotftp

    def Connect(self) -> bool:
        """Connect to the FTP server. A failure is reported as a popup.

        :return: True if the connection was established, False otherwise
        """
        import ftplib
        self.Disconnect()
        self._print("POPUP: <p>Connecting to <strong>%s</strong> using user name <strong>%s</strong> and password ****</p><p>Please wait...</p>" % (self.server_ip, self.username))
        try:
            self.ftp = ftplib.FTP(self.server_ip, self.username, self.password, timeout=self.timeout)
            self._print('Connection established')
            return True
        except Exception as e:
            self._error("Connection to %s failed: <p>%s</p>" % (self.server_ip, e))
            return False

    def Disconnect(self):
        """Close the connection, if any. Any error is ignored."""
        if self.ftp is None:
            return

        try:
            self.ftp.quit()  # politely close the session (it fails if the connection is already broken)
        except Exception:
            pass

        try:
            self.ftp.close()  # make sure the socket is released
        except Exception:
            pass

        self.ftp = None

    #----------------------------------------------
    # Transfer

    def Upload(self, program: Union[str, List[str]], remote_path: str) -> bool:
        """Upload a file, a folder (recursively), or a list of files and folders to a remote folder.

        :param program: local file or folder to transfer, or a list of files and folders
        :param str remote_path: remote folder to transfer to, it must exist (example: ``/program``)

        :return: True if everything was transferred, False otherwise
        """
        if isinstance(program, (list, tuple)):
            # Transfer all the files, do not stop at the first failure
            ntransferred = sum(1 for item in program if self.Upload(item, remote_path))
            if ntransferred == len(program):
                self._print("POPUP: <font color=\"blue\">Done: %i files and folders successfully transferred</font>" % ntransferred)
            else:
                self._print("POPUP: <font color=\"red\">Warning: only %i of %i files and folders were transferred</font>" % (ntransferred, len(program)))
            return ntransferred == len(program)

        if not program or not isinstance(program, str):
            self._error('File or folder not provided: %s' % repr(program))
            return False

        if os.path.isdir(program):
            self._print('Sending program folder %s...' % program)
            return self.UploadDir(program, remote_path)

        elif os.path.isfile(program):
            self._print('Sending program file %s...' % program)
            return self.UploadFile(program, remote_path)

        self._error('File or folder not found: %s' % program)
        return False

    def UploadFile(self, local_file: str, remote_path: str) -> bool:
        """Upload one file to a remote folder.

        :param str local_file: local file to transfer
        :param str remote_path: remote folder to transfer to, it must exist (example: ``/program``)

        :return: True if the file was transferred, False otherwise
        """
        import ftplib
        if not local_file or not os.path.isfile(local_file):
            self._error('File not found: %s' % local_file)
            return False

        if not self._Connected():
            return False

        filename = self._Name(local_file)
        remote_file = self._Join(remote_path, filename)
        if not self._Cd(remote_path):
            return False

        self._print("POPUP: Connected. Deleting remote file %s..." % remote_file)
        # The file may not exist (it is not an error), the transfer is attempted even if it can not be deleted
        self.RemoveFile(filename, silent=True)

        self._print("POPUP: Connected. Uploading program to %s..." % self.server_ip)
        try:
            self._Store(local_file, filename)
        except ftplib.all_errors + (ValueError,) as e:
            self._error('File transfer failed: %s<p>%s</p>' % (remote_file, e))
            return False

        self._print("POPUP: File transfer completed: <font color=\"blue\">%s</font>" % remote_file)
        return True

    def UploadDir(self, local_folder: str, remote_path: str) -> bool:
        """Upload a folder and its contents (recursively) to a remote folder.
        The remote folder is deleted first, if it exists.

        :param str local_folder: local folder to transfer
        :param str remote_path: remote folder to transfer to, it must exist (example: ``/program``)

        :return: True if the folder was transferred, False otherwise
        """
        import ftplib
        if not local_folder or not os.path.isdir(local_folder):
            self._error('Folder not found: %s' % local_folder)
            return False

        if not self._Connected():
            return False

        foldername = self._Name(os.path.normpath(local_folder))
        remote_folder = self._Join(remote_path, foldername)

        self._print("POPUP: Connected. Deleting existing files on %s..." % remote_folder)
        self.RemoveDir(remote_folder)

        self._print("POPUP: Connected. Uploading program to %s..." % self.server_ip)
        if not self._Cd(remote_path):
            return False

        try:
            self._Mkdir(foldername)  # the folder may still exist if it could not be deleted
            self.ftp.cwd(foldername)
            self._UploadContents(local_folder)
        except ftplib.all_errors + (ValueError,) as e:
            self._error('Folder transfer failed: %s<p>%s</p>' % (remote_folder, e))
            return False

        self._print("POPUP: Folder transfer completed: <font color=\"blue\">%s</font>" % remote_folder)
        return True

    def RemoveFile(self, remote_file: str, silent: bool = False) -> bool:
        """Delete a file on the FTP server.

        :param str remote_file: remote file to delete
        :param bool silent: True to report a failure in the console only (deleting a file that does not exist is not always an error)

        :return: True if the file was deleted, False otherwise
        """
        import ftplib
        if not self._Connected():
            return False

        try:
            self.ftp.delete(remote_file)
            return True
        except ftplib.all_errors as e:
            self._print('%sCould not remove file %s: %s' % ('' if silent else 'POPUP: ', remote_file, e))
            return False

    def RemoveDir(self, remote_folder: str, max_depth: int = MAX_DEPTH) -> bool:
        """Delete a folder and its contents (recursively) on the FTP server.

        :param str remote_folder: remote folder to delete
        :param int max_depth: maximum folder depth to delete (it prevents an infinite recursion)

        :return: True if the folder was deleted, False otherwise
        """
        import ftplib
        if not self._Connected():
            return False

        if max_depth <= 0:
            self._print('Maximum folder depth reached, skipping %s' % remote_folder)
            return False

        try:
            names = self.ftp.nlst(remote_folder)
        except ftplib.all_errors as e:
            # some FTP servers complain when you try and list non-existent paths
            self._print('Could not remove folder %s: %s' % (remote_folder, e))
            return False

        for name in names:
            # some FTP servers return the complete path instead of the file name only
            name = self._Name(name)
            if name in ('', '.', '..'):
                continue

            remote_item = self._Join(remote_folder, name)
            self._print('Removing %s' % remote_item)
            if self._IsDir(remote_item):
                self.RemoveDir(remote_item, max_depth - 1)
            else:
                self.RemoveFile(remote_item, silent=True)

        try:
            self.ftp.rmd(remote_folder)
        except ftplib.all_errors as e:
            self._print('Could not remove folder %s: %s' % (remote_folder, e))
            return False

        return True

    #----------------------------------------------
    # Internal

    @staticmethod
    def _print(message: str):
        """Display a message in the console (``POPUP:`` messages are displayed in RoboDK)"""
        print(message)
        sys.stdout.flush()

    def _error(self, message: str):
        """Display an error as a popup and give the user time to read it"""
        self._print("POPUP: <font color=\"red\">%s</font>" % message)
        robomath.pause(4)

    @staticmethod
    def _Name(path: str) -> str:
        """Returns the file or folder name of a local or remote path"""
        return path.replace('\\', '/').rstrip('/').rsplit('/', 1)[-1]

    @staticmethod
    def _Join(remote_path: str, name: str) -> str:
        """Join a remote (POSIX style) path and a file or folder name"""
        if not remote_path:
            return name

        return remote_path.rstrip('/') + '/' + name

    @staticmethod
    def _Check(name: str) -> str:
        """Make sure a file or folder name can be used in an FTP command.
        FTP commands are line based, therefore a name containing a new line character could inject arbitrary FTP commands."""
        if not name or '\r' in name or '\n' in name:
            raise ValueError('Invalid file or folder name for FTP transfer: %s' % repr(name))

        return name

    def _Connected(self) -> bool:
        """Returns True if we are connected to the FTP server. It connects if it is not connected yet."""
        return self.ftp is not None or self.Connect()

    def _IsDir(self, remote_path: str) -> bool:
        """Returns True if a remote path is a folder (if we can enter it)"""
        import ftplib
        try:
            working_folder = self.ftp.pwd()
            self.ftp.cwd(remote_path)
        except ftplib.all_errors:
            return False

        try:
            self.ftp.cwd(working_folder)  # don't stay inside a folder that may be deleted
        except ftplib.all_errors:
            pass

        return True

    def _Cd(self, remote_path: str) -> bool:
        """Set the remote working folder. A failure is reported as a popup."""
        import ftplib
        try:
            self.ftp.cwd(remote_path)
            return True
        except ftplib.all_errors as e:
            self._error("Remote path not found or can't be created: %s<p>%s</p>" % (remote_path, e))
            #contin = mbox("Remote path\n%s\nnot found or can't create folder.\n\nChange path and permissions and retry." % remote_path)
            return False

    def _Mkdir(self, name: str):
        """Create a folder in the remote working folder. An existing folder is not an error."""
        import ftplib
        self._Check(name)
        try:
            self.ftp.mkd(name)
        except ftplib.all_errors:
            pass  # the folder may already exist

    def _Store(self, local_file: str, name: str):
        """Upload one file to the remote working folder"""
        self._Check(name)
        self._print('  Sending file: %s' % local_file)
        self._print("POPUP: Sending file: %s" % name)
        with open(local_file, 'rb') as fh:
            self.ftp.storbinary('STOR %s' % name, fh)

    def _UploadContents(self, local_folder: str):
        """Upload the contents of a local folder to the remote working folder, recursively.
        The remote working folder is left unchanged."""
        for name in sorted(os.listdir(local_folder)):
            local_item = os.path.join(local_folder, name)
            if os.path.isfile(local_item):
                self._Store(local_item, name)

            elif os.path.isdir(local_item):
                self._print('  Sending folder: %s' % name)
                self._Mkdir(name)
                self.ftp.cwd(name)
                self._UploadContents(local_item)
                self.ftp.cwd('..')


def RemoveFileFTP(ftp: 'ftplib.FTP', filepath: str) -> bool:
    """Delete a file on a remote server.

    :return: True if the file was deleted, False otherwise

    .. seealso:: :func:`RobotFTP.RemoveFile <robodk.robofileio.RobotFTP.RemoveFile>`
    """
    return RobotFTP.FromConnection(ftp).RemoveFile(filepath)


def RemoveDirFTP(ftp: 'ftplib.FTP', path: str) -> bool:
    """Recursively delete a directory tree on a remote server.

    :return: True if the folder was deleted, False otherwise

    .. seealso:: :func:`RobotFTP.RemoveDir <robodk.robofileio.RobotFTP.RemoveDir>`
    """
    return RobotFTP.FromConnection(ftp).RemoveDir(path)


def UploadDirFTP(localpath: str, server_ip: str, remote_path: str, username: str, password: str, timeout: float = RobotFTP.TIMEOUT) -> bool:
    """Upload a folder to a robot through FTP recursively

    :return: True if the folder was transferred, False otherwise

    .. seealso:: :func:`RobotFTP.UploadDir <robodk.robofileio.RobotFTP.UploadDir>`
    """
    with RobotFTP(server_ip, username, password, timeout) as ftp:
        return ftp.UploadDir(localpath, remote_path)


def UploadFileFTP(file_path_name: str, server_ip: str, remote_path: str, username: str, password: str, timeout: float = RobotFTP.TIMEOUT) -> bool:
    """Upload a file to a robot through FTP

    :return: True if the file was transferred, False otherwise

    .. seealso:: :func:`RobotFTP.UploadFile <robodk.robofileio.RobotFTP.UploadFile>`
    """
    with RobotFTP(server_ip, username, password, timeout) as ftp:
        return ftp.UploadFile(file_path_name, remote_path)


def UploadFTP(program: Union[str, List[str]], robot_ip: str, remote_path: str, ftp_user: str, ftp_pass: str, pause_sec: float = 2) -> bool:
    """Upload a program or a list of programs to the robot through FTP provided the connection parameters

    :return: True if all the files and folders were transferred, False otherwise

    .. seealso:: :func:`RobotFTP.Upload <robodk.robofileio.RobotFTP.Upload>`
    """
    if isinstance(program, (list, tuple)) and len(program) == 0:
        print('POPUP: Nothing to transfer')
        sys.stdout.flush()
        robomath.pause(pause_sec)
        return False

    # All the files and folders are transferred through the same connection
    with RobotFTP(robot_ip, ftp_user, ftp_pass) as ftp:
        success = ftp.Upload(program, remote_path)

    robomath.pause(pause_sec)
    print("POPUP: Done")
    sys.stdout.flush()
    return success


if __name__ == "__main__":
    pass
