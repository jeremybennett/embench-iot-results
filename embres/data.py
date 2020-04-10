#!/usr/bin/env python3

# Module to handle JSON Embench records as part of the embres package

# Copyright (C) 2019, 2020 Embecosm Limited
#
# Contributor: Jeremy Bennett <jeremy.bennett@embecosm.com>
#
# This file is part of Embench.

# SPDX-License-Identifier: GPL-3.0-or-later

"""Module with all the classes etc to capture Embench results from JSON files.

We have three main classes

- Record: The high level details of architecture, Embench version, descrption
  of the benchmark, Result for each category (size, speed, speed/MHz) and
  reference to DetailedRecord.

- Result: A record of geometric mean, geometric standard deviation, and
- derived from these low and high ranges (+/- one SD).

- DetailedRecord: All the data from the JSON file.

"""

from json import loads
from json.decoder import JSONDecodeError


class Result:
    """
    A class to capture one set of results (geometric mean and standard
    deviation) and compute the range derived from this.
    """
    def __init__(self, geomean, geosd):
        """
        Constructor sets the geometric mean and standard deviation.
        """
        # Sanity check
        assert (geomean >= 0.0), "Geometric mean must be >= 0.0."
        assert (geosd > 0.0), "Geometric standard deviation must be > 0.0."

        # Base values
        self.__geomean = geomean
        self.__geosd = geosd

    def geomean(self):
        """
        Accessor for the geometric mean
        """
        return self.__geomean

    def geosd(self):
        """
        Accessor for the geometric standard deviation
        """
        return self.__geosd

    def range_lo(self):
        """
        Accessor for the low end of the range
        """
        return self.__geomean / self.__geosd

    def range_hi(self):
        """
        Accessor for the high end of the range
        """
        return self.__geomean * self.__geosd


class DetailedRecord:
    """
    All the data on a particular run held in its JSON file.
    """
    def __init__(self, resfile):
        """
        Initialize from a JSON file. If this fails, then the data will be
        empty and we set the error fields.
        """
        self.__resfile = resfile

        self.__json_data = None
        with open(resfile) as fileh:
            try:
                self.__json_data = loads(fileh.read())
            except JSONDecodeError as jex:
                self.__json_data = None
                self.__err_lineno = jex.lineno
                self.__err_colno = jex.colno
                self.__err_msg = jex.msg

    def desc(self):
        """
        Return the description. Only valid if we actually have data.
        """
        assert self.json_data, "No valid JSON data"
        return self.__json_data['desc']

    def json_data(self):
        """
        Return the JSON data, which will be None if we have none
        """
        return self.__json_data

    def errmsg(self):
        """
        Return an error message. Only valid if we failed to get data.
        """
        assert not self.__json_data, "No error in JSON data"
        return (f'at line {self.__err_lineno}, '
                f'column {self.__err_colno}: '
                f'{self.__err_msg}')


class Record:
    """
    Top level record of a result. Its contents are mostly derived from the
    DetailedRecord, but potentially supplemented by a link to a page with
    details of the actual run.
    """
    def __init__(self, resfile):
        """
        Initialize from a JSON file. Throw an exception if the data is not
        valid.
        """
        self.__detailed_record = DetailedRecord(resfile)

        # Set up useful fields if we have them
        if self.valid_data():
            json_data = self.__detailed_record.json_data()

            self.__desc = json_data['description']
            self.__arch = json_data['architecture family']
            self.__embench_version = json_data['Embench version']

            platform_info = json_data['platform information']
            self.__cpu_mhz = platform_info['nominal clock rate (MHz)']

            # Collect data
            self.__results = dict()


            if 'relative size results' in json_data:
                size_data = json_data['relative size results']
                self.__results['Size'] = Result(
                    size_data['geometric mean'],
                    size_data['geometric standard deviation']
                )
            else:
                self.__results['Size'] = None

            if 'relative speed results' in json_data:
                speed_data = json_data['relative speed results']
                self.__results['Speed'] = Result(
                    speed_data['geometric mean'],
                    speed_data['geometric standard deviation']
                )
                self.__results['Speed/MHz'] = Result(
                    self.__results['Speed'].geomean() / self.__cpu_mhz,
                    self.__results['Speed'].geosd()
                )
            else:
                self.__results['Speed'] = None
                self.__results['Speed/MHz'] = None

    def valid_data(self, log=None):
        """
        Determine if the supplied data is valid, logging any omissions if a
        log file is provided.
        """
        json_data = self.__detailed_record.json_data()

        # Must have data
        if not json_data:
            if log:
                log.info('Invalid JSON data ' + self.__detailed_record.errmsg())
            return False

        # Must have key fields
        fields = {
            'description', 'architecture family', 'Embench version',
            'platform information',
        }

        res = True
        for field in fields:
            if not field in json_data:
                if log:
                    log.debug(f'Missing JSON field {field}')
                res = False

        if not res:
            return res

        # Must have certain platform info
        pfields = {
            'nominal clock rate (MHz)',
            'max clock rate (MHz)',
            'isa',
            'address size (bits)',
            'processor version',
            'number of enabled cores',
            'hardware threads per core',
            'caches',
            'thermal design power',
            'program memory size (kB)',
            'data memory size (kB)',
            'storage',
            'external memory',
            'external buses',
            'misc accellerators and I/O devices',
            'OS and version',
        }
        pinfo = json_data['platform information']

        res = True
        for pfield in pfields:
            if not pfield in pinfo:
                if log:
                    log.debug(f'Missing JSON plaform info {pfield}')
                res = False

        return res

    def desc(self):
        """
        Accessor for the test desc.
        """
        return self.__desc

    def arch(self):
        """
        Accessor for the architecture family.
        """
        return self.__arch

    def embench_version(self):
        """
        Accessor for the Embench version
        """
        return self.__embench_version

    def cpu_mhz(self):
        """
        Accessor for the clock speed used for the test
        """
        return self.__cpu_mhz

    def results(self):
        """
        Accessor for the list of results associated with this test.
        """
        return self.__results

    def details(self):
        """
        Accessor for the detailed results.
        """
        return self.__detailed_record
