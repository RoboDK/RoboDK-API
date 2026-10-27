"""Tests for the transfer tools of robodk.robofileio: RobotFTP, RobotSFTP, RobotFTPS and the Upload functions.

These tests are standalone: RoboDK does not need to be running, and no FTP/SFTP server
or paramiko installation is required.
A fake server (in memory) replaces ftplib.FTP and the paramiko module, so the complete
transfer logic can be verified without a real robot controller.

The transfer tests in TransferTests run identically over every protocol.
"""

import ftplib
import os
import shutil
import stat
import sys
import tempfile
import unittest

# Test the robodk package of this repository, not a copy that may be installed in site-packages
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from robodk.robofileio import RobotFTP, RobotSFTP, RobotFTPS
from robodk.robofileio import UploadFTP, UploadFileFTP, UploadDirFTP, RemoveFileFTP, RemoveDirFTP
from robodk.robofileio import UploadSFTP, UploadFileSFTP, UploadDirSFTP


class FakeError(OSError):
    """A failure reported by the fake server.
    It derives from OSError so that it is part of both ftplib.all_errors and the SFTP error tuple."""


class FakeServer:
    """Minimal in-memory remote file system, shared by the FTP and the SFTP doubles.
    Folders is a set of absolute POSIX paths, files maps such a path to its content."""

    # Set by the tests to simulate server specific behaviors
    nlst_full_path = False  # some FTP servers return the complete path instead of the file name
    nlst_dots = False  # some FTP servers include '.' and '..' when a folder is listed
    fail_delete = False  # some controllers do not allow deleting files
    fail_store = False  # the connection may drop during a transfer
    instances = []  # every connection that was established, in order

    def __init__(self):
        self.closed = False
        self.working_folder = '/'
        self.folders = {'/', '/prog'}
        self.files = {}
        FakeServer.instances.append(self)

    #----------------------------------------------
    # Protocol independent operations
    def _cd(self, path):
        folder = self._abs(path)
        if folder not in self.folders:
            raise FakeError('%s: No such file or directory' % path)
        self.working_folder = folder

    def _list(self, path):
        folder = self._abs(path)
        if folder not in self.folders:
            raise FakeError('%s: No such file or directory' % path)

        names = []
        prefix = folder.rstrip('/') + '/'
        for item in sorted(self.folders | set(self.files)):
            if not item.startswith(prefix) or '/' in item[len(prefix):]:
                continue  # not a direct child
            names.append(item[len(prefix):])

        return names

    def _remove(self, path):
        if self.fail_delete:
            raise FakeError('Permission denied')
        if self._abs(path) not in self.files:
            raise FakeError('%s: No such file or directory' % path)
        self.files.pop(self._abs(path))

    def _mkdir(self, path):
        folder = self._abs(path)
        if folder in self.folders or folder in self.files:
            raise FakeError('%s: File exists' % path)
        if self._parent(folder) not in self.folders:
            raise FakeError('%s: No such file or directory' % path)
        self.folders.add(folder)

    def _rmdir(self, path):
        folder = self._abs(path)
        if folder not in self.folders:
            raise FakeError('%s: No such file or directory' % path)
        if self._list(folder):
            raise FakeError('%s: Directory not empty' % path)
        self.folders.discard(folder)

    def _store(self, path, content):
        if self.fail_store:
            raise FakeError('Connection closed, transfer aborted')
        filepath = self._abs(path)
        if self._parent(filepath) not in self.folders:
            raise FakeError('%s: No such file or directory' % path)
        self.files[filepath] = content

    def _isdir(self, path):
        return self._abs(path) in self.folders

    #----------------------------------------------
    def _abs(self, path):
        if not path.startswith('/'):
            path = self.working_folder.rstrip('/') + '/' + path

        parts = []
        for name in path.split('/'):
            if name in ('', '.'):
                continue
            elif name == '..':
                if parts:
                    parts.pop()
            else:
                parts.append(name)

        return '/' + '/'.join(parts)

    @staticmethod
    def _parent(path):
        return path.rsplit('/', 1)[0] or '/'


