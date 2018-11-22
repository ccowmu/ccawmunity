from os import listdir
from os.path import isfile, dirname, abspath, join

# make a list of python files in the package directory.
# remove __init__.py from the list.
_directory = dirname(abspath(__file__))
_listener_files = [f for f in listdir(_directory) if isfile(join(_directory, f))]
_listener_files.remove("__init__.py")
if "README.md" in _listener_files:
    _listener_files.remove("README.md")

_module_names = [filename.split(".")[0] for filename in _listener_files]

__all__ = _module_names