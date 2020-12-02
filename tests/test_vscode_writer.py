import os
import ast
from json import load, dumps

import stat_attributes as attributes
from services import remove, formatMakeCommand, isWindows, nameExecutable
from stat_makefile import StatMakefile

from stat_makefile_project import StatMakefileProject
from tests.testing_tools import FileBasedTestCase
from vscode_writer import VsCodeWriter

CUT = VsCodeWriter.__module__

TEST_MAKEFILE = 'simplified_example.mak'
TEST_TARGET_NAME = TEST_MAKEFILE[:-len('.mak')]
TEST_IDE_DIRECTORY = os.path.join(attributes.IDE_DIRECTORY, TEST_TARGET_NAME)
TEST_MAKEFILE_LINK = os.path.join(TEST_IDE_DIRECTORY, TEST_MAKEFILE)
TEST_FOLDERS_INIT_CONFIG = [{"name": TEST_IDE_DIRECTORY, "path": os.path.abspath(TEST_IDE_DIRECTORY)}]


class TestVsCodeWriterOnNativeOs(FileBasedTestCase):

    def _doBeforeSetup(self):
        self.isOnWindows = isWindows()

    def setUp(self):
        self._doBeforeSetup()
        self.patch(CUT, isWindows.__name__, return_value=self.isOnWindows)
        self.maxDiff = None
        if not os.path.isdir(attributes.IDE_DIRECTORY):
            os.mkdir(attributes.IDE_DIRECTORY)
        remove(TEST_IDE_DIRECTORY)
        self.makefileProject = StatMakefileProject(TEST_MAKEFILE)
        self.writer = VsCodeWriter(self.makefileProject)
        namespace = "ide_{0}".format(TEST_TARGET_NAME)
        command = formatMakeCommand(TEST_MAKEFILE, STAT_NAMESPACE=namespace)
        self.makeTool = command[0]
        self.makeArguments = command[1:]
        self.foldersInitConfig = [{"name": TEST_IDE_DIRECTORY, "path": os.path.abspath(TEST_IDE_DIRECTORY)}]

    def tearDown(self):
        remove(TEST_IDE_DIRECTORY)

    def test_initBasics(self):
        workspace = self.writer._workspace
        self.assertSameItems(["settings", "launch", "tasks", "folders"], list(workspace))
        self.assertTrue(os.path.isfile(TEST_MAKEFILE_LINK), "'{0}' not found!".format(TEST_MAKEFILE_LINK))
        for name in self.makefileProject[StatMakefile.INTERFACES].split():
            self.assertTrue(os.path.isfile(os.path.join(TEST_IDE_DIRECTORY, "dummies", name)))

    def test_innitSettings(self):
        expected = self._getExpectedSettings()
        workspace = self.writer._workspace

        self.assertSameItems(expected, workspace["settings"])

    def _getExpectedSettings(self):
        includes = ["${workspaceFolder}/dummies"]
        includes.extend([os.path.abspath(_path) for _path in self.makefileProject[StatMakefile.INCLUDES].split()])
        expected = {
            "search.showLineNumbers": True,
            "debug.inlineValues": True,
            "debug.showBreakpointsInOverviewRuler": True,
            "debug.toolBarLocation": "docked",
            "terminal.integrated.cwd": "${workspaceFolder}/../..",
            "C_Cpp.default.includePath": includes,
            "C_Cpp.default.defines": self.makefileProject.definitions,
            # "files.exclude": {"**/node_modules": True,},
        }
        return expected

    def test_initTaskConfigurations(self):
        expected = self._getExpectedTaskConfigurations()
        workspace = self.writer._workspace

        self.assertSameItems(expected, workspace["tasks"])

    def _getExpectedTaskConfigurations(self):
        expected = {
            "version": "2.0.0",
            "tasks": [
                {
                    "label": "Build",
                    "type": "shell",
                    "presentation": {
                        "echo": False,
                        "reveal": "always",
                        "focus": True,
                        "panel": "shared",
                        "showReuseMessage": True,
                        "clear": True,
                    },
                    "command": self.makeTool,
                    "args": self.makeArguments,
                    "group": {
                        "kind": "build",
                        "isDefault": True
                    },
                    "options": {
                        "cwd": "${workspaceFolder}/../.."
                    },
                    "problemMatcher": {
                        "owner": "cpp",
                        "fileLocation": [
                            "relative",
                            "${workspaceFolder}/../.."
                        ],
                        "pattern": {
                            "regexp": "^(.*):(\\d+):(\\d+):\\s+(warning|error):\\s+(.*)$",
                            "file": 1,
                            "line": 2,
                            "column": 3,
                            "severity": 4,
                            "message": 5
                        }
                    }
                },
                {
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
                    "command": self.makeTool,
                    "args": self.makeArguments + ["clean"],
                    "options": {
                        "cwd": "${workspaceFolder}/../.."
                    },
                    "problemMatcher": []
                },
                {
                    "label": "Rebuild",
                    "dependsOrder": "sequence",
                    "dependsOn": [
                        "Clean",
                        "Build"
                    ],
                    "problemMatcher": []
                }
            ]
        }
        return expected

    def _getExpectedLaunchConfigurations(self):
        workingDirectory = os.path.abspath(".")
        target = 'ide_' + self.makefileProject.name
        output = os.path.join(workingDirectory, attributes.OUTPUT_DIRECTORY, self.makefileProject.outputName, target)
        program = os.path.join(output, "bin", nameExecutable(self.makefileProject.outputName))
        debug = {
            "name": "Debug {0}".format(TEST_TARGET_NAME),
            "request": "launch",
            "preLaunchTask": "Build",
            "program": program,
            "args": [],
            "stopAtEntry": False,
            "cwd": workingDirectory,
            "environment": [],
            "externalConsole": False,
        }
        if self.isOnWindows:
            debug["type"] = "cppvsdbg"
        else:
            debug["type"] = "cppdbg"
            debug["MIMode"] = "gdb"
            debug["setupCommands"] = [
                {
                    "description": "Enable pretty-printing for gdb",
                    "text": "-enable-pretty-printing",
                    "ignoreFailures": True
                }
            ]
        return {"configurations": [debug]}

    def test_initLaunchConfigurations(self):
        expected = self._getExpectedLaunchConfigurations()
        workspace = self.writer._workspace

        self.assertSameItems(expected, workspace["launch"])

    def test_initFolders(self):
        expected = self.foldersInitConfig
        workspace = self.writer._workspace

        self.assertSameItems(expected, workspace["folders"])

    def test_addFile(self):
        _file = "./tests/example/stat_test_example.c"
        _path = os.path.normpath(os.path.dirname(_file))
        expected = self.foldersInitConfig[:] + [dict(name=_path, path=os.path.abspath(_path))]

        self.writer.addFile(_file, None)

        workspace = self.writer._workspace
        self.assertSameItems(expected, workspace["folders"])

    def test_addFilesMany(self):
        files = ["../unity/unity.c", "../lib/src/stat.c", "../lib/src/stat_rng.c"]
        paths = list(set(os.path.normpath(os.path.dirname(_file)) for _file in files))
        expected = self.foldersInitConfig[:] + [dict(name=_path, path=os.path.abspath(_path)) for _path in paths]

        files.append(os.path.join(attributes.DUMMIES_DIRECTORY, "first_dummy.h"))

        for _file in files:
            self.writer.addFile(_file, None)

        workspace = self.writer._workspace
        self.assertSameItems(expected, workspace["folders"])

    def test_write(self):
        self.writer.write()

        workspacePath = os.path.join(TEST_IDE_DIRECTORY, "{0}.vs.code-workspace".format(self.makefileProject.name))
        self.assertTrue(os.path.isfile(workspacePath))
        with open(workspacePath) as jsonFile:
            contents = ast.literal_eval(dumps(load(jsonFile)).replace("true", "True").replace("false", "False"))
            self.assertSameItems(self._getExpectedSettings(), contents.get("settings", None))
            self.assertSameItems(self._getExpectedLaunchConfigurations(), contents.get("launch", None))
            self.assertSameItems(self._getExpectedTaskConfigurations(), contents.get("tasks", None))
            self.assertSameItems(self.foldersInitConfig, contents.get("folders", None))

    def test_createTokens(self):
        writer = self.writer

        self.assertEqual(".", writer.createRootToken())
        self.assertEqual(os.path.sep.join(("parent", "child")), writer.createDirectoryToken("child", "parent"))


class TestVsCodeWriterLinux(TestVsCodeWriterOnNativeOs):

    def _doBeforeSetup(self):
        self.isOnWindows = False


class TestVsCodeWriterWindows(TestVsCodeWriterOnNativeOs):

    def _doBeforeSetup(self):
        self.isOnWindows = True