class FakeFTP(FakeServer):
    """Fake ftplib.FTP"""

    def __init__(self, host='', user='', passwd='', acct='', timeout=None, **kwargs):
        FakeServer.__init__(self)
        self.host = host
        self.user = user
        self.port = None
        self.timeout = timeout
        self.logged_in = bool(user)

    def connect(self, host, port=21):
        self.host = host
        self.port = port

    def login(self, user='', passwd=''):
        self.user = user
        self.logged_in = True

    def pwd(self):
        return self.working_folder

    def cwd(self, path):
        self._cd(path)

    def nlst(self, path=''):
        names = ['.', '..'] if self.nlst_dots else []
        folder = self._abs(path).rstrip('/')
        for name in self._list(path):
            names.append(folder + '/' + name if self.nlst_full_path else name)
        return names

    def delete(self, filepath):
        self._remove(filepath)

    def mkd(self, path):
        self._mkdir(path)

    def rmd(self, path):
        self._rmdir(path)

    def storbinary(self, cmd, fp, blocksize=8192):
        if not cmd.startswith('STOR '):
            raise FakeError('Unknown command: %s' % cmd)
        self._store(cmd[len('STOR '):], fp.read())

    def quit(self):
        self.closed = True

    def close(self):
        self.closed = True


class FakeFTP_TLS(FakeFTP):
    """Fake ftplib.FTP_TLS"""

    def __init__(self, *args, **kwargs):
        FakeFTP.__init__(self, *args, **kwargs)
        self.encrypted = False

    def prot_p(self):
        self.encrypted = True


class FakeSFTP(FakeServer):
    """Fake paramiko.SFTPClient"""

    def getcwd(self):
        return self.working_folder

    def chdir(self, path):
        self._cd(path)

    def listdir(self, path='.'):
        return self._list(path)  # paramiko returns the names only, never '.' or '..'

    def remove(self, path):
        self._remove(path)

    def mkdir(self, path, mode=511):
        self._mkdir(path)

    def rmdir(self, path):
        self._rmdir(path)

    def put(self, localpath, remotepath, callback=None, confirm=True):
        with open(localpath, 'rb') as fh:
            self._store(remotepath, fh.read())

    def stat(self, path):
        if not self._isdir(path) and self._abs(path) not in self.files:
            raise FakeError('%s: No such file or directory' % path)

        class Attributes:
            st_mode = stat.S_IFDIR | 0o755 if self._isdir(path) else stat.S_IFREG | 0o644

        return Attributes()

    def close(self):
        self.closed = True


class FakeSSHClient:
    """Fake paramiko.SSHClient"""

    fail_connect = False  # set by the tests to simulate a server that can not be reached

    def __init__(self):
        self.policy = None
        self.system_host_keys_loaded = False
        self.connect_args = None
        self.closed = False
        self.sftp = None

    def load_system_host_keys(self, filename=None):
        self.system_host_keys_loaded = True

    def set_missing_host_key_policy(self, policy):
        self.policy = policy

    def connect(self, hostname, **kwargs):
        if FakeSSHClient.fail_connect:
            raise FakeSSHException('Unable to connect to port %s on %s' % (kwargs.get('port'), hostname))

        self.connect_args = dict(kwargs)
        self.connect_args['hostname'] = hostname

    def open_sftp(self):
        self.sftp = FakeSFTP()
        return self.sftp

    def close(self):
        self.closed = True


class FakeAutoAddPolicy:
    pass


class FakeRejectPolicy:
    pass


class FakeSSHException(Exception):
    pass


class FakeParamiko:
    """Fake paramiko module"""

    SSHClient = FakeSSHClient
    AutoAddPolicy = FakeAutoAddPolicy
    RejectPolicy = FakeRejectPolicy
    SSHException = FakeSSHException
    imports = 0  # how many times the module was requested (it must be lazy)

    @staticmethod
    def Import():
        """Stands in for RobotSFTP._Paramiko"""
        FakeParamiko.imports += 1
        return FakeParamiko


