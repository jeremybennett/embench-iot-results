#!/usr/bin/env python3

# Module to generate the new README as part of the process package

# Copyright (C) 2019 Embecosm Limited
#
# Contributor: Jeremy Bennett <jeremy.bennett@embecosm.com>
#
# This file is part of Embench.

# SPDX-License-Identifier: GPL-3.0-or-later

"""
Module to generate a new README

This can be summarized as generating the header, then generating a series of
sections based on different orderings.
"""


class Readme:
    """
    A class to handle README file generation
    """
    def __init__(self, readme_hdr, readme):
        """
        The constructor just copies the header into the new README.
        """
        # Header from README.md
        for line in readme_hdr:
            readme.writelines(line)

    def __wiki_tblhdr(self, readme):
        """
        Private method to write out the standard wiki table header.
        """
        # Header is all fixed.
        readme.writelines('{| class="wikitable sortable"\n')
        readme.writelines('! align="left"  | Architecture\n')
        readme.writelines('! align="left"  | Benchmark name\n')
        readme.writelines('! align="right" | MHz\n')
        readme.writelines('! align="left"  | Type\n')
        readme.writelines('! align="right" | Score\n')
        readme.writelines('! align="center" | Range\n')

    def __wiki_tblrow(self, readme, res):
        """
        Private method to write out one row of wiki table data for the
        supplied result file.
        """
        # Put out the lines
        readme.writelines(f'|- align="left"\n')
        readme.writelines(f'|  rowspan="3" | {res.arch()}\n')
        readme.writelines(f'|  rowspan="3" | {res.name()}\n')
        readme.writelines(f'|  align="right" rowspan="3" | {res.cpu_mhz()}\n')

        # Line for each type of result
        resvals = res.results()

        for rtype in ['Size', 'Speed', 'Speed/MHz']:
            rval = resvals[rtype]

            readme.writelines(f'|  {rtype}\n')
            readme.writelines(f'|  align="right" | {rval.geomean():.2f}\n')
            readme.writelines(f'|  align="center" | {rval.range_lo():.2f}'
                              f'- {rval.range_hi():.2f}\n')
            readme.writelines(f'|-\n')

    def __wiki_tblftr(self, readme):
        """
        Private method to write out the standard wiki footer.
        """
        # Footer followed by a blank line.
        readme.writelines('|}\n\n')

    def write_table(self, readme, title, reslist):
        """
        Given a list of results generate them as a mediawiki table, preceded
        by the supplied level 2 title
        """
        # The title, followed by a blank line
        readme.writelines(f'== {title} ==\n\n')

        # The wiki table header
        self.__wiki_tblhdr(readme)

        # The wiki table body - one row for each entry
        for res in reslist:
            self.__wiki_tblrow(readme, res)

        # The wiki table footer
        self.__wiki_tblftr(readme)
