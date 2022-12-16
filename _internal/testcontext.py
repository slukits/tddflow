# -*- coding: utf-8 -
#
# Copyright (c) 2022 Stephan Lukits. All rights reserved.
# Use of this source code is governed by a MIT-style
# license that can be found in the LICENSE file.

import os
import sys

pyunit_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../../pyunit'))

sys.path.insert(0, pyunit_path)

import testing
_ = testing