class FakeServerTestCase(unittest.TestCase):
    """Replaces the real FTP and SFTP connections with the fake server, and isolates the file system"""

    def setUp(self):
        FakeServer.nlst_full_path = False
        FakeServer.nlst_dots = False
        FakeServer.fail_delete = False
        FakeServer.fail_store = False
        FakeServer.instances = []
        FakeParamiko.imports = 0
        FakeSSHClient.fail_connect = False

        self.ftp_class = ftplib.FTP
        self.ftp_tls_class = ftplib.FTP_TLS
        self.paramiko_import = RobotSFTP._Paramiko
        ftplib.FTP = FakeFTP
        ftplib.FTP_TLS = FakeFTP_TLS
        RobotSFTP._Paramiko = staticmethod(FakeParamiko.Import)

        from robodk import robomath
        self.pause = robomath.pause
        robomath.pause = lambda seconds: None  # do not slow down the tests

        self.tempdir = tempfile.mkdtemp(prefix='robodk_ftp_test_')
        self.cwd = os.getcwd()

    def tearDown(self):
        from robodk import robomath
        ftplib.FTP = self.ftp_class
        ftplib.FTP_TLS = self.ftp_tls_class
        RobotSFTP._Paramiko = self.paramiko_import
        robomath.pause = self.pause
        os.chdir(self.cwd)
        shutil.rmtree(self.tempdir, ignore_errors=True)

    #----------------------------------------------
    def newfile(self, name, content=b'MODULE MainModule\nENDMODULE\n', folder=None):
        filepath = os.path.join(self.tempdir if folder is None else folder, name)
        with open(filepath, 'wb') as f:
            f.write(content)
        return filepath

    def newfolder(self, name, parent=None):
        folderpath = os.path.join(self.tempdir if parent is None else parent, name)
        os.makedirs(folderpath)
        return folderpath

    def server(self):
        """The (only) server that was connected to"""
        self.assertEqual(len(FakeServer.instances), 1, 'Expected exactly one connection')
        return FakeServer.instances[0]


