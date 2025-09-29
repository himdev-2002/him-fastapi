import os
import pkgutil

# Import all classes and functions from modules in this folder for easier access

__all__ = []

package_dir = os.path.dirname(__file__)

for _, module_name, is_pkg in pkgutil.iter_modules([package_dir]):
    if not is_pkg and module_name != "__init__":
        try:
            module = __import__(f"{__name__}.{module_name}", fromlist=["*"])
            for attr in dir(module):
                if not attr.startswith("_"):
                    globals()[attr] = getattr(module, attr)
                    __all__.append(attr)
        except ImportError as e:
            # Skip modules that can't be imported due to missing dependencies
            print(f"Warning: Could not import {module_name}: {e}")
            continue