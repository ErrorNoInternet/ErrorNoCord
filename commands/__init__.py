import importlib
import inspect

from state import reloaded_modules

from . import tools, utils, voice
from .utils import *


def __reload_module__():
    for name, module in globals().items():
        if inspect.ismodule(module) and name not in constants.RELOAD_BLACKLISTED_MODULES:
            importlib.reload(module)
            if "__reload_module__" in dir(module) and name not in reloaded_modules:
                reloaded_modules.add(name)
                module.__reload_module__()

    globals().update({k: v for k, v in vars(utils).items() if not k.startswith("_")})
