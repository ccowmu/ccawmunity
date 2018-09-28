from os import listdir
from os.path import isfile, dirname, abspath, join

# make a list of python files in the package directory.
# remove __init__.py from the list.
_directory = dirname(abspath(__file__))
_command_files = [f for f in listdir(_directory) if isfile(join(_directory, f))]
_command_files.remove("__init__.py")

_module_names = [filename.split(".")[0] for filename in _command_files]

__all__ = _module_names