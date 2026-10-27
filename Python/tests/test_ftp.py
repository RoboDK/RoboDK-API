"""Tests for the FTP transfer tools of robodk.robofileio (RobotFTP and the UploadFTP functions).

These tests are standalone: RoboDK does not need to be running.
A fake FTP server (in memory) replaces ftplib.FTP so that the complete transfer logic
can be verified without a real robot controller.
"""

import ftplib
import os
import shutil
import sys
import tempfile
import unittest

# Test the robodk package of this repository, not a copy that may be installed in site-packages
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from robodk.robofileio import RobotFTP, UploadFTP, UploadFileFTP, UploadDirFTP, RemoveFileFTP, RemoveDirFTP


class FakeFTP:
    """Minimal in-memory FTP server simulation.
    The remote file system is a set of folders and a dict of files (absolute POSIX paths)."""

    # Set by the tests to simulate server specific behaviors
    nlst_full_path = False  # some FTP servers return the complete path instead of the file name
    nlst_dots = False  # some FTP servers include '.' and '..' when a folder is listed
    fail_delete = False  # some controllers do not allow deleting files
    fail_store = False  # the connection may drop during a transfer
    instances = []

    def __init__(self, host='', user='', passwd='', acct='', timeout=None, **kwargs):
        self.host = host
        self.user = user
        self.timeout = timeout
        self.closed = False
        self.working_folder = '/'
        self.folders = {'/', '/prog'}
        self.files = {}
        FakeFTP.instances.append(self)

    #----------------------------------------------
    def pwd(self):
        return self.working_folder

    def cwd(self, path):
        folder = self._abs(path)
        if folder not in self.folders:
            raise ftplib.error_perm('550 %s: No such file or directory' % path)
        self.working_folder = folder

    def nlst(self, path=''):
        folder = self._abs(path)
        if folder not in self.folders:
            raise ftplib.error_perm('550 %s: No such file or directory' % path)

        names = ['.', '..'] if self.nlst_dots else []
        prefix = folder.rstrip('/') + '/'
        for item in sorted(self.folders | set(self.files)):
            if not item.startswith(prefix) or '/' in item[len(prefix):]:
                continue  # not a direct child
            names.append(item if self.nlst_full_path else item[len(prefix):])

        return names

    def delete(self, filepath):
        if self.fail_delete:
            raise ftplib.error_perm('550 Permission denied')
        if self._abs(filepath) not in self.files:
            raise ftplib.error_perm('550 %s: No such file or directory' % filepath)
        self.files.pop(self._abs(filepath))

    def mkd(self, path):
        folder = self._abs(path)
        if folder in self.folders or folder in self.files:
            raise ftplib.error_perm('550 %s: File exists' % path)
        if self._parent(folder) not in self.folders:
            raise ftplib.error_perm('550 %s: No such file or directory' % path)
        self.folders.add(folder)

    def rmd(self, path):
        folder = self._abs(path)
        if folder not in self.folders:
            raise ftplib.error_perm('550 %s: No such file or directory' % path)
        if self.nlst(folder):
            raise ftplib.error_perm('550 %s: Directory not empty' % path)
        self.folders.discard(folder)

    def storbinary(self, cmd, fp, blocksize=8192):
        if self.fail_store:
            raise ftplib.error_temp('426 Connection closed, transfer aborted')
        if not cmd.startswith('STOR '):
            raise ftplib.error_perm('500 Unknown command: %s' % cmd)
        filepath = self._abs(cmd[len('STOR '):])
        if self._parent(filepath) not in self.folders:
            raise ftplib.error_perm('550 %s: No such file or directory' % cmd)
        self.files[filepath] = fp.read()

    def quit(self):
        self.closed = True

    def close(self):
        self.closed = True

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


