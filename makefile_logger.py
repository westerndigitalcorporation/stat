#!/usr/bin/env python

# SPDX-FileCopyrightText: (c) 2020 Western Digital Corporation or its affiliates,
#                             Arseniy Aharonov <arseniy@aharonov.icu>
#
# SPDX-License-Identifier: MIT

import os

import stat_attributes as attributes


class MakefileLogger(object):

    def __init__(self, makefileName, beSilent=False):
        self._makefile = makefileName
        self._isSilent = beSilent
        if not os.path.isdir(attributes.LOGS_DIRECTORY):
            os.mkdir(attributes.LOGS_DIRECTORY)
        logfilePath = os.path.join(attributes.LOGS_DIRECTORY, '.'.join([os.path.splitext(makefileName)[0], 'log']))
        self._logfile = open(logfilePath, 'w')

    def write(self, line):
        lineToLog = line.strip()
        if not self._isSilent:
            print(lineToLog)
        self._logfile.write(line)

    def __del__(self):
        self._logfile.close()