class TransferTests:
    """Transfer tests that must pass identically over every protocol.
    Mixed into one test case per protocol: it is not a TestCase itself."""

    CLIENT = None  # RobotFTP or RobotSFTP
    CONNECTION = None  # FakeFTP or FakeSFTP, to build a client from an existing connection
    UPLOAD = None  # UploadFTP or UploadSFTP
    UPLOAD_FILE = None  # UploadFileFTP or UploadFileSFTP
    UPLOAD_DIR = None  # UploadDirFTP or UploadDirSFTP

    def client(self, **kwargs):
        return self.CLIENT('192.168.0.1', 'user', 'pass', **kwargs)

    #----------------------------------------------
    # Connection
    def test_operations_connect_when_needed(self):
        # The connection is established by the first operation that needs it, and it is then reused
        ftp = self.client()
        try:
            self.assertTrue(ftp.UploadFile(self.newfile('main1.mod', b'1'), '/prog'))
            self.assertTrue(ftp.UploadFile(self.newfile('main2.mod', b'2'), '/prog'))
            self.assertTrue(ftp.RemoveFile('/prog/main2.mod'))
        finally:
            ftp.Disconnect()

        self.assertEqual(self.server().files, {'/prog/main1.mod': b'1'}, 'Expected a single connection for every operation')

    #----------------------------------------------
    # UploadFile
    def test_upload_file(self):
        self.assertTrue(self.UPLOAD_FILE(self.newfile('main.mod'), '192.168.0.1', '/prog', 'user', 'pass'))
        server = self.server()
        self.assertEqual(server.files, {'/prog/main.mod': b'MODULE MainModule\nENDMODULE\n'})
        self.assertTrue(server.closed, 'The connection must be closed')

    def test_upload_file_overwrites_the_remote_file(self):
        with self.client() as ftp:
            self.assertTrue(ftp.Connect())
            ftp.ftp.files['/prog/main.mod'] = b'old content'
            self.assertTrue(ftp.UploadFile(self.newfile('main.mod', b'new content'), '/prog'))
            self.assertEqual(ftp.ftp.files, {'/prog/main.mod': b'new content'})

    def test_upload_file_not_found(self):
        self.assertFalse(self.UPLOAD_FILE(os.path.join(self.tempdir, 'missing.mod'), '192.168.0.1', '/prog', 'user', 'pass'))
        self.assertEqual(len(FakeServer.instances), 0, 'It must not connect at all if the local file does not exist')

    def test_upload_file_invalid_remote_path(self):
        self.assertFalse(self.UPLOAD_FILE(self.newfile('main.mod'), '192.168.0.1', '/not_a_folder', 'user', 'pass'))
        self.assertTrue(self.server().closed, 'The connection must be closed on failure')

    def test_upload_file_transfer_error(self):
        FakeServer.fail_store = True
        self.assertFalse(self.UPLOAD_FILE(self.newfile('main.mod'), '192.168.0.1', '/prog', 'user', 'pass'))
        self.assertTrue(self.server().closed, 'The connection must be closed on failure')

    def test_upload_file_undeletable_remote_file(self):
        # A controller that does not allow deleting files must not prevent the transfer
        FakeServer.fail_delete = True
        self.assertTrue(self.UPLOAD_FILE(self.newfile('main.mod'), '192.168.0.1', '/prog', 'user', 'pass'))
        self.assertIn('/prog/main.mod', self.server().files)

    #----------------------------------------------
    # UploadDir
    def test_upload_folder(self):
        folder = self.newfolder('Program')
        self.newfile('main.mod', b'main', folder)
        self.newfile('sub1.mod', b'sub1', self.newfolder('sub', folder))

        self.assertTrue(self.UPLOAD_DIR(folder, '192.168.0.1', '/prog', 'user', 'pass'))
        server = self.server()
        self.assertEqual(server.files, {'/prog/Program/main.mod': b'main', '/prog/Program/sub/sub1.mod': b'sub1'})
        self.assertTrue(server.closed)

    def test_upload_folder_keeps_the_local_working_directory(self):
        folder = self.newfolder('Program')
        self.newfile('main.mod', b'main', folder)
        self.newfolder('sub', folder)
        self.assertTrue(self.UPLOAD_DIR(folder, '192.168.0.1', '/prog', 'user', 'pass'))
        self.assertEqual(os.getcwd(), self.cwd, 'The local working directory must not be modified')

    def test_upload_folder_deletes_the_existing_remote_folder(self):
        folder = self.newfolder('Program')
        self.newfile('main.mod', b'new', folder)
        with self.client() as ftp:
            self.assertTrue(ftp.Connect())
            ftp.ftp.folders.update({'/prog/Program', '/prog/Program/old_sub'})
            ftp.ftp.files['/prog/Program/obsolete.mod'] = b'obsolete'
            ftp.ftp.files['/prog/Program/old_sub/obsolete.mod'] = b'obsolete'

            self.assertTrue(ftp.UploadDir(folder, '/prog'))
            self.assertEqual(ftp.ftp.files, {'/prog/Program/main.mod': b'new'})
            self.assertNotIn('/prog/Program/old_sub', ftp.ftp.folders)

    def test_upload_folder_undeletable_remote_folder(self):
        # The transfer must go through even if the existing remote folder can not be deleted
        FakeServer.fail_delete = True
        folder = self.newfolder('Program')
        self.newfile('main.mod', b'new', folder)
        with self.client() as ftp:
            self.assertTrue(ftp.Connect())
            ftp.ftp.folders.add('/prog/Program')
            ftp.ftp.files['/prog/Program/obsolete.mod'] = b'obsolete'

            self.assertTrue(ftp.UploadDir(folder, '/prog'))
            self.assertIn('/prog/Program/main.mod', ftp.ftp.files)

    def test_upload_folder_not_found(self):
        self.assertFalse(self.UPLOAD_DIR(os.path.join(self.tempdir, 'missing'), '192.168.0.1', '/prog', 'user', 'pass'))
        self.assertEqual(len(FakeServer.instances), 0, 'It must not connect at all if the local folder does not exist')

    def test_upload_folder_invalid_remote_path(self):
        folder = self.newfolder('Program')
        self.newfile('main.mod', b'main', folder)
        self.assertFalse(self.UPLOAD_DIR(folder, '192.168.0.1', '/not_a_folder', 'user', 'pass'))
        self.assertTrue(self.server().closed, 'The connection must be closed on failure')

    def test_upload_folder_transfer_error(self):
        FakeServer.fail_store = True
        folder = self.newfolder('Program')
        self.newfile('main.mod', b'main', folder)
        self.assertFalse(self.UPLOAD_DIR(folder, '192.168.0.1', '/prog', 'user', 'pass'))
        self.assertTrue(self.server().closed, 'The connection must be closed on failure')

    def test_upload_empty_folder(self):
        self.assertTrue(self.UPLOAD_DIR(self.newfolder('Program'), '192.168.0.1', '/prog', 'user', 'pass'))
        self.assertIn('/prog/Program', self.server().folders)

    #----------------------------------------------
    # RemoveDir
    def test_remove_dir_recursively(self):
        server = self.CONNECTION()
        server.folders.update({'/prog/Program', '/prog/Program/sub'})
        server.files['/prog/Program/sub/main.mod'] = b'main'
        server.files['/prog/Program/main.mod'] = b'main'

        self.assertTrue(self.CLIENT.FromConnection(server).RemoveDir('/prog/Program'))
        self.assertEqual(server.files, {})
        self.assertEqual(server.folders, {'/', '/prog'})

    def test_remove_dir_missing_folder(self):
        self.assertFalse(self.CLIENT.FromConnection(self.CONNECTION()).RemoveDir('/prog/missing'))

    def test_remove_dir_max_depth(self):
        server = self.CONNECTION()
        for i in range(5):
            server.folders.add('/prog/Program' + '/sub' * i)

        self.assertFalse(self.CLIENT.FromConnection(server).RemoveDir('/prog/Program', max_depth=2))
        self.assertIn('/prog/Program/sub/sub/sub', server.folders, 'The recursion must stop at the maximum depth')

    #----------------------------------------------
    # Upload (file, folder or list)
    def test_upload_program_file(self):
        self.assertTrue(self.UPLOAD(self.newfile('main.mod', b'main'), '192.168.0.1', '/prog', 'user', 'pass', 0))
        self.assertEqual(self.server().files, {'/prog/main.mod': b'main'})

    def test_upload_program_folder(self):
        folder = self.newfolder('Program')
        self.newfile('main.mod', b'main', folder)
        self.assertTrue(self.UPLOAD(folder, '192.168.0.1', '/prog', 'user', 'pass', 0))
        self.assertEqual(self.server().files, {'/prog/Program/main.mod': b'main'})

    def test_upload_program_list(self):
        folder = self.newfolder('Program')
        self.newfile('sub.mod', b'sub', folder)
        files = [self.newfile('main1.mod', b'1'), self.newfile('main2.mod', b'2'), folder]

        self.assertTrue(self.UPLOAD(files, '192.168.0.1', '/prog', 'user', 'pass', 0))
        self.assertEqual(self.server().files, {
            '/prog/main1.mod': b'1',
            '/prog/main2.mod': b'2',
            '/prog/Program/sub.mod': b'sub',
        })

    def test_upload_program_list_partial_failure(self):
        files = [self.newfile('main1.mod', b'1'), os.path.join(self.tempdir, 'missing.mod')]
        self.assertFalse(self.UPLOAD(files, '192.168.0.1', '/prog', 'user', 'pass', 0))
        self.assertEqual(self.server().files, {'/prog/main1.mod': b'1'}, 'The transfer must not stop at the first failure')

    def test_upload_program_empty_list(self):
        self.assertFalse(self.UPLOAD([], '192.168.0.1', '/prog', 'user', 'pass', 0))
        self.assertEqual(len(FakeServer.instances), 0)

    def test_upload_program_missing_file(self):
        # A missing file must not be transferred as a folder
        self.assertFalse(self.UPLOAD(os.path.join(self.tempdir, 'missing.mod'), '192.168.0.1', '/prog', 'user', 'pass', 0))
        self.assertEqual(len(FakeServer.instances), 0, 'It must not connect at all if the file does not exist')

    def test_upload_program_invalid_program(self):
        for invalid in [None, '', 0]:
            self.assertFalse(self.UPLOAD(invalid, '192.168.0.1', '/prog', 'user', 'pass', 0))


