
import unittest
import importlib

class TestImport(unittest.TestCase):

    modules = ['robodk.robolink', 'robodk.robomath','robodk.robodialogs','robodk.robofileio','robodk.roboapps']
    legacy = ['robodk', 'robolink']

    def setUp(self) -> None:
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