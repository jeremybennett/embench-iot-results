#!/usr/bin/env python3

# Script to collate all benchmark results

# Copyright (C) 2019 Embecosm Limited
#
# Contributor: Jeremy Bennett <jeremy.bennett@embecosm.com>
#
# This file is part of Embench.

# SPDX-License-Identifier: GPL-3.0-or-later

"""
Collate all Embench benchmark results

Data are held in files in the results directory of the form
<arch>-<description>.json.  Each defines a set of results in a JSON file.
"""

# System packages
import os.path
import sys

# Local packages
import embres


def main():
    """
    Main program to drive collating of benchmarks.
    """
    # Parse the arguments, set up logging and then validate the arguments
    args = embres.Args(os.path.abspath(os.path.dirname(__file__)))
    log = embres.Logger(args.logdir(), 'results')
    arglist = args.all_args(log)
    args.log(log)

    # Get the data into a list
    reslist = []
    for resf in arglist['resfiles']:
        record = embres.Record(resf)
        if record.valid_data():
            reslist.append(record)
        else:
            # If there is a problem we run valid_data a second time to capture
            # the detail in the log.
            log.info(f'Warning: Invalid results file {resf}: ignored')
            record.valid_data(log)

    # Create the new readme
    readme = embres.Readme(arglist['readme_hdr'], arglist['readme'])
    readme.write_header()
    readme.write_table('Results sorted by name', reslist)


# Make sure we have new enough python
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


# Make sure we have new enough Python and only run if this is the main package
check_python_version(3, 6)
if __name__ == '__main__':
    sys.exit(main())