class TestRobotFTP(TransferTests, FakeServerTestCase):
    """The transfer matrix over FTP, plus the FTP specific behaviors"""

    CLIENT = RobotFTP
    CONNECTION = FakeFTP
    UPLOAD = staticmethod(UploadFTP)
    UPLOAD_FILE = staticmethod(UploadFileFTP)
    UPLOAD_DIR = staticmethod(UploadDirFTP)

    #----------------------------------------------
    # Connection
    def test_context_manager_closes_the_connection(self):
        with RobotFTP('192.168.0.1', 'user', 'pass') as ftp:
            self.assertIsNone(ftp.ftp, 'It must not connect before it is needed')
            self.assertTrue(ftp.Connect())
            self.assertIsNotNone(ftp.ftp.timeout, 'A timeout must be used to avoid blocking forever')
        self.assertTrue(self.server().closed)

    def test_connection_failed(self):

        def connection_refused(*args, **kwargs):
            raise OSError('Connection refused')

        ftplib.FTP = connection_refused
        with RobotFTP('192.168.0.1', 'user', 'pass') as ftp:
            self.assertFalse(ftp.Connect())
            self.assertIsNone(ftp.ftp)
            self.assertFalse(ftp.UploadFile(self.newfile('main.mod'), '/prog'), 'Nothing can be transferred without a connection')

    def test_custom_port(self):
        self.assertTrue(UploadFileFTP(self.newfile('main.mod'), '192.168.0.1', '/prog', 'user', 'pass'))
        self.assertIsNone(self.server().port, 'The default port of ftplib must be used when no port is given')

        FakeServer.instances = []
        with RobotFTP('192.168.0.1', 'user', 'pass', port=2121) as ftp:
            self.assertTrue(ftp.Connect())
            self.assertEqual(ftp.ftp.port, 2121)
            self.assertTrue(ftp.ftp.logged_in)

    #----------------------------------------------
    # Paths
    def test_path_helpers(self):
        self.assertEqual(RobotFTP._Join('/prog', 'main.mod'), '/prog/main.mod')
        self.assertEqual(RobotFTP._Join('/prog/', 'main.mod'), '/prog/main.mod')
        self.assertEqual(RobotFTP._Join('', 'main.mod'), 'main.mod')
        self.assertEqual(RobotFTP._Name('main.mod'), 'main.mod')
        self.assertEqual(RobotFTP._Name('/prog/main.mod'), 'main.mod')
        self.assertEqual(RobotFTP._Name('/prog/sub/'), 'sub')
        self.assertEqual(RobotFTP._Name('C:\\RoboDK\\main.mod'), 'main.mod')
        self.assertEqual(RobotFTP._Check('main.mod'), 'main.mod')
        for invalid in ['', None, 'main.mod\r\nDELE /prog/important.mod']:
            with self.assertRaises(ValueError):
                RobotFTP._Check(invalid)

    def test_ftp_commands_can_not_be_injected(self):
        # FTP commands are line based: a name with a new line character could inject arbitrary FTP commands
        with RobotFTP('192.168.0.1', 'user', 'pass') as ftp:
            self.assertTrue(ftp.Connect())
            with self.assertRaises(ValueError):
                ftp._Store(self.newfile('main.mod'), 'main.mod\r\nDELE /prog/important.mod')

            with self.assertRaises(ValueError):
                ftp._Mkdir('sub\r\nDELE /prog/important.mod')

            self.assertEqual(ftp.ftp.files, {}, 'Nothing must be transferred with an invalid name')

    def test_upload_folder_when_the_server_returns_full_paths(self):
        # Some FTP servers return the complete path (and '.' and '..') when a folder is listed
        FakeServer.nlst_full_path = True
        FakeServer.nlst_dots = True
        folder = self.newfolder('Program')
        self.newfile('main.mod', b'new', folder)
        with RobotFTP('192.168.0.1', 'user', 'pass') as ftp:
            self.assertTrue(ftp.Connect())
            ftp.ftp.folders.add('/prog/Program')
            ftp.ftp.files['/prog/Program/obsolete.mod'] = b'obsolete'

            self.assertTrue(ftp.UploadDir(folder, '/prog'))
            self.assertEqual(ftp.ftp.files, {'/prog/Program/main.mod': b'new'})

    #----------------------------------------------
    # The RemoveFileFTP / RemoveDirFTP functions take an ftplib.FTP connection
    def test_remove_file_function(self):
        server = FakeFTP()
        server.files['/prog/main.mod'] = b'main'
        self.assertTrue(RemoveFileFTP(server, '/prog/main.mod'))
        self.assertEqual(server.files, {})
        self.assertFalse(RemoveFileFTP(server, '/prog/main.mod'), 'The file no longer exists')

    def test_remove_dir_function_restores_the_remote_working_folder(self):
        server = FakeFTP()
        server.folders.update({'/prog/Program', '/prog/Program/sub'})
        server.files['/prog/Program/sub/main.mod'] = b'main'
        server.cwd('/prog')

        self.assertTrue(RemoveDirFTP(server, '/prog/Program'))
        self.assertEqual(server.files, {})
        self.assertEqual(server.folders, {'/', '/prog'})
        self.assertEqual(server.pwd(), '/prog')


