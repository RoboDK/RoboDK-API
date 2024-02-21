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
# This is a file operations toolbox for RoboDK API for Python
# This toolbox includes FTP functions, file operations, etc.
#
# More information about the RoboDK API for Python here:
#     https://robodk.com/doc/en/RoboDK-API.html
#     https://robodk.com/doc/en/PythonAPI/index.html
#
# --------------------------------------------
import sys
if sys.version_info.major >= 3 and sys.version_info.minor >= 5:
    # Python 3.5+ type hints. Type hints are stripped for <3.5
    from typing import List, Union, Tuple, Dict

import time
import os.path
import time
import ftplib
from robodk import robomath

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


def FilterName(namefilter: str, safechar: str = 'P', reserved_names: List[str] = None, max_len: int = -1, space_to_underscore: bool = False, invalid_chars: str = r' .-[]/\;,><&*:%=+@!#^|?^') -> str:
    """
    Get a safe program or variable name that can be used for robot programming.
    Removes invalid characters ( .-[]/\;,><&*:%=+@!#^|?), remove non-english characters, etc.

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
    :param invalid_chars: string containing all invalid character to remove. Defaults to r' .-[]/\;,><&*:%=+@!#^|?^'
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
        except:
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
def RemoveFileFTP(ftp: ftplib.FTP, filepath: str):
    """Delete a file on a remote server."""
    try:
        ftp.delete(filepath)
    except ftplib.all_errors as e:
        import sys
        print('POPUP: Could not remove file {0}: {1}'.format(filepath, e))
        sys.stdout.flush()


def RemoveDirFTP(ftp: ftplib.FTP, path: str):
    """Recursively delete a directory tree on a remote server."""
    wd = ftp.pwd()
    try:
        names = ftp.nlst(path)
    except ftplib.all_errors as e:
        # some FTP servers complain when you try and list non-existent paths
        print('RemoveDirFTP: Could not remove folder {0}: {1}'.format(path, e))
        return

    for name in names:
        if os.path.split(name)[1] in ('.', '..'):
            continue
        print('RemoveDirFTP: Checking {0}'.format(name))
        try:
            ftp.cwd(path + '/' + name)  # if we can cwd to it, it's a folder
            ftp.cwd(wd)  # don't try a nuke a folder we're in
            RemoveDirFTP(ftp, path + '/' + name)
        except ftplib.all_errors:
            ftp.delete(path + '/' + name)
            #RemoveFileFTP(ftp, name)

    try:
        ftp.rmd(path)
    except ftplib.all_errors as e:
        print('RemoveDirFTP: Could not remove {0}: {1}'.format(path, e))


def UploadDirFTP(localpath: str, server_ip: str, remote_path: str, username: str, password: str) -> bool:
    """Upload a folder to a robot through FTP recursively"""
    import os
    import sys
    main_folder = os.path.basename(os.path.normpath(localpath))
    print("POPUP: <p>Connecting to <strong>%s</strong> using user name <strong>%s</strong> and password ****</p><p>Please wait...</p>" % (server_ip, username))
    sys.stdout.flush()
    try:
        myFTP = ftplib.FTP(server_ip, username, password)
        print('Connection established')
    except:
        error_str = sys.exc_info()[1]
        print("POPUP: <font color=\"red\">Connection to %s failed: <p>%s</p></font>" % (server_ip, error_str))
        sys.stdout.flush()
        robomath.pause(4)
        return False

    remote_path_prog = remote_path + '/' + main_folder
    myPath = r'%s' % localpath
    print("POPUP: Connected. Deleting existing files on %s..." % remote_path_prog)
    sys.stdout.flush()
    RemoveDirFTP(myFTP, remote_path_prog)
    print("POPUP: Connected. Uploading program to %s..." % server_ip)
    sys.stdout.flush()
    try:
        myFTP.cwd(remote_path)
        myFTP.mkd(main_folder)
        myFTP.cwd(remote_path_prog)
    except:
        error_str = sys.exc_info()[1]
        print("POPUP: <font color=\"red\">Remote path not found or can't be created: %s</font>" % (remote_path))
        sys.stdout.flush()
        robomath.pause(4)
        #contin = mbox("Remote path\n%s\nnot found or can't create folder.\n\nChange path and permissions and retry." % remote_path)
        return False

    def uploadThis(path):
        files = os.listdir(path)
        os.chdir(path)
        for f in files:
            if os.path.isfile(path + r'\{}'.format(f)):
                print('  Sending file: %s' % f)
                print("POPUP: Sending file: %s" % f)
                sys.stdout.flush()
                fh = open(f, 'rb')
                myFTP.storbinary('STOR %s' % f, fh)
                fh.close()
            elif os.path.isdir(path + r'\{}'.format(f)):
                print('  Sending folder: %s' % f)
                myFTP.mkd(f)
                myFTP.cwd(f)
                uploadThis(path + r'\{}'.format(f))
        myFTP.cwd('..')
        os.chdir('..')

    uploadThis(myPath)  # now call the recursive function
    myFTP.close()
    print("POPUP: Folder trasfer completed: <font color=\"blue\">%s</font>" % remote_path)
    sys.stdout.flush()
    return True


def UploadFileFTP(file_path_name: str, server_ip: str, remote_path: str, username: str, password: str) -> bool:
    """Upload a file to a robot through FTP"""
    filepath = getFileDir(file_path_name)
    filename = getBaseName(file_path_name)
    import sys
    print("POPUP: <p>Connecting to <strong>%s</strong> using user name <strong>%s</strong> and password ****</p><p>Please wait...</p>" % (server_ip, username))
    sys.stdout.flush()
    try:
        myFTP = ftplib.FTP(server_ip, username, password)
    except:
        error_str = sys.exc_info()[1]
        print("POPUP: <font color=\"red\">Connection to %s failed: <p>%s</p></font>" % (server_ip, error_str))
        sys.stdout.flush()
        robomath.pause(4)
        return False

    remote_path_prog = remote_path + '/' + filename
    print("POPUP: Connected. Deleting remote file %s..." % remote_path_prog)
    sys.stdout.flush()
    RemoveFileFTP(myFTP, remote_path_prog)
    print("POPUP: Connected. Uploading program to %s..." % server_ip)
    sys.stdout.flush()
    try:
        myFTP.cwd(remote_path)
    except:
        error_str = sys.exc_info()[1]
        print("POPUP: <font color=\"red\">Remote path not found or can't be created: %s</font>" % (remote_path))
        sys.stdout.flush()
        robomath.pause(4)
        #contin = mbox("Remote path\n%s\nnot found or can't create folder.\n\nChange path and permissions and retry." % remote_path)
        return False

    def uploadThis(localfile, filename):
        print('  Sending file: %s' % localfile)
        print("POPUP: Sending file: %s" % filename)
        sys.stdout.flush()
        fh = open(localfile, 'rb')
        myFTP.storbinary('STOR %s' % filename, fh)
        fh.close()

    uploadThis(file_path_name, filename)
    myFTP.close()
    print("POPUP: File trasfer completed: <font color=\"blue\">%s</font>" % remote_path_prog)
    sys.stdout.flush()
    return True


def UploadFTP(program: Union[str, List[str]], robot_ip: str, remote_path: str, ftp_user: str, ftp_pass: str, pause_sec: float = 2):
    """Upload a program or a list of programs to the robot through FTP provided the connection parameters"""
    # Iterate through program list if it is a list of files
    if isinstance(program, list):
        if len(program) == 0:
            print('POPUP: Nothing to transfer')
            sys.stdout.flush()
            robomath.pause(pause_sec)
            return

        for prog in program:
            UploadFTP(prog, robot_ip, remote_path, ftp_user, ftp_pass, 0)

        print("POPUP: <font color=\"blue\">Done: %i files and folders successfully transferred</font>" % len(program))
        sys.stdout.flush()
        robomath.pause(pause_sec)
        print("POPUP: Done")
        sys.stdout.flush()
        return

    import os
    if os.path.isfile(program):
        print('Sending program file %s...' % program)
        UploadFileFTP(program, robot_ip, remote_path, ftp_user, ftp_pass)
    else:
        print('Sending program folder %s...' % program)
        UploadDirFTP(program, robot_ip, remote_path, ftp_user, ftp_pass)

    robomath.pause(pause_sec)
    print("POPUP: Done")
    sys.stdout.flush()


if __name__ == "__main__":
    pass