class TestRobotFTP(unittest.TestCase):

    def setUp(self):
        FakeFTP.nlst_full_path = False
        FakeFTP.nlst_dots = False
        FakeFTP.fail_delete = False
        FakeFTP.fail_store = False
        FakeFTP.instances = []
        self.ftp_class = ftplib.FTP
        ftplib.FTP = FakeFTP

        from robodk import robomath
        self.pause = robomath.pause
        robomath.pause = lambda seconds: None  # do not slow down the tests

        self.tempdir = tempfile.mkdtemp(prefix='robodk_ftp_test_')
        self.cwd = os.getcwd()

    def tearDown(self):
        from robodk import robomath
        ftplib.FTP = self.ftp_class
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
        """The (only) FTP server that was connected to"""
        self.assertEqual(len(FakeFTP.instances), 1, 'Expected exactly one FTP connection')
        return FakeFTP.instances[0]

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

    def test_operations_connect_when_needed(self):
        # The connection is established by the first operation that needs it, and it is then reused
        ftp = RobotFTP('192.168.0.1', 'user', 'pass')
        try:
            self.assertTrue(ftp.UploadFile(self.newfile('main1.mod', b'1'), '/prog'))
            self.assertTrue(ftp.UploadFile(self.newfile('main2.mod', b'2'), '/prog'))
            self.assertTrue(ftp.RemoveFile('/prog/main2.mod'))
        finally:
            ftp.Disconnect()

        self.assertEqual(self.server().files, {'/prog/main1.mod': b'1'}, 'Expected a single connection for every operation')

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
                ftp._Store(self.newfile('main.mod'), 'main.mod' + chr(13) + chr(10) + 'DELE /prog/important.mod')

            with self.assertRaises(ValueError):
                ftp._Mkdir('sub' + chr(13) + chr(10) + 'DELE /prog/important.mod')

            self.assertEqual(ftp.ftp.files, {}, 'Nothing must be transferred with an invalid name')

    #----------------------------------------------
    # UploadFile
    def test_upload_file(self):
        self.assertTrue(UploadFileFTP(self.newfile('main.mod'), '192.168.0.1', '/prog', 'user', 'pass'))
        server = self.server()
        self.assertEqual(server.files, {'/prog/main.mod': b'MODULE MainModule\nENDMODULE\n'})
        self.assertTrue(server.closed, 'The connection must be closed')

    def test_upload_file_overwrites_the_remote_file(self):
        with RobotFTP('192.168.0.1', 'user', 'pass') as ftp:
            self.assertTrue(ftp.Connect())
            ftp.ftp.files['/prog/main.mod'] = b'old content'
            self.assertTrue(ftp.UploadFile(self.newfile('main.mod', b'new content'), '/prog'))
            self.assertEqual(ftp.ftp.files, {'/prog/main.mod': b'new content'})

    def test_upload_file_not_found(self):
        self.assertFalse(UploadFileFTP(os.path.join(self.tempdir, 'missing.mod'), '192.168.0.1', '/prog', 'user', 'pass'))
        self.assertEqual(len(FakeFTP.instances), 0, 'It must not connect at all if the local file does not exist')

    def test_upload_file_invalid_remote_path(self):
        self.assertFalse(UploadFileFTP(self.newfile('main.mod'), '192.168.0.1', '/not_a_folder', 'user', 'pass'))
        self.assertTrue(self.server().closed, 'The connection must be closed on failure')

    def test_upload_file_transfer_error(self):
        FakeFTP.fail_store = True
        self.assertFalse(UploadFileFTP(self.newfile('main.mod'), '192.168.0.1', '/prog', 'user', 'pass'))
        self.assertTrue(self.server().closed, 'The connection must be closed on failure')

    def test_upload_file_undeletable_remote_file(self):
        # A controller that does not allow deleting files must not prevent the transfer
        FakeFTP.fail_delete = True
        self.assertTrue(UploadFileFTP(self.newfile('main.mod'), '192.168.0.1', '/prog', 'user', 'pass'))
        self.assertIn('/prog/main.mod', self.server().files)

    #----------------------------------------------
    # UploadDir
    def test_upload_folder(self):
        folder = self.newfolder('Program')
        self.newfile('main.mod', b'main', folder)
        self.newfile('sub1.mod', b'sub1', self.newfolder('sub', folder))

        self.assertTrue(UploadDirFTP(folder, '192.168.0.1', '/prog', 'user', 'pass'))
        server = self.server()
        self.assertEqual(server.files, {'/prog/Program/main.mod': b'main', '/prog/Program/sub/sub1.mod': b'sub1'})
        self.assertTrue(server.closed)

    def test_upload_folder_keeps_the_local_working_directory(self):
        folder = self.newfolder('Program')
        self.newfile('main.mod', b'main', folder)
        self.newfolder('sub', folder)
        self.assertTrue(UploadDirFTP(folder, '192.168.0.1', '/prog', 'user', 'pass'))
        self.assertEqual(os.getcwd(), self.cwd, 'The local working directory must not be modified')

    def test_upload_folder_deletes_the_existing_remote_folder(self):
        folder = self.newfolder('Program')
        self.newfile('main.mod', b'new', folder)
        with RobotFTP('192.168.0.1', 'user', 'pass') as ftp:
            self.assertTrue(ftp.Connect())
            ftp.ftp.folders.update({'/prog/Program', '/prog/Program/old_sub'})
            ftp.ftp.files['/prog/Program/obsolete.mod'] = b'obsolete'
            ftp.ftp.files['/prog/Program/old_sub/obsolete.mod'] = b'obsolete'

            self.assertTrue(ftp.UploadDir(folder, '/prog'))
            self.assertEqual(ftp.ftp.files, {'/prog/Program/main.mod': b'new'})
            self.assertNotIn('/prog/Program/old_sub', ftp.ftp.folders)

    def test_upload_folder_when_the_server_returns_full_paths(self):
        # Some FTP servers return the complete path (and '.' and '..') when a folder is listed
        FakeFTP.nlst_full_path = True
        FakeFTP.nlst_dots = True
        folder = self.newfolder('Program')
        self.newfile('main.mod', b'new', folder)
        with RobotFTP('192.168.0.1', 'user', 'pass') as ftp:
            self.assertTrue(ftp.Connect())
            ftp.ftp.folders.add('/prog/Program')
            ftp.ftp.files['/prog/Program/obsolete.mod'] = b'obsolete'

            self.assertTrue(ftp.UploadDir(folder, '/prog'))
            self.assertEqual(ftp.ftp.files, {'/prog/Program/main.mod': b'new'})

    def test_upload_folder_undeletable_remote_folder(self):
        # The transfer must go through even if the existing remote folder can not be deleted
        FakeFTP.fail_delete = True
        folder = self.newfolder('Program')
        self.newfile('main.mod', b'new', folder)
        with RobotFTP('192.168.0.1', 'user', 'pass') as ftp:
            self.assertTrue(ftp.Connect())
            ftp.ftp.folders.add('/prog/Program')
            ftp.ftp.files['/prog/Program/obsolete.mod'] = b'obsolete'

            self.assertTrue(ftp.UploadDir(folder, '/prog'))
            self.assertIn('/prog/Program/main.mod', ftp.ftp.files)

    def test_upload_folder_not_found(self):
        self.assertFalse(UploadDirFTP(os.path.join(self.tempdir, 'missing'), '192.168.0.1', '/prog', 'user', 'pass'))
        self.assertEqual(len(FakeFTP.instances), 0, 'It must not connect at all if the local folder does not exist')

    def test_upload_folder_invalid_remote_path(self):
        folder = self.newfolder('Program')
        self.newfile('main.mod', b'main', folder)
        self.assertFalse(UploadDirFTP(folder, '192.168.0.1', '/not_a_folder', 'user', 'pass'))
        self.assertTrue(self.server().closed, 'The connection must be closed on failure')

    def test_upload_folder_transfer_error(self):
        FakeFTP.fail_store = True
        folder = self.newfolder('Program')
        self.newfile('main.mod', b'main', folder)
        self.assertFalse(UploadDirFTP(folder, '192.168.0.1', '/prog', 'user', 'pass'))
        self.assertTrue(self.server().closed, 'The connection must be closed on failure')

    def test_upload_empty_folder(self):
        self.assertTrue(UploadDirFTP(self.newfolder('Program'), '192.168.0.1', '/prog', 'user', 'pass'))
        self.assertIn('/prog/Program', self.server().folders)

    #----------------------------------------------
    # RemoveFile / RemoveDir
    def test_remove_file(self):
        server = FakeFTP()
        server.files['/prog/main.mod'] = b'main'
        self.assertTrue(RemoveFileFTP(server, '/prog/main.mod'))
        self.assertEqual(server.files, {})
        self.assertFalse(RemoveFileFTP(server, '/prog/main.mod'), 'The file no longer exists')

    def test_remove_dir_restores_the_remote_working_folder(self):
        server = FakeFTP()
        server.folders.update({'/prog/Program', '/prog/Program/sub'})
        server.files['/prog/Program/sub/main.mod'] = b'main'
        server.cwd('/prog')

        self.assertTrue(RemoveDirFTP(server, '/prog/Program'))
        self.assertEqual(server.files, {})
        self.assertEqual(server.folders, {'/', '/prog'})
        self.assertEqual(server.pwd(), '/prog')

    def test_remove_dir_missing_folder(self):
        self.assertFalse(RemoveDirFTP(FakeFTP(), '/prog/missing'))

    def test_remove_dir_max_depth(self):
        server = FakeFTP()
        for i in range(5):
            server.folders.add('/prog/Program' + '/sub' * i)

        self.assertFalse(RobotFTP.FromConnection(server).RemoveDir('/prog/Program', max_depth=2))
        self.assertIn('/prog/Program/sub/sub/sub', server.folders, 'The recursion must stop at the maximum depth')

    #----------------------------------------------
    # UploadFTP
    def test_upload_ftp_file(self):
        self.assertTrue(UploadFTP(self.newfile('main.mod', b'main'), '192.168.0.1', '/prog', 'user', 'pass', 0))
        self.assertEqual(self.server().files, {'/prog/main.mod': b'main'})

    def test_upload_ftp_folder(self):
        folder = self.newfolder('Program')
        self.newfile('main.mod', b'main', folder)
        self.assertTrue(UploadFTP(folder, '192.168.0.1', '/prog', 'user', 'pass', 0))
        self.assertEqual(self.server().files, {'/prog/Program/main.mod': b'main'})

    def test_upload_ftp_list(self):
        folder = self.newfolder('Program')
        self.newfile('sub.mod', b'sub', folder)
        files = [self.newfile('main1.mod', b'1'), self.newfile('main2.mod', b'2'), folder]

        self.assertTrue(UploadFTP(files, '192.168.0.1', '/prog', 'user', 'pass', 0))
        self.assertEqual(self.server().files, {
            '/prog/main1.mod': b'1',
            '/prog/main2.mod': b'2',
            '/prog/Program/sub.mod': b'sub',
        })

    def test_upload_ftp_list_partial_failure(self):
        files = [self.newfile('main1.mod', b'1'), os.path.join(self.tempdir, 'missing.mod')]
        self.assertFalse(UploadFTP(files, '192.168.0.1', '/prog', 'user', 'pass', 0))
        self.assertEqual(self.server().files, {'/prog/main1.mod': b'1'}, 'The transfer must not stop at the first failure')

    def test_upload_ftp_empty_list(self):
        self.assertFalse(UploadFTP([], '192.168.0.1', '/prog', 'user', 'pass', 0))
        self.assertEqual(len(FakeFTP.instances), 0)

    def test_upload_ftp_missing_file(self):
        # A missing file must not be transferred as a folder
        self.assertFalse(UploadFTP(os.path.join(self.tempdir, 'missing.mod'), '192.168.0.1', '/prog', 'user', 'pass', 0))
        self.assertEqual(len(FakeFTP.instances), 0, 'It must not connect at all if the file does not exist')

    def test_upload_ftp_invalid_program(self):
        for invalid in [None, '', 0]:
            self.assertFalse(UploadFTP(invalid, '192.168.0.1', '/prog', 'user', 'pass', 0))


if __name__ == '__main__':
    unittest.main()
