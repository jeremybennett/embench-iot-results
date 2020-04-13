#!/usr/bin/env python3

# Initialization of the embres package

# Copyright (C) 2020 Embecosm Limited
#
# Contributor: Jeremy Bennett <jeremy.bennett@embecosm.com>
#
# This file is part of Embench.

# SPDX-License-Identifier: GPL-3.0-or-later

"""
Import the classes from the embres package. Only the classes we expose to the
outside world.
"""

from embres.args import Args
from embres.data import Record
from embres.logger import Logger
from embres.readme import Readme
from embres.readme import Details
from embres.utils import check_python_version
from embres.utils import abs_json_to_wiki
