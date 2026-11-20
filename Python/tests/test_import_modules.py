
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