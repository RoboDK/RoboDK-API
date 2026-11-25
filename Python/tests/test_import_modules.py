
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

    def test_qt5_dll_clash_guard(self):
        # import_install must refuse, with an ImportError, to import a Qt 5 bundling module once PySide2 is loaded
        import sys, types
        from robodk import robolink
        fake = types.ModuleType('PySide2')
        had_pyside2 = 'PySide2' in sys.modules
        sys.modules.setdefault('PySide2', fake)
        try:
            self.assertNotIn('pymeshlab', sys.modules)
            with self.assertRaises(ImportError) as ctx:
                robolink.import_install('pymeshlab')
            self.assertIn('PySide2', str(ctx.exception))
        finally:
            if not had_pyside2:
                sys.modules.pop('PySide2', None)
        self.setUp()

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
        code = chr(10).join(["from PySide2 import QtCore; from robodk import robolink", "try:", "    robolink.import_install('PySide6')", "except ImportError as e:", "    print('GUARD', 'Qt 5' in str(e))"])
        proc = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, env=env)
        self.assertIn("GUARD True", proc.stdout, proc.stderr[-500:])

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