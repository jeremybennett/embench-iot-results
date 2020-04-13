#!/usr/bin/env python3

# Module to generate the new README as part of the embres package

# Copyright (C) 2019, 2020 Embecosm Limited
#
# Contributor: Jeremy Bennett <jeremy.bennett@embecosm.com>
#
# This file is part of Embench.

# SPDX-License-Identifier: GPL-3.0-or-later

"""
Module to generate a new README and the subsidiary pages

This can be summarized as generating the header, then generating a series of
sections based on different orderings.
"""

# System packages
import os.path


class Readme:
    """
    A class to handle README file generation
    """
    def __init__(self, readme_hdr, readme, details_dir):
        """
        The constructor just keeps a copy of the file handles and the
        directory with pages of details.
        """
        # Record the file handle.
        self.__readme_hdr = readme_hdr
        self.__readme = readme
        self.__details_dir = details_dir

    def __wiki_tblhdr(self):
        """
        Private method to write out the standard wiki table header.
        """
        # Header is all fixed.
        self.__readme.writelines('{| class="wikitable sortable"\n')
        self.__readme.writelines('! align="left"  | Architecture\n')
        self.__readme.writelines('! align="left"  | Benchmark description\n')
        self.__readme.writelines('! align="right" | MHz\n')
        self.__readme.writelines('! align="left"  | Type\n')
        self.__readme.writelines('! align="right" | Score\n')
        self.__readme.writelines('! align="center" | Range\n')

    def __wiki_tblrow(self, res):
        """
        Private method to write out one row of wiki table data for the
        supplied result file.
        """
        # Put out the lines
        self.__readme.writelines(f'|- align="left"\n')
        self.__readme.writelines(f'|  rowspan="3" | {res.arch()}\n')
        dref = f'{self.__details_dir}/{res.details_wikipage()}'
        self.__readme.writelines(f'|  rowspan="3" | [[{dref}|{res.desc()}]]\n')
        self.__readme.writelines(f'|  align="right" rowspan="3" | '
                                 f'{res.cpu_mhz()}\n')

        # Line for each type of result
        resvals = res.results()

        for rtype in ['Size', 'Speed', 'Speed/MHz']:
            rval = resvals[rtype]

            self.__readme.writelines(f'|  {rtype}\n')
            self.__readme.writelines(f'|  align="right" | '
                                     f'{rval.geomean():.2f}\n')
            self.__readme.writelines(f'|  align="center" | '
                                     f'{rval.range_lo():.2f}'
                                     f'- {rval.range_hi():.2f}\n')
            self.__readme.writelines(f'|-\n')

    def __wiki_tblftr(self):
        """
        Private method to write out the standard wiki footer.
        """
        # Footer
        self.__readme.writelines('|}\n')

    def write_header(self):
        """
        Copy the fixed pre-header into the README.
        """
        for line in self.__readme_hdr:
            self.__readme.writelines(line)

    def write_table(self, title, reslist):
        """
        Given a list of results generate them as a mediawiki table, preceded
        by the supplied level 3 title
        """
        # The title, preceded and followed by a blank line
        self.__readme.writelines(f'\n=== {title} ===\n\n')

        # The wiki table header
        self.__wiki_tblhdr()

        # The wiki table body - one row for each entry
        for res in reslist:
            self.__wiki_tblrow(res)

        # The wiki table footer
        self.__wiki_tblftr()


class Details:
    """
    A class to deal with the details for each set of results
    """
    def __open(self, filepath):
        """
        Private method to open the details file for writing. Return the file
        handle.
        """
        fileh = None
        try:
            fileh = open(filepath, 'w')
        except OSError as osex:
            log.error(f'ERROR: Could not open {filepath} for writing: ' +
                      f'{osex.strerror}: exiting.')
            sys.exit(1)

        return fileh

    def __init__(self, absdetailsdir, detailsfile):
        """
        The constructor opens the detailsfile for writing. We pass the
        absolute directory name, so this will work from any directory.
        """
        # Sanity check
        if not os.path.isabs(absdetailsdir):
            log.error(
                f'ERROR: {absdetailsdir} must be passed to the Details class ' +
                f'constructor as an absolute directory name. Check the code.'
            )
            sys.exit(2)

        # Record the details file name and the file handle
        self.__filename = detailsfile
        self.__fileh = self.__open(os.path.join(absdetailsdir, detailsfile))

    def write_results(self, record):
        """
        Write out the details of one result.
        """
        self.__fileh.writelines(f'== {record.desc()} ==\n')
