[![FOSSA Status](https://app.fossa.com/api/projects/git%2Bgitlab.com%2Fhashmapinc%2Fctso%2Futilities%2Fprovidah.svg?type=shield)](https://app.fossa.com/projects/git%2Bgitlab.com%2Fhashmapinc%2Fctso%2Futilities%2Fprovidah?ref=badge_shield)

[![codecov](https://codecov.io/gl/hashmapinc:ctso:utilities/providah/branch/development/graph/badge.svg?token=WSR9CIU4A3)](https://codecov.io/gl/hashmapinc:ctso:utilities/providah)

# providah

providah is a small, simple utility. It is an opinionated approach to creating object factories in Python without adding 
the additional complexity of maintaining factories.

## Concept
The library is utilized as a basic global (to package) Iversion of Control (IoC) Container (Dependency Injection Container). The idea
as presented is to provide an approach where all class in a package will automatically be registered. You can also override a specific 
registered class when you have monkey patched the class. When a new class is added it can manually be added to the registry, and this 
is helpful for application level classes, local extensions to a library, and so on. In even other situations you may want to add a 
a class when you want to retain the default version of a class, but want to support an alternative version as well. 

## Design

## Examples

### Example 1 - Library Factory
Within an \_\_init\_\_ .py - often at the root of a library's source code. This is ideal when you want to register all classes in 
the library in a single factory.
```python
from providah.factories.package_factory import PackageFactory
PackageFactory.fill_registry()
```

### Example 2 - Patching
When You want to monkey patch the functionality of a class.
```python
from X import Y
from providah.factories.package_factory import PackageFactory

def new_method(params):
    print('Hello there')

Y.print = new_method()
PackageFactory.register(key=str('Y'), library=str('X'), class_def=Y)
```

### Example 3 - Ad Hoc Registration
When you want to add a class that will later be referenced by a label - in the case you are creating more than one class with the 
same key, but not using library identifiers.
```python
class Writer:
    @classmethod
    def write(cls) -> None:
        raise NotImplementedError('Base class method - must be implemented.')

class A(Writer):
    @classmethod
    def write(cls) -> None:
        print("Hello World")

import sqlite3
class B(Writer):
    __db_conn: sqlite3.connect('B.db')

    @classmethod
    def write(cls):
        cls.__write_to_db('Hello World')
    
    @classmethod
    def __write_to_db(cls, data: str) -> None:
        with cls.db_conn.cursor() as cursor:
            cursor.execute(f"INSERT INTO logs VALUES ({data})")
            cursor.commit()

from providah.factories.package_factory import PackageFactory
PackageFactory.register(key=str('A'), class_def=A, label=str('print_writer'))
PackageFactory.register(key=str('B'), class_def=A, label=str('db_writer'))
```

### Example 4 - Using IoC Factory

```python
from providah.factories.package_factory import PackageFactory

# Must import library - when library classes added to factory as in Example 1 (above) the 
# runtime execution of this will happen when the library is imported.
import some_package
import another_package

# To make sure we get the right version - Exceptions occur otherwise.
some_obj = PackageFactory.create('bob', library='some_package')
another_obj = PackageFactory.create('bob', library='another_package')
```


