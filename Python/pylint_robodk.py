import robodk
import robolink
import inspect
from types import ModuleType

# import astroid
robolink.import_install('astroid')

import astroid
from astroid.builder import AstroidBuilder

def get_members():            
    names_str = ''
    for name, value in inspect.getmembers(robolink) + inspect.getmembers(robodk):
        if name.startswith('__'):
            # some built in method from Python
            continue   
            
        if isinstance(value,ModuleType):
            continue
            
        if hasattr(value, '__call__'):
            # name is a function
            names_str += name + "=None\n"
        else:
            # name is a value
            names_str += name + "=" + str(value) + "\n"
    
    return names_str

def transform():
    builder = AstroidBuilder(astroid.MANAGER)
    return builder.string_build(get_members())
    #return builder.string_build("""
    ## Fill in the rest of the fields that are missing
    #ITEM_TYPE_ROBOT = None
    #""")

def register(linter):
    print("RoboDK linter")

astroid.register_module_extender(astroid.MANAGER, "pylintrobodk", transform)

if __name__ == "__main__":   
    print(get_members())