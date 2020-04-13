#!/usr/bin/env python3

# Module to generate the new README as part of the embres package

# Copyright (C) 2019, 2020 Embecosm Limited
#
# Contributor: Jeremy Bennett <jeremy.bennett@embecosm.com>
#
# This file is part of Embench.

# SPDX-License-Identifier: GPL-3.0-or-later

"""
Module with useful static functions

For now just one function to check we have new enough Python
"""

# System packages
import os.path
import sys


def check_python_version(major, minor):
    """
    Check the python version is at least {major}.{minor}.

    Note. We can't use the log yet - it isn't created!
    """
    if ((sys.version_info[0] < major)
            or ((sys.version_info[0] == major)
                and (sys.version_info[1] < minor))):
        print(f'ERROR: Requires Python {major}.{minor} or later')
        sys.exit(1)

def abs_json_to_wiki(absf):
    """
    JSON results files are held as absolute file names ending in .json. Their
    details will be in a file with the same name as the last part, and with
    the suffix .mediawiki. This function makes that conversion.
    """
    root, suffix = os.path.splitext(os.path.basename(absf))

    # Sanity check
    if suffix != '.json':
        log.warning(
            f'Warning: {absf} does not have suffix .json for conversion to ' +
            f'mediawiki filename. Suffix ignored.'
        )

    return root + '.mediawiki'
