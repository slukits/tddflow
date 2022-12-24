# -*- coding: utf-8 -
#
# Copyright (c) 2022 Stephan Lukits. All rights reserved.
# Use of this source code is governed by a MIT-style
# license that can be found in the LICENSE file.

import os
import sys

tddflow_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../../../..'))

if tddflow_path not in sys.path:
    sys.path.insert(0, tddflow_path)

from tddflow import testing
