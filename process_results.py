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
        details_wikipage = embres.abs_json_to_wiki(resf)
        record = embres.Record(resf, details_wikipage)
        if record.valid_data():
            details = embres.Details(
                arglist['absdetailsdir'], details_wikipage
            )
            record.write_details(details)
            reslist.append(record)
        else:
            # If there is a problem we run valid_data a second time to capture
            # the detail in the log.
            log.info(f'Warning: Invalid results file {resf}: ignored')
            record.valid_data(log)

    # Create the new readme
    readme = embres.Readme(
        arglist['readme_hdr'], arglist['readme'], arglist['detailsdir']
    )
    readme.write_header()

    # Results sorted by speed (large is good)
    reslist_sorted = sorted(
        reslist, key=lambda rec: rec.results()['Speed'].geomean(), reverse=True
    )
    readme.write_table('Results sorted by Embench speed score', reslist_sorted)

    # Results sorted by speed/MHz (large is good)
    reslist_sorted = sorted(
        reslist,
        key=lambda rec: rec.results()['Speed/MHz'].geomean(),
        reverse=True
    )
    readme.write_table(
        'Results sorted by Embench speed score/MHz', reslist_sorted
    )

    # Results sorted by size (small is good)
    reslist_sorted = sorted(
        reslist, key=lambda rec: rec.results()['Size'].geomean()
    )
    readme.write_table('Results sorted by Embench size score', reslist_sorted)

    # Per architecture results sorted by speed (large is good)
    reslist_sorted = sorted(
        reslist, key=lambda rec: rec.arch()
    )
    reslist_sorted2 = sorted(
        reslist_sorted,
        key=lambda rec: rec.results()['Speed'].geomean(),
        reverse=True
    )
    readme.write_table(
        'Per architecture results sorted by Embench speed score', reslist_sorted2
    )

    # Results sorted by speed/MHz (large is good)
    reslist_sorted2 = sorted(
        reslist_sorted,
        key=lambda rec: rec.results()['Speed/MHz'].geomean(),
        reverse=True
    )
    readme.write_table(
        'Per architecture results sorted by Embench speed score/MHz',
        reslist_sorted2
    )

    # Results sorted by size (small is good)
    reslist_sorted2 = sorted(
        reslist_sorted, key=lambda rec: rec.results()['Size'].geomean()
    )
    readme.write_table(
        'Per achitecture results sorted by Embench size score', reslist_sorted2
    )


# Make sure we have new enough Python and only run if this is the main package
embres.check_python_version(3, 6)
if __name__ == '__main__':
    sys.exit(main())
