#!/usr/bin/env python
# SPDX-FileCopyrightText: (c) 2020 Western Digital Corporation or its affiliates,
#                             Arseniy Aharonov <arseniy@aharonov.icu>
#
# SPDX-License-Identifier: MIT
import os
import shutil
from json import dump

import stat_attributes as attributes

from ide_writer import IdeWriter
from services import mkdir, createLink, nameExecutable, isWindows
from stat_makefile import StatMakefile


class VsCodeWriter(IdeWriter):
    IDE = 'VS-Code'

    def __init__(self, contents, *args, **kwargs):
        super(VsCodeWriter, self).__init__(contents, *args, **kwargs)
        self.__ideLocation = os.path.join(attributes.IDE_DIRECTORY, contents.name)
        self._workspace = {}
        self.__folders = []
        self.__prepareIdeFileTreeStructure(contents)
        self.__buildSettings()
        self.__buildLaunchConfiguration()
        self.__buildTaskConfigurations()
        self.__buildFoldersConfiguration()

    def __prepareIdeFileTreeStructure(self, contents):
        dummiesLocation = os.path.join(self.__ideLocation, "dummies")
        mkdir(self.__ideLocation, exist_ok=True)
        mkdir(dummiesLocation, exist_ok=True)
        target = os.path.abspath(os.path.join(self.__ideLocation, contents.makefile))
        if not os.path.isfile(target):
            createLink(contents.makefile, target)
        for name in self.__getItems(StatMakefile.INTERFACES):
            target = os.path.abspath(os.path.join(dummiesLocation, name))
            source = os.path.join(attributes.DUMMIES_DIRECTORY, name)
            if not os.path.isfile(target):
                createLink(source, target)

    def __buildSettings(self):
        includes = ["${workspaceFolder}/dummies"]
        includes.extend([os.path.abspath(_path) for _path in self.__getItems(StatMakefile.INCLUDES)])
        defines = self._contents.definitions
        settings = {
            "search.showLineNumbers": True,
            "debug.inlineValues": True,
            "debug.showBreakpointsInOverviewRuler": True,
            "debug.toolBarLocation": "docked",
            "terminal.integrated.cwd": "${workspaceFolder}/../..",
            "C_Cpp.default.includePath": includes,
            "C_Cpp.default.defines": defines,
        }
        self._workspace["settings"] = settings

    def __getItems(self, name):
        return self._contents[name].split()

    def __buildLaunchConfiguration(self):
        cwd = os.path.abspath(".")
        program = os.path.join(cwd, attributes.OUTPUT_DIRECTORY, self._contents.outputName,
                               'ide_' + self._contents.name, "bin", nameExecutable(self._contents.outputName))
        debug = dict(
            name="Debug {0}".format(self._contents.name), cwd=cwd, program=program, preLaunchTask="Build",
            request="launch", args=[], environment=[], stopAtEntry=False, externalConsole=False,
        )
        if isWindows():
            debug["type"] = "cppvsdbg"
        else:
            setupCommands = [
                dict(description="Enable pretty-printing for gdb", text="-enable-pretty-printing", ignoreFailures=True),
            ]
            debug.update(dict(type="cppdbg", MIMode="gdb", setupCommands=setupCommands))
        self._workspace["launch"] = {"configurations": [debug]}

    def __buildTaskConfigurations(self):
        command = self.formatMakeCommand("clean")
        clean = {
            "label": "Clean",
            "type": "shell",
            "presentation": {
                "echo": False,
                "reveal": "always",
                "focus": True,
                "panel": "shared",
                "showReuseMessage": True,
                "clear": True
            },
            "command": command[0],
            "args": command[1:],
            "options": {
                "cwd": "${workspaceFolder}/../.."
            },
            "problemMatcher": []
        }
        build = clean.copy()
        build["label"] = "Build"
        build["args"] = command[1:]
        build["args"].remove("clean")
        build["problemMatcher"] = {
            "owner": "cpp",
            "fileLocation": ["relative", "${workspaceFolder}/../.."],
            "pattern": {"regexp": "^(.*):(\\d+):(\\d+):\\s+(warning|error):\\s+(.*)$",
                        "file": 1, "line": 2, "column": 3, "severity": 4, "message": 5}
        }
        build["group"] = {"kind": "build", "isDefault": True}
        rebuild = {"label": "Rebuild",
                   "dependsOrder": "sequence",
                   "dependsOn": ["Clean", "Build"],
                   "problemMatcher": []}
        tasks = [build, clean, rebuild]
        self._workspace["tasks"] = {"version": "2.0.0", "tasks": tasks}

    def __buildFoldersConfiguration(self):
        folders = [dict(name=self.__ideLocation, path=os.path.abspath(self.__ideLocation))]
        self.__folders.extend([self.__ideLocation, os.path.normpath(attributes.DUMMIES_DIRECTORY)])
        self._workspace["folders"] = folders

    def createRootToken(self):
        return "."

    def createDirectoryToken(self, name, parentDirectoryToken):
        return parentDirectoryToken + os.path.sep + name

    def addFile(self, filePath, parentDirectoryToken):
        _path = os.path.normpath(os.path.dirname(filePath))
        if _path not in self.__folders:
            self.__folders.append(_path)
            self._workspace["folders"].append(dict(name=_path, path=os.path.abspath(_path)))

    def write(self):
        _path = os.path.join(self.__ideLocation, "{0}.vs.code-workspace".format(self._contents.name))
        _file = open(_path, "w")
        dump(self._workspace, _file)
        _file.close()
        print('VS-Code Workspace "{path}" was build'.format(path=_path))
