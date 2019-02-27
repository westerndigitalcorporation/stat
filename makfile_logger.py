#!/usr/bin/env python
import os
from services import config


class MakfileLogger(object):

    def __init__(self, makfileName, beSilent = False):
        self._makfile = makfileName
        self._isSilent = beSilent
        if not os.path.isdir(config.LOGS_DIRECTORY):
            os.mkdir(config.LOGS_DIRECTORY)
        logfilePath = os.path.join(config.LOGS_DIRECTORY, '.'.join([os.path.splitext(makfileName)[0], 'log']))
        self._logfile = open(logfilePath,'w')

    def write(self, line):
        lineToLog = line.strip('\n')
        if not self._isSilent:
            print(lineToLog)
        self._logfile.write(line)

    def __del__(self):
        self._logfile.close()