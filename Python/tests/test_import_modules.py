
import unittest
import importlib

class TestImport(unittest.TestCase):

    modules = ['robodk.robolink', 'robodk.robomath','robodk.robodialogs','robodk.robofileio','robodk.roboapps']
    legacy = ['robodk', 'robolink']

    def setUp(self):
        import sys

        for m in self.legacy + self.modules:
            if m in sys.modules:
                print("Removing " + m + " from sys.modules")
                sys.modules.pop(m)
                
        return super().setUp()

    def test_import_all(self):
        for m in self.modules:
            print("-> Importing " + m)
            try:
                importlib.import_module(m)
            except :
                self.assertTrue(False)
            self.setUp()

    def test_qt_binding(self):
        # robodialogs must pick PySide6 first, then PySide2, then tkinter, and never crash at import time
        from robodk import robodialogs
        self.assertIn(robodialogs.QT_API, ('PySide6', 'PySide2', None))
        self.assertEqual(robodialogs.ENABLE_QT, robodialogs.QT_API is not None)
        self.assertTrue(robodialogs.ENABLE_QT or robodialogs.ENABLE_TK)
        if robodialogs.ENABLE_QT:
            import os
            os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
            from robodk import roboapps
            app = roboapps.get_qt_app(robodk_icon=False, robodk_theme=False)
            self.assertIsNotNone(app)
            dialog = robodialogs.DialogsQt.InputDialogQt('Message', {'Float': 1.5, 'Text': 'abc', 'Flag': True, 'Choice': [0, ['A', 'B']]}, title='Test', default_button=True, actions=[('Action', lambda: None)])
            self.assertEqual(dialog.windowTitle(), 'Test')
            self.assertTrue(hasattr(dialog, 'exec') or hasattr(dialog, 'exec_'))
        self.setUp()

    def test_import_install_refreshes_import_system(self):
        # After pip installs a package, import_install must import it in the same process even when the package landed in
        # a sys.path folder that did not exist at the first (failed) import, or in the user site-packages pip fell back to
        import sys, os, io, subprocess, site, tempfile
        from robodk import robolink

        def fake_pip(folder, name, user_fallback):

            class FakePopen:

                def __init__(self, cmd, **kwargs):
                    os.makedirs(folder)
                    with open(os.path.join(folder, name + '.py'), 'w') as f:
                        f.write('X = 1\n')
                    text = ('Defaulting to user installation because normal site-packages is not writeable\n' if user_fallback else '') + 'Successfully installed ' + name + '\n'
                    self.stdout = io.BytesIO(text.encode())

                def wait(self):
                    return 0

            return FakePopen

        cases = [('zz_probe_cached_folder', True, False), ('zz_probe_user_site', False, True)]
        originals = subprocess.Popen, site.getusersitepackages
        folders = []
        try:
            for name, on_path_before, user_fallback in cases:
                folder = os.path.join(tempfile.mkdtemp(), 'site-packages')  # does not exist yet: importlib caches "no importer"
                folders.append(folder)
                if on_path_before:
                    sys.path.append(folder)
                subprocess.Popen = fake_pip(folder, name, user_fallback)
                site.getusersitepackages = lambda folder=folder: folder
                robolink.import_install(name)
                self.assertIn(name, sys.modules, name)
                self.assertEqual(os.path.normcase(os.path.dirname(sys.modules[name].__file__)), os.path.normcase(folder))
                self.assertTrue(any(os.path.normcase(os.path.abspath(p)) == os.path.normcase(folder) for p in sys.path))
        finally:
            subprocess.Popen, site.getusersitepackages = originals
            for name, _, _ in cases:
                sys.modules.pop(name, None)
            sys.path[:] = [p for p in sys.path if os.path.normcase(os.path.abspath(p)) not in {os.path.normcase(f) for f in folders}]
        self.setUp()

    def test_runtime_clash_guard(self):
        # import_install must refuse, with an ImportError, to import a runtime-sensitive module while the process runs on
        # the private MSVC runtime of a PySide2 package folder (simulated here)
        import sys
        from robodk import robolink
        original = robolink._private_runtime_loaded
        robolink._private_runtime_loaded = lambda: 'C:/some/site-packages/PySide2/msvcp140.dll'
        try:
            self.assertNotIn('pymeshlab', sys.modules)
            with self.assertRaises(ImportError) as ctx:
                robolink.import_install('pymeshlab')
            self.assertIn('PySide2', str(ctx.exception))
            robolink._private_runtime_loaded = lambda: None
            robolink._check_qt_dll_clash('pymeshlab')  # must not raise: a shared runtime is in use
        finally:
            robolink._private_runtime_loaded = original
        self.setUp()

    def test_qt_binding_resolved_lazily(self):
        # Importing robodk must not load any Qt binding: add-ins import robodk first and their own binding afterwards,
        # and the binding is chosen on the first dialog / get_qt_app() call so that it matches the script's widgets
        import subprocess, sys, os
        env = dict(os.environ, QT_QPA_PLATFORM="offscreen", PYTHONPATH=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        code = "import sys; from robodk import robolink, roboapps, robodialogs, robofileio; print('QTLOADED', 'PySide6' in sys.modules or 'PySide2' in sys.modules)"
        proc = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, env=env)
        self.assertEqual(proc.returncode, 0, proc.stderr[-500:])
        self.assertIn("QTLOADED False", proc.stdout)
        for binding in ("PySide2", "PySide6"):
            if subprocess.run([sys.executable, "-c", "import " + binding], capture_output=True).returncode != 0:
                continue
            # The add-in pattern: robodk first, the binding second, then roboapps.get_qt_app() and the add-in's widgets
            code = chr(10).join([
                "from robodk import robolink, roboapps, robodialogs",
                "from %s import QtWidgets" % binding,
                "app = roboapps.get_qt_app(False, False)",
                "QtWidgets.QLabel('x')",  # fails with 'Must construct a QApplication before a QWidget' if app is the other binding
                "print('API', robodialogs.QT_API, type(app).__module__.split('.')[0])",
            ])
            proc = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, env=env)
            self.assertEqual(proc.returncode, 0, binding + ": " + proc.stderr[-500:])
            self.assertIn("API %s %s" % (binding, binding), proc.stdout)
        # ENABLE_QT = False right after the import forces tkinter and keeps Qt out of the process
        code = "import sys; from robodk import robodialogs; robodialogs.ENABLE_QT = False; from robodk import roboapps; print('TK', robodialogs.QT_API, 'PySide6' in sys.modules or 'PySide2' in sys.modules)"
        proc = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, env=env)
        self.assertEqual(proc.returncode, 0, proc.stderr[-500:])
        self.assertIn("TK None False", proc.stdout)

    def test_pyside2_already_loaded(self):
        # A script that imported PySide2 before robodk must stay on PySide2: loading PySide6 next to it crashes the process
        import subprocess, sys, os
        probe = subprocess.run([sys.executable, "-c", "import PySide2"], capture_output=True)
        if probe.returncode != 0:
            self.skipTest("PySide2 is not installed")
        env = dict(os.environ, QT_QPA_PLATFORM="offscreen", PYTHONPATH=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        code = "from PySide2 import QtCore; from robodk import robodialogs, robolink; print('API', robodialogs.QT_API)"
        proc = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, env=env)
        self.assertEqual(proc.returncode, 0, proc.stderr[-500:])
        self.assertIn("API PySide2", proc.stdout)
        # import_install('PySide6') after PySide2 either works (shared runtime) or raises; it must never crash the process
        code = chr(10).join(["from PySide2 import QtCore; from robodk import robolink", "try:", "    robolink.import_install('PySide6'); print('GUARD ok')", "except ImportError as e:", "    print('GUARD', 'runtime' in str(e))"])
        proc = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, env=env)
        self.assertEqual(proc.returncode, 0, proc.stderr[-500:])
        self.assertIn("GUARD", proc.stdout, proc.stderr[-500:])

    def test_import_legacy(self):
        # Support backward compatibility until we deprecate "from robolink .."
        for m in self.legacy:
            print("-> Importing " + m)
            try:
                importlib.import_module(m)
            except :
                self.assertTrue(False)
            self.setUp()


if __name__ == '__main__':
    import unittest
    unittest.main()