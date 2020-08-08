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

from providah.factories.providah_error import ProvidahError


class TestProvidahError(TestCase):

    def test_raise_error(self):

        with self.assertRaises(ProvidahError):
            raise ProvidahError('Some Error')

        with self.assertRaises(ProvidahError):
            raise ProvidahError

    def test_print_exception_message(self):

        try:
            raise ProvidahError('Test Error')
        except ProvidahError as ex:
            print(ex)

    def test_print_exception_no_message(self):

        try:
            raise ProvidahError
        except ProvidahError as ex:
            print(ex)
