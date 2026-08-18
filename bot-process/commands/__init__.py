import pkgutil
import importlib
from .command import Command

for module_info in pkgutil.iter_modules(__path__):
    importlib.import_module(f"{__name__}.{module_info.name}")

COMMAND_REGISTRY = {
    command_class.REQUEST_TYPE: command_class for command_class in Command.__subclasses__()
}