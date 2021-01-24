#!/usr/bin/env python
import os
import sys

import subprocess


def getFileLocationThroughoutCurrentPath(fileName, currentPath='.'):
    previousDirectory = None
    currentDirectory = currentPath if currentPath != '.' else os.getcwd()
    while previousDirectory != currentDirectory:
        fileLocation = os.path.join(currentDirectory, fileName)
        if os.path.isfile(fileLocation):
            return fileLocation
        previousDirectory = currentDirectory
        currentDirectory = os.path.dirname(previousDirectory)
    return None


# Entry-point
if __name__ == "__main__":
    statTool = getFileLocationThroughoutCurrentPath('stat/stat_main.py')
    if statTool is None:
        print("fatal: STAT tool wasn't found")
        sys.exit(-1)
    else:
        cmd = [sys.executable, statTool]
        cmd.extend(sys.argv[1:])
        try:
            returnCode = subprocess.call(cmd)
            sys.exit(-1 if returnCode == 0 else 0)
        except OSError as e:
            print("fatal: unable to start STAT")
            print("fatal: %s" % e)
            sys.exit(e.errno)