class TestRobotSFTP(TransferTests, FakeServerTestCase):
    """The same transfer matrix over SFTP, plus the SFTP specific behaviors"""

    CLIENT = RobotSFTP
    CONNECTION = FakeSFTP
    UPLOAD = staticmethod(UploadSFTP)
    UPLOAD_FILE = staticmethod(UploadFileSFTP)
    UPLOAD_DIR = staticmethod(UploadDirSFTP)

    def ssh(self):
        """The (only) SSH client that was created"""
        server = self.server()
        self.assertIsInstance(server, FakeSFTP)
        return server

    #----------------------------------------------
    # paramiko is installed and imported only when it is needed
    def test_paramiko_is_not_imported_until_a_transfer_is_attempted(self):
        sftp = RobotSFTP('192.168.0.1', 'user', 'pass')
        self.assertEqual(FakeParamiko.imports, 0, 'Creating the object must not import paramiko')

        self.assertFalse(sftp.UploadFile(os.path.join(self.tempdir, 'missing.mod'), '/prog'))
        self.assertEqual(FakeParamiko.imports, 0, 'A local file that does not exist must not import paramiko')

        self.assertTrue(sftp.UploadFile(self.newfile('main.mod'), '/prog'))
        self.assertEqual(FakeParamiko.imports, 1, 'paramiko must be imported to transfer')

        self.assertTrue(sftp.UploadFile(self.newfile('main2.mod'), '/prog'))
        sftp.Disconnect()
        self.assertEqual(FakeParamiko.imports, 1, 'paramiko must not be imported again for the same connection')

    def test_paramiko_not_available(self):
        # A missing paramiko that can not be installed must be reported as a failed connection, not a traceback
        def no_paramiko():
            raise ImportError("No module named 'paramiko'")

        RobotSFTP._Paramiko = staticmethod(no_paramiko)
        with RobotSFTP('192.168.0.1', 'user', 'pass') as sftp:
            self.assertFalse(sftp.Connect())
            self.assertFalse(sftp.UploadFile(self.newfile('main.mod'), '/prog'))
            self.assertIsNone(sftp.ftp)

    #----------------------------------------------
    # Connection
    def test_connects_over_ssh_with_the_default_port(self):
        with RobotSFTP('192.168.0.1', 'user', 'pass') as sftp:
            self.assertTrue(sftp.Connect())
            args = sftp.ssh.connect_args
            self.assertEqual(args['hostname'], '192.168.0.1')
            self.assertEqual(args['port'], 22)
            self.assertEqual(args['username'], 'user')
            self.assertEqual(args['password'], 'pass')
            self.assertEqual(args['timeout'], RobotSFTP.TIMEOUT)
            self.assertFalse(args['look_for_keys'], 'The given password must be used, not a key of the user running the script')

        self.assertTrue(self.server().closed, 'The SFTP session must be closed')

    def test_custom_port(self):
        with RobotSFTP('192.168.0.1', 'user', 'pass', port=2222) as sftp:
            self.assertTrue(sftp.Connect())
            self.assertEqual(sftp.ssh.connect_args['port'], 2222)

    def test_disconnect_closes_the_ssh_session(self):
        with RobotSFTP('192.168.0.1', 'user', 'pass') as sftp:
            self.assertTrue(sftp.Connect())
            ssh = sftp.ssh

        self.assertTrue(ssh.closed, 'The SSH session must be closed, not only the SFTP channel')
        self.assertTrue(self.server().closed, 'The SFTP channel must be closed')
        self.assertIsNone(sftp.ssh)

    def test_connection_failed(self):
        FakeSSHClient.fail_connect = True
        with RobotSFTP('192.168.0.1', 'user', 'pass') as sftp:
            self.assertFalse(sftp.Connect())
            self.assertIsNone(sftp.ftp)
            self.assertFalse(sftp.UploadFile(self.newfile('main.mod'), '/prog'), 'Nothing can be transferred without a connection')

    #----------------------------------------------
    # Host keys
    def test_any_host_key_is_accepted_by_default(self):
        with RobotSFTP('192.168.0.1', 'user', 'pass') as sftp:
            self.assertTrue(sftp.Connect())
            self.assertIsInstance(sftp.ssh.policy, FakeAutoAddPolicy)
            self.assertFalse(sftp.ssh.system_host_keys_loaded)

    def test_host_key_can_be_verified(self):
        with RobotSFTP('192.168.0.1', 'user', 'pass', verify_host_key=True) as sftp:
            self.assertTrue(sftp.Connect())
            self.assertIsInstance(sftp.ssh.policy, FakeRejectPolicy)
            self.assertTrue(sftp.ssh.system_host_keys_loaded, 'The known hosts of the system must be used')

    #----------------------------------------------
    def test_folders_are_detected_with_stat(self):
        # SFTP has no 'cwd into it to find out': the remote working folder must not be moved around
        with RobotSFTP('192.168.0.1', 'user', 'pass') as sftp:
            self.assertTrue(sftp.Connect())
            sftp.ftp.folders.add('/prog/Program')
            sftp.ftp.files['/prog/main.mod'] = b'main'
            sftp._Cwd('/prog')

            self.assertTrue(sftp._IsDir('/prog/Program'))
            self.assertFalse(sftp._IsDir('/prog/main.mod'))
            self.assertFalse(sftp._IsDir('/prog/missing'))
            self.assertEqual(sftp.ftp.getcwd(), '/prog', 'The remote working folder must not change')


class TestRobotFTPS(FakeServerTestCase):
    """FTPS only differs in how the connection is established"""

    def test_ftps_encrypts_the_data_channel(self):
        with RobotFTPS('192.168.0.1', 'user', 'pass') as ftps:
            self.assertTrue(ftps.Connect())
            self.assertIsInstance(ftps.ftp, FakeFTP_TLS)
            self.assertTrue(ftps.ftp.encrypted, 'prot_p() must be called, otherwise only the commands are encrypted')
            self.assertEqual(ftps.ftp.port, 21)
            self.assertTrue(ftps.ftp.logged_in)

            self.assertTrue(ftps.UploadFile(self.newfile('main.mod', b'main'), '/prog'))
            self.assertEqual(ftps.ftp.files, {'/prog/main.mod': b'main'})

    def test_ftps_custom_port(self):
        with RobotFTPS('192.168.0.1', 'user', 'pass', port=990) as ftps:
            self.assertTrue(ftps.Connect())
            self.assertEqual(ftps.ftp.port, 990)


if __name__ == '__main__':
    unittest.main()
