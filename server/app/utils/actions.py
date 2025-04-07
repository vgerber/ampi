import os
import pkgutil
import app.actions


def get_actions() -> list[str]:
    pkg_path = os.path.dirname(app.actions.__file__)
    return [module_info.name for module_info in pkgutil.iter_modules([pkg_path])]
