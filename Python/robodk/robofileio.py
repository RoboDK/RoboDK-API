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
import time
import os.path
import time

from . import robomath

#----------------------------------------------------
#--------      Generic file usage     ---------------


def searchfiles(pattern='C:\\RoboDK\\Library\\*.rdk'):
    """List the files in a directory with a given extension"""
    import glob
    return glob.glob(pattern)


#def CurrentFile(file = __file__):
#    """Returns the current Python file being executed"""
#    return os.path.realpath(file)


def getFileDir(filepath):
    """Returns the directory of a file path"""
    return os.path.dirname(filepath)


def getBaseName(filepath):
    """Returns the file name and extension of a file path"""
    return os.path.basename(filepath)


def getFileName(filepath):
    """Returns the file name (with no extension) of a file path"""
    return os.path.splitext(os.path.basename(filepath))[0]


def DateModified(filepath, stringformat=False):
    """Returns the time that a file was modified"""
    time_in_s = os.path.getmtime(filepath)
    if stringformat:
        return time.ctime(time_in_s)
    else:
        return time_in_s


def DateCreated(filepath, stringformat=False):
    """Returns the time that a file was modified"""
    time_in_s = os.path.getctime(filepath)
    if stringformat:
        return time.ctime(time_in_s)
    else:
        return time_in_s


def DirExists(folder):
    """Returns true if the folder exists"""
    return os.path.isdir(folder)


def FileExists(file):
    """Returns true if the file exists"""
    return os.path.exists(file)


def FilterName(namefilter, safechar='P', reserved_names=None):
    """Get a safe program or variable name that can be used for robot programming"""
    # remove non accepted characters
    for c in r' -[]/\;,><&*:%=+@!#^|?^':
        namefilter = namefilter.replace(c, '')

    # remove non english characters
    char_list = (c for c in namefilter if 0 < ord(c) < 127)
    namefilter = ''.join(char_list)

    # Make sure we have a non empty string
    if len(namefilter) <= 0:
        namefilter = safechar

    # Make sure we don't start with a number
    if namefilter[0].isdigit():
        print(namefilter)
        namefilter = safechar + namefilter

    # Make sure we are not using a reserved name
    if reserved_names is not None:
        while namefilter.lower() in reserved_names:
            namefilter = safechar + namefilter

        # Add the name to reserved names
        reserved_names.append(namefilter)

    return namefilter


#-------------------------------------------------------
# CSV tools
def LoadList(strfile, separator=',', codec='utf-8'):
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


def SaveList(list_variable, strfile, separator=','):
    """Save a list or a list of lists as a CSV or TXT file.

    .. seealso:: :func:`~robodk.robofileio.LoadList`, :func:`~robodk.robofileio.LoadMat`"""

    robomath.Mat(list_variable).tr().SaveMat(strfile, separator)


def LoadMat(strfile, separator=','):
    """Load data from a CSV file or a TXT file to a :class:`.Mat` Matrix

    .. seealso:: :func:`~robodk.robofileio.LoadList`

    """
    return robomath.Mat(LoadList(strfile, separator))


#-------------------------------------------------------
# FTP TRANSFER Tools
def RemoveFileFTP(ftp, filepath):
    """Delete a file on a remote server."""
    import ftplib
    try:
        ftp.delete(filepath)
    except ftplib.all_errors as e:
        import sys
        print('POPUP: Could not remove file {0}: {1}'.format(filepath, e))
        sys.stdout.flush()


def RemoveDirFTP(ftp, path):
    """Recursively delete a directory tree on a remote server."""
    import ftplib
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


def UploadDirFTP(localpath, server_ip, remote_path, username, password):
    """Upload a folder to a robot through FTP recursively"""
    import ftplib
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


def UploadFileFTP(file_path_name, server_ip, remote_path, username, password):
    """Upload a file to a robot through FTP"""
    filepath = getFileDir(file_path_name)
    filename = getBaseName(file_path_name)
    import ftplib
    import os
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


def UploadFTP(program, robot_ip, remote_path, ftp_user, ftp_pass, pause_sec=2):
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
