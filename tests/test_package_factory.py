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
from unittest import TestCase

from providah.factories.package_factory import PackageFactory

import tst_pkg
import tst_pkg_2

from providah.factories.providah_error import ProvidahError


class TestPackageFactory(TestCase):

    def test_create_class(self):
        a = PackageFactory.create('ClassA', library='tst_pkg')
        self.assertIsInstance(a, tst_pkg.lib.class_A.ClassA)

    def test_create_class_with_nest_class(self):
        b = PackageFactory.create('ClassB', library='tst_pkg_2')
        self.assertIsInstance(b, tst_pkg_2.lib.class_B.ClassB)
        self.assertIsInstance(b.c, tst_pkg_2.lib.sublib.class_C.ClassC)

    def test_create_second_class_in_file(self):
        d = PackageFactory.create('ClassD', library='tst_pkg')
        self.assertIsInstance(d, tst_pkg.lib.class_A.ClassD)

    def test_key_doesnt_exist(self):
        with self.assertRaises(ProvidahError):
            PackageFactory.create('ClassF', library='tst_pkg')

    def test_library_doesnt_exist(self):
        with self.assertRaises(ProvidahError):
            PackageFactory.create('ClassD', library='some_package')

    def test_label_doesnt_exist(self):
        with self.assertRaises(ProvidahError):
            PackageFactory.create('ClassD', label='some_package')

    def test_duplicate_entries(self):
        with self.assertRaises(ProvidahError):
            PackageFactory.create('ClassB')

