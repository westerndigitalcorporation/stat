from __future__ import print_function

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
        cmd = [sys.executable, "-m", "cProfile", statTool]
        cmd.extend(sys.argv[1:])
        try:
            process = subprocess.Popen(cmd, bufsize=1, universal_newlines=True,
                                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            with open('_stat_profiling.txt', 'w') as fp:
                for line in iter(process.stdout.readline, ''):
                    print(line, end='')
                    fp.write(line)
                    fp.flush()
                process.wait()
            sys.exit(process.returncode)
        except OSError as e:
            print("fatal: unable to start STAT")
            print("fatal: %s" % e)
            sys.exit(e.errno)
