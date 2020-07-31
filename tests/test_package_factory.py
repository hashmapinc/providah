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


class TestPackageFactory(TestCase):

    def test_create_class(self):
        a = PackageFactory.create('ClassA')
        self.assertIsInstance(a, tst_pkg.lib.class_A.ClassA)

    def test_create_class_with_nest_class(self):
        b = PackageFactory.create('ClassB')
        self.assertIsInstance(b, tst_pkg.lib.class_B.ClassB)
        self.assertIsInstance(b.c, tst_pkg.lib.sublib.class_C.ClassC)
