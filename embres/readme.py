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
    def __init__(self, readme_hdr, readme, absdetailsdir, detailsdir):
        """
        The constructor just keeps a copy of the file handles, creates a
        writer for details pages and the relative directory with pages of
        details.
        """
        # Sanity check
        assert os.path.isabs(absdetailsdir), f'{absdetailsdir} is relative'

        # Record the file handle.
        self.__readme_hdr = readme_hdr
        self.__readme = readme
        self.__absdetailsdir = absdetailsdir
        self.__detailsdir = detailsdir

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
        dref = f'{self.__detailsdir}/{res.details_page()}'
        self.__readme.writelines(f'|  rowspan="3" | [[{dref}|{res.desc()}]]\n')
        self.__readme.writelines(f'|  align="right" rowspan="3" | '
                                 f'{res.cpu_mhz()}\n')

        # Line for each type of result
        resvals = res.scores()

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

    @staticmethod
    def __write_general_details(fileh, json_data):
        """
        Static method to write out general detail fields.

        Will raise KeyError if the description field is missing
        """
        # Page title is the description
        desc = json_data.pop('description')
        fileh.writelines(f'== {desc} ==\n\n')

        # Table for the info
        fileh.writelines('{| class="wikitable sortable"\n')

        fields = ['Embench version', 'architecture family', 'date/time',]
        for field in fields:
            val = json_data.pop(field, '')
            fileh.writelines(f'|- align="left"\n')
            fileh.writelines(f'| {field} || {val}\n')

        fileh.writelines('|}\n\n')

    @staticmethod
    def __write_platform_info(fileh, json_data):
        """
        Static method to write out platform information fields.

        Will raise KeyError if the platform information field is missing
        """
        # Section title is the description
        pinfo = json_data.pop('platform information')
        fileh.writelines('== Platform information ==\n\n')

        # Table for the info
        fileh.writelines('{| class="wikitable sortable"\n')

        for field, val in pinfo.items():
            fileh.writelines(f'|- align="left"\n')
            fileh.writelines(f'| {field} || {val}\n')

        fileh.writelines('|}\n\n')

    @staticmethod
    def __write_tool_chain_info(fileh, json_data):
        """
        Static method to write out tool chain info fields.

        Will raise KeyError if the tool chain information, tool chain version
        or tool chain flag fields are missing
        """
        # Main section title
        tcinfo = json_data.pop('tool chain information')
        fileh.writelines('== Tool chain information ==\n\n')

        # Section for tool chain version
        tcvinfo = tcinfo.pop('tool chain version')
        fileh.writelines('=== Tool chain versions ===\n\n')

        # Table for the tool chain version info
        fileh.writelines('{| class="wikitable sortable"\n')

        for field, val in tcvinfo.items():
            fileh.writelines(f'|- align="left"\n')
            fileh.writelines(f'| {field} || {val}\n')

        fileh.writelines('|}\n\n')

        # Section for tool chain flags
        tcfinfo = tcinfo.pop('tool chain flags')
        fileh.writelines('=== Tool chain flags used in benchmarking ===\n\n')

        # Table for the tool chain flags info
        fileh.writelines('{| class="wikitable sortable"\n')

        for field, val in tcfinfo.items():
            fileh.writelines(f'|- align="left"\n')
            fileh.writelines(f'| {field} || {val}\n')

        fileh.writelines('|}\n\n')

        # Section for any other tool chain info
        if tcinfo:
            fileh.writelines('=== Other tool chain information ===\n\n')

            # Table for the other tool chain info
            fileh.writelines('{| class="wikitable sortable"\n')

            for field, val in tcinfo.items():
                fileh.writelines(f'|- align="left"\n')
                fileh.writelines(f'| {field} || {val}\n')

            fileh.writelines('|}\n\n')

    def __write_details(self, details):
        """
        Write out a file with all the details for a set of results.

        Raises OSError if there is a problem opening the file. We work with a
        copy of the details, from which we delete elements as they are
        printed. This allows us to print any remaining general information at
        the end, thus allowing arbitary information to be recorded.
        """
        fileh = open(
            os.path.join(self.__absdetailsdir, details.details_page()), 'w'
        )
        json_data = details.json_data_copy()
        self.__write_general_details(fileh, json_data)
        self.__write_platform_info(fileh, json_data)
        self.__write_tool_chain_info(fileh, json_data)
        fileh.close()

    def write_all_details(self, result_set):
        """
        Write out all the details files for the supplied set of results
        """
        for res in result_set.results():
            self.__write_details(res.details())

    def write_table(self, title, result_set):
        """
        Given a list of results generate them as a mediawiki table, preceded
        by the supplied level 3 title
        """
        # The title, preceded and followed by a blank line
        self.__readme.writelines(f'\n=== {title} ===\n\n')

        # The wiki table header
        self.__wiki_tblhdr()

        # The wiki table body - one row for each entry
        for res in result_set.results():
            self.__wiki_tblrow(res)

        # The wiki table footer
        self.__wiki_tblftr()
