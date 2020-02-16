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


import process.args
import process.logging
import process.data
import os
import re
import sys
import time

# All the global parameters
gparam = dict()


def output_markdown_line(resdata):
    """Output a line of a markdown table of results"""

    name = resdata['name']
    clk_rate = resdata['platform information']['nominal clock rate (MHz)']

    # Compute the size entries
    if 'size results' in resdata:
        size = {
            'geomean' : resdata['size results']['size geometric mean'],
            'geosd' : resdata['size results']['size geometric standard deviation'],
        }

        size['lo'] = size['geomean'] / size['geosd']
        size['hi'] = size['geomean'] * size['geosd']

    # Compute the speed entries
    if 'speed results' in resdata:
        speed = {
            'geomean' : resdata['speed results']['speed geometric mean'],
            'geosd' : resdata['speed results']['speed geometric standard deviation'],
        }

        speed['lo'] = speed['geomean'] / speed['geosd']
        speed['hi'] = speed['geomean'] * speed['geosd']

        speed_rel = {
            'geomean' : speed['geomean'] / clk_rate,
            'geosd' : speed['geosd'],
        }

        speed_rel['lo'] = speed_rel['geomean'] / speed_rel['geosd']
        speed_rel['hi'] = speed_rel['geomean'] * speed_rel['geosd']

    # Generate the rows
    gparam['readme_newf'].writelines('|                             ' +
                                     '|      ' +
                                     '|           ' +
                                     '|         |         |         |\n')
    if 'size results' in resdata:
        gparam['readme_newf'].writelines(f'| {name:27} ' +
                                         f'| {clk_rate:4} ' +
                                         f'| Size      ' +
                                         f'| {size["geomean"]:7.2f} ' +
                                         f'| {size["lo"]:7.2f} ' +
                                         f'| {size["hi"]:7.2f} |\n')
    else:
        gparam['readme_newf'].writelines(f'| {name:27} ' +
                                         f'| {clk_rate:4} ' +
                                         f'| Size      ' +
                                         f'|     n/a ' +
                                         f'|     n/a ' +
                                         f'|     n/a |\n')

    if 'speed results' in resdata:
        gparam['readme_newf'].writelines(f'|                             ' +
                                         f'|      ' +
                                         f'| Speed     ' +
                                         f'| {speed["geomean"]:7.2f} ' +
                                         f'| {speed["lo"]:7.2f} ' +
                                         f'| {speed["hi"]:7.2f} |\n')
        gparam['readme_newf'].writelines(f'|                             ' +
                                         f'|      ' +
                                         f'| Speed/MHz ' +
                                         f'| {speed_rel["geomean"]:7.2f} ' +
                                         f'| {speed_rel["lo"]:7.2f} ' +
                                         f'| {speed_rel["hi"]:7.2f} |\n')
    else:
        gparam['readme_newf'].writelines(f'|                             ' +
                                         f'|      ' +
                                         f'| Speed     ' +
                                         f'|     n/a ' +
                                         f'|     n/a ' +
                                         f'|     n/a |\n')
        gparam['readme_newf'].writelines(f'|                             ' +
                                         f'|      ' +
                                         f'| Speed/MHz ' +
                                         f'|     n/a ' +
                                         f'|     n/a ' +
                                         f'|     n/a |\n')


def transcribe_results():
    """Transcribe the results from JSON to Markdown"""

    # Header from README.md
    for line in gparam['readme_oldf']:
        gparam['readme_newf'].writelines(line)
        if '<!-- Insert results here -->' in line:
            break

    # Table of data
    gparam['readme_newf'].writelines('\n')
    gparam['readme_newf'].writelines('| Benchmark name              ' +
                                     '|  MHz ' +
                                     '| Type      ' +
                                     '|   Score |     Low |    High |\n')
    gparam['readme_newf'].writelines('| --------------------------- ' +
                                     '| ----:' +
                                     '|:---------:' +
                                     '| -------:| -------:| -------:|\n')

    allres = {}
    for resf in gparam['resfiles']:
        absf = os.path.join(gparam['resdir'], resf + '.json')
        with open(absf) as fileh:
            try:
                resdata = loads(fileh.read())
                log.info(resdata['name'])
                output_markdown_line(resdata)
            except JSONDecodeError as jex:
                log.warning(f'Warning: JSON results data error in {resf} '
                             f'at line {jex.lineno}, column {jex.colno}: '
                             f'{jex.msg}')

    # Footer from README.md
    gparam['readme_newf'].writelines('\n')

    for line in gparam['readme_oldf']:
        if '<!-- Results end here -->' in line:
            gparam['readme_newf'].writelines(line)
            break

    for line in gparam['readme_oldf']:
        gparam['readme_newf'].writelines(line)


def main():
    """
    Main program to drive collating of benchmarks.
    """
    # Parse the arguments, set up logging and then validate the arguments
    args = process.args.Args(os.path.abspath(os.path.dirname(__file__)))
    log = process.logging.Logger(args.logdir(), 'process')
    arglist = args.all_args(log)
    args.log_raw(log)
    args.log_cooked(log)

    # Get the data into a list
    reslist = []
    for resf in arglist['resfiles']:
        record = process.data.Record(resf)
        if record.valid_data():
            reslist.append(record)
        else:
            # If there is a problem we run valid_data a second time to capture
            # the detail in the log.
            log.info(f'Warning: Invalid results file {resf}: ignored')
            record.valid_data(log)

    # Create the new readme
    readme = process.readme.Readme(arglist['readme_hdr'], arglist['readme'])
    readme.write_table(arglist['readme'], 'Results sorted by name', reslist)

# Make sure we have new enough python
def check_python_version(major, minor):
    """Check the python version is at least {major}.{minor}."""
    if ((sys.version_info[0] < major)
            or ((sys.version_info[0] == major)
                and (sys.version_info[1] < minor))):
        log.error(f'ERROR: Requires Python {major}.{minor} or later')
        sys.exit(1)


# Make sure we have new enough Python and only run if this is the main package

check_python_version(3, 6)
if __name__ == '__main__':
    sys.exit(main())
