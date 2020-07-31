# Modifications © 2020 Hashmap, Inc
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# Modifications © 2020 Hashmap, Inc
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import inspect
import logging
import os
import pkgutil
import sys
import traceback
from pathlib import Path
from typing import Any

from providah.factories.providah_error import ProvidahError


class PackageFactory:
    """
    PackageFactory is a factory designed to store class definitions and keys to access them (and then construct with a configuration) without having to
    explicitly build this factory. This will make coding cleaner - remove the necessity to build and maintain a factory. If you need specifically typed
    factories, then this factory can be inherited from and a duck-typing filter applied to limit to only the classes of interest.
    """
    # This is the registry of packages
    __entries = {}

    # Logger instance using the global settings
    __logger = logging.getLogger()

    @classmethod
    def register(cls, key: str, value: type) -> None:
        """
        Register a class with the factory.
        Args:
            key: name used to reference the class
            value: class that can be used to instantiate an instance of the class

        """
        cls.__entries[key.lower()] = value

    @classmethod
    def create(cls, key: str, **kwargs) -> Any:
        """
        Generate a class instance given the key and configuration parameters.
        Args:
            key: name to reference the class from the registry
            **kwargs: Configuration parameters as key-word arguments

        Returns:
            Configured instance of class requested.

        Raises:
            ValueError: When key is invalid.
        """
        if key.lower() not in cls.__entries.keys():
            raise ValueError(f"key {key} not present in factory registry")

        return cls.__entries[key.lower()](**kwargs)

    @classmethod
    def fill_registry(cls, path: str = None, module: str = None) -> None:
        """
        Recursive method designed to start from a root path and recursively build
        out the entire registry of classes from that depth downward for the PackageFactory.
        Args:
            path: package path where modules are located
            module: name of module from which classes will be extracted

        Returns:

        """

        # First pass through the path shouldn't be specified. This snippet will make sure that the right path is being used.
        if not path:
            _module = inspect.getmodule(inspect.stack()[1][0])
            filename = _module.__file__
            path = Path(filename).parent

        # Make sure the root module is correctly specified
        if not module:
            module = os.path.basename(path)

        # Location of package
        pkg_dir = path

        # Loop over the modules. If it is a package, the make recursive call, otherwise for each non-package
        # module import the module and register it.
        for (_, name, is_a_package) in pkgutil.iter_modules([pkg_dir]):
            pkg_name = f"{module}.{name}"
            if not is_a_package:

                try:
                    exec('import ' + pkg_name)

                    obj = sys.modules[pkg_name]

                    for dir_name in dir(obj):

                        # We don't want to print in anything that is private by intent or system default
                        if dir_name.startswith('_'):
                            continue

                        # Get the object
                        dir_obj = getattr(obj, dir_name)

                        # Register the object
                        PackageFactory.register(key=dir_name.lower(), value=dir_obj)
                except:
                    # Something seems to have gone wrong. Let's log it and let there be a failure. Silently
                    # continuing would make it hard to track where a potential/likely issue in the package
                    # or in the consuming application for which classes are being extracted.
                    error_message = traceback.format_exc()
                    cls.__logger.error(error_message)
                    raise ProvidahError(error_message)
            else:
                # Make recursive call to the
                cls.fill_registry(path=os.path.join(pkg_dir, name), module=pkg_name)
