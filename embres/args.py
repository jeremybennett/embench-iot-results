#!/usr/bin/env python3

# Module to handle arguments as part of the embres package

# Copyright (C) 2019, 2020 Embecosm Limited
#
# Contributor: Jeremy Bennett <jeremy.bennett@embecosm.com>
#
# This file is part of Embench.

# SPDX-License-Identifier: GPL-3.0-or-later

"""
Module to handle argument parsing.

We break this into two stages.

- an initial parse to get the raw arguments, so the log file can be set up

- a post processing phase to validate and sanitize the arguments.
"""


import argparse
import os
import re
import sys


class Args:
    """
    A class to handle argument parsing
    """
    def __init__(self, rootdir):
        """
        Parse the raw arguments. The goal is to get enough information we can
        set up logging. We need to know the root directory, since ultimately
        relative file arguments will be based on this.
        """
        # Capture the root directory
        self.__rootdir = rootdir

        # Create a parser
        parser = argparse.ArgumentParser(description='Collate benchmark results')

        # Add the arguments
        parser.add_argument(
            '--resdir',
            type=str,
            default=None,
            help='Directory holding the results files',
        )
        parser.add_argument(
            '--logdir',
            type=str,
            default='logs',
            help='Directory in which to store logs',
        )
        parser.add_argument(
            'resfiles',
            metavar='result-file',
            type=str,
            nargs='*',
            help='Specific results files to accumulate',
        )

        # Parse the command line
        self.__args = parser.parse_args()

        # Mark all private copies as empty for now.
        self.__cooked = dict()
        self.__cooked['logdir'] = None
        self.__cooked['resdir'] = None
        self.__cooked['readme_hdr'] = None
        self.__cooked['readme'] = None
        self.__cooked['resfiles'] = []

    def logdir(self):
        """
        Extract the log directory, create it if necessary and make sure it is
        writable. This means dealing with relative v absolute directory
        names. Any errors here are going to go straight to the console as
        exceptions.
        """
        # Sort out absolutism
        logdir = self.__args.logdir
        if not os.path.isabs(logdir):
            logdir = os.path.join(self.__rootdir, logdir)

        # Create the directory if necessary and maks sure we can write it.
        if not os.path.isdir(logdir):
            try:
                os.makedirs(logdir)
            except PermissionError:
                raise PermissionError(f'Unable to create log directory {logdir}')

        if not os.access(logdir, os.W_OK):
            raise PermissionError(f'Unable to write to log directory {logdir}')

        self.__cooked['logdir'] = logdir
        return logdir

    def __resdir(self, log):
        """
        Private method to sort out the results directory, which should end up
        as an (existing) absolute directory that is writable.
        """
        resdir = self.__args.resdir
        if resdir:
            if not os.path.isabs(resdir):
                resdir = os.path.join(self.__rootdir, resdir)

            # Directory exists and is writable?
            if not os.path.isdir(resdir):
                log.error(f'ERROR: Results directory {resdir} not ' +
                          f'found: exiting')
                sys.exit(1)

            if not os.access(resdir, os.R_OK):
                log.error(f'ERROR: Unable to read results directory ' +
                          f'{resdir}: exiting')
                sys.exit(1)
        else:
            resdir = self.__rootdir

        self.__cooked['resdir'] = resdir

    def __readme(self, log):
        """
        Private method to sort out the README files. The README header must
        exist and be readable. The new README must be available for writing.
        The README header is opened for reading and the new README  opened for
        writing.
        """
        readme_hdr = os.path.join(self.__rootdir, 'README-header.mediawiki')
        readme = os.path.join(self.__rootdir, 'README.mediawiki')

        # Try to open the README header for reading, if it is not already opened.
        if not self.__cooked['readme_hdr']:
            # Old readme should exist.
            try:
                self.__cooked['readme_hdr'] = open(readme_hdr, 'r')
            except OSError as osex:
                log.error(f'ERROR: Could not open {readme_hdr} for reading: ' +
                          f'{osex.strerror}')
                sys.exit(1)

        # Try to open the new README for writing, if it is not already opened.
        if not self.__cooked['readme']:
            try:
                self.__cooked['readme'] = open(readme, 'w')
            except OSError as osex:
                log.error(f'ERROR: Could not open {readme} for writing: ' +
                          f'{osex.strerror}')
                sys.exit(1)

    def __resfiles(self, log):
        """
        Collate the results files as a list of absolute file names. The list
        is either the files on the command line, or all the JSON files in the
        results directory.
        """
        # Enumerate the files
        self.__cooked['resfiles'] = []

        resfiles = self.__args.resfiles
        if resfiles:
            # Specific results files from the command line
            for resf in resfiles:
                if not os.path.isabs(resf):
                    resf = os.path.join(self.__cooked['resdir'], resf)
                    if os.access(resf, os.R_OK):
                        self.__cooked['resfiles'].append(resf)
                    else:
                        log.warning(f'Warning: Unable to find result file '
                                    f'{resf}: ignored')
        else:
            # All results files - we sort to put them in alphabetica order in
            # this case.
            dirlist = sorted(os.listdir(self.__cooked['resdir']))
            for resf in dirlist:
                _, suffix = os.path.splitext(resf)
                resf = os.path.join(self.__cooked['resdir'], resf)
                if (suffix == '.json' and os.path.isfile(resf) and
                        os.access(resf, os.R_OK)):
                    self.__cooked['resfiles'].append(resf)

        if not self.__cooked['resfiles']:
            log.error(f'ERROR: No results files found')
            sys.exit(1)

    def all_args(self, log):
        """
        Sort out all the arguments, other than the logdir. Any diagnostics
        take advantage of the supplied log.

        The result is a dictionary of processed arguments. Note that this can
        be called multiple times - after the first time, it will just return
        the result from the first call.
        """
        # Results directory
        if not self.__cooked['resdir']:
            self.__resdir(log)

        # New and old readme files as needed. Note that these are file handles.
        if not (self.__cooked['readme_hdr'] and self.__cooked['readme']):
            self.__readme(log)

        # Collate all the files to be processed.
        if not self.__cooked['resfiles']:
            self.__resfiles(log)

        return self.__cooked

    def log_raw(self, log):
        """
        Record the raw argument values
        """
        log.debug('Supplied raw arguments')
        log.debug('======================')

        for arg in vars(self.__args):
            realarg = re.sub('_', '-', arg)
            val = getattr(self.__args, arg)
            log.debug(f'--{realarg:20}: {val}')

        log.debug('')

    def log_cooked(self, log):
        """
        Record the cooked argument values. No point in printing file handles!
        """
        log.debug('Supplied cooked arguments')
        log.debug('=========================')

        log.debug('Results directory: ' + self.__cooked['resdir'])

        log.debug('Results files to process:')
        for resf in self.__cooked['resfiles']:
            log.debug('  ' + resf)

        log.debug('')

    def log(self, log):
        """
        Convenience method to log both raw and cooked args
        """
        self.log_raw(log)
        self.log_cooked(log)
