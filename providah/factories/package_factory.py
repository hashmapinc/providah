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
from typing import Any, NamedTuple

from providah.factories.providah_error import ProvidahError


class Entry(NamedTuple):
    """
    Registry entry.
    """
    key: str
    class_def: type
    library: str
    label: str


# noinspection BuiltinExec
class PackageFactory:
    """
    PackageFactory is a factory designed to store class definitions and keys to access them (and then construct with a configuration) without having to
    explicitly build this factory. This will make coding cleaner - remove the necessity to build and maintain a factory. If you need specifically typed
    factories, then this factory can be inherited from and a duck-typing filter applied to limit to only the classes of interest.
    """
    # This is the registry of packages
    __registry = []

    # Logger instance using the global settings
    __logger = logging.getLogger()

    @classmethod
    def register(cls,
                 key: str,
                 class_def: type,
                 library: str = None,
                 label: str = None) -> None:
        """
        Register a class with the factory.
        Args:
            key: name used to reference the class
            class_def: class that can be used to instantiate an instance of the class
            library: name of library that the application is from.
            label: label used to identify a class - possible linked to a monkey-patched version or a sub-application specific class.

        """
        new_entry = Entry(key=key.lower(),
                          class_def=class_def,
                          library=str(library).lower(),
                          label=str(label).lower())

        # Add entry if it is not currently present. Prevents duplicate entry.
        if new_entry not in cls.__registry:
            cls.__registry.append(new_entry)

    @classmethod
    def create(cls,
               key: str,
               library: str = None,
               label: str = None,
               **kwargs) -> Any:
        """
        Generate a class instance given the key and configuration parameters.
        Args:
            key: name to reference the class from the registry
            library: name of library that the application is from.
            label: label used to identify a class - possible linked to a monkey-patched version or a sub-application specific class.
            **kwargs: Configuration parameters as key-word arguments

        Returns:
            Configured instance of class requested.

        Raises:
            ValueError: When key is invalid.
        """
        # Find all entries which have the specified key value.
        entries = [entry for entry in cls.__registry if entry.key == key.lower()]
        if len(entries) == 0:
            error_message = f"The key {key} not present."
            cls.__logger.error(error_message)
            raise ProvidahError(error_message)

        # If a library filter was specified, then find all such entries that have that filter
        if library:
            entries = [entry for entry in entries if entry.library == library.lower()]
            if len(entries) == 0:
                error_message = f"The library {library} not present in for key {key}."
                cls.__logger.error(error_message)
                raise ProvidahError(error_message)

        # If a label filter was specified, then find all such entries that have that filter
        if label:
            entries = [entry for entry in entries if entry.label == label.lower()]
            if len(entries) == 0:
                error_message = f"The label {label} not present in for key {key}."
                cls.__logger.error(error_message)
                raise ProvidahError(error_message)

        # If more than one entry was found, then the appropriate filters have not been applied.
        if len(entries) > 1:
            error_message = f'The combination of key {key}, label {label}, and library {library} did not return a unique result. A total of {len(entries)} ' \
                            f'possible entries were found'
            cls.__logger.error(error_message)
            raise ProvidahError(error_message)

        # Return instantiated and configured class.
        return entries[0].class_def(**kwargs)

    @classmethod
    def fill_registry(cls, path: str = None,
                      module: str = None,
                      library: str = None,
                      label: str = None) -> None:
        """
        Recursive method designed to start from a root path and recursively build
        out the entire registry of classes from that depth downward for the PackageFactory.
        Args:
            path: package path where modules are located
            module: name of module from which classes will be extracted
            library: name of library that the application is from.
            label: label used to identify a class - possible linked to a monkey-patched version or a sub-application specific class.

        """

        # First pass through the path shouldn't be specified. This snippet will make sure that the right path is being used.
        if not path:
            _module = inspect.getmodule(inspect.stack()[1][0])
            filename = _module.__file__
            path = Path(filename).parent

        # Make sure the root module is correctly specified
        if not module:
            module = os.path.basename(path)

        if not library:
            library = module

        # Location of package
        pkg_dir = path

        # Loop over the modules. If it is a package, the make recursive call, otherwise for each non-package
        # module import the module and register it.
        for (_, name, is_a_package) in pkgutil.iter_modules([pkg_dir]):
            pkg_name = f"{module}.{name}"
            if not is_a_package:

                cls.__add_entry_to_registry(label=label,
                                            library=library,
                                            name_of_package=pkg_name)
            else:
                # Make recursive call to the
                cls.fill_registry(path=os.path.join(pkg_dir, name),
                                  module=pkg_name,
                                  library=library,
                                  label=label)

    @classmethod
    def __add_entry_to_registry(cls, label: str, library: str, name_of_package: str) -> None:
        """

        Args:
            library: name of library that the application is from.
            label: label used to identify a class - possible linked to a monkey-patched version or a sub-application specific class.
            name_of_package: Name of the package

        Raises:
            ProvidahError
        """
        try:
            exec('import ' + name_of_package)

            obj = sys.modules[name_of_package]

            for dir_name in dir(obj):

                # We don't want to print in anything that is private by intent or system default
                if dir_name.startswith('_'):
                    continue

                # Get the object
                class_def = getattr(obj, dir_name)

                # Register the object - but don't register this factory
                if not dir_name.lower() == 'packagefactory':
                    PackageFactory.register(key=dir_name.lower(),
                                            class_def=class_def,
                                            library=library,
                                            label=label)
        except Exception:
            # Something seems to have gone wrong. Let's log it and let there be a failure. Silently
            # continuing would make it hard to track where a potential/likely issue in the package
            # or in the consuming application for which classes are being extracted.
            error_message = traceback.format_exc()
            cls.__logger.error(error_message)
            raise ProvidahError(error_message)
