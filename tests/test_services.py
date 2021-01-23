#!/usr/bin/env python
import subprocess
from io import TextIOWrapper
from shutil import copyfile

import services
from stat_attributes import OUTPUT_DIRECTORY, PRODUCT_DIRECTORY
from tests.testing_tools import *  # pylint: disable=unused-wildcard-import


CUT = services.__name__


class TestServices(FileBasedTestCase):

    def setUp(self):
        self._fakeOs = FakeOs('services')
        services.remove(OUTPUT_DIRECTORY)

    def tearDown(self):
        self._fakeOs.restoreOriginalModule()
        services.remove(OUTPUT_DIRECTORY)

    def test_isWindows(self):
        self.patch(CUT, 'platform.system', side_effect=['linux', 'Windows'])
        self.assertFalse(services.isWindows())
        self.assertTrue(services.isWindows())

    def test_toWindowsPath(self):
        original = 'home/feature/inc'
        expected = 'home\\feature\\inc'
        self.assertEqual(expected, services.toWindowsPath(expected))
        self.assertEqual(expected, services.toWindowsPath(original))

    def test_toPosixPath(self):
        original = 'home\\feature\\inc'
        expected = 'home/feature/inc'
        self.assertEqual(expected, services.toPosixPath(expected))
        self.assertEqual(expected, services.toPosixPath(original))

    def test_createLinkOnLinux(self):
        patcher = self.patch(CUT, subprocess.__name__)
        self.patch(CUT, 'platform.system', return_value='linux')

        source = "/home/product/fw/inc/example.h"
        target = "/home/tests/fw/inc/example.h"
        services.createLink(source, target)

        self.assertCalls(patcher, [])
        self.assertEqual(1, len(self._fakeOs['symlink']))
        symlinkCall = self._fakeOs['symlink'][0]
        expectedSource = os.path.join(*"../../../product/fw/inc/example.h".split('/'))
        self.assertEqual(expectedSource, symlinkCall.source)
        self.assertEqual(target, symlinkCall.target)

    def test_createLinkOnWindowsForFile(self):
        patcher = self.patch(CUT, subprocess.__name__)
        self.patch(CUT, 'platform.system', return_value='Windows')

        source = "/home/product/fw/inc/example.h"
        target = "/home/tests/fw/inc/example.h"
        services.createLink(source, target)

        commandLine = services.formatCommandLine('cmd /c mklink "{target}" "{source}" >nul'.format(
            target=services.toWindowsPath(target), source=services.toWindowsPath("../../../product/fw/inc/example.h")))
        self.assertCalls(patcher, [call.Popen(commandLine, shell=True), call.Popen().wait()])
        self.assertEqual(0, len(self._fakeOs['symlink']))

    def test_createLinkOnWindowsForDirectory(self):
        patcher = self.patch(CUT, subprocess.__name__)
        self.patch(CUT, 'platform.system', return_value='Windows')
        self._fakeOs.path.addMockForFunction('isdir', True)

        source = "/home/product/fw/inc"
        target = "/home/tests/fw/inc"
        services.createLink(source, target)

        self.assertEqual(0, len(self._fakeOs['symlink']))
        commandLine = services.formatCommandLine('cmd /c mklink /D "{target}" "{source}" >nul'.format(
            target=services.toWindowsPath(target), source=services.toWindowsPath("../../product/fw/inc")))
        self.assertCalls(patcher, [call.Popen(commandLine, shell=True), call.Popen().wait()])

    def test_findSubFolderOnPathOfCurrentWorkingDirectory(self):
        currentPath = '/system/tools/bin'
        subFolder = 'vc'
        expected = os.path.join(currentPath, subFolder)
        self.patch(CUT, 'os.getcwd', return_value=currentPath)
        patcher = self.patch(CUT, 'os.path.isdir', return_value=True)
        self.assertEqual(expected, services.findSubFolderOnPath(subFolder))
        self.assertCalls(patcher, [call(expected)])

    def test_findSubFolderOnPathWhenLocatedOnSubTree(self):
        locationPath = '/system/tools/bin'
        startingPath = '/'.join([locationPath] + ['leaf']*2)
        subFolder = 'vc'
        expected = os.path.join(locationPath, subFolder)
        patcher = self.patch(CUT, 'os.path.isdir', side_effect=[False, False, True])
        self.assertEqual(expected, services.findSubFolderOnPath(subFolder, startingPath))
        self.assertCalls(patcher, [
            call(os.path.join('/'.join([locationPath] + ['leaf'] * 2), subFolder)),
            call(os.path.join('/'.join([locationPath] + ['leaf']), subFolder)),
            call(os.path.join(expected)),
        ])

    def test_findSubFolderOnPathWhenNotExisting(self):
        startingPath = '/bad-path/system/tools/bin'
        subFolder = 'vc'
        self.patch(CUT, 'os.path.isdir', side_effect=[False] * startingPath.count('/'))
        self.assertEqual(None, services.findSubFolderOnPath(subFolder, startingPath))

    def test_getFileLocationThroughoutCurrentPathUponCurrentDirectoryFile(self):
        filePath = os.path.join(*'/home/product/config.mak'.split('/'))
        currentPath = os.path.dirname(filePath)
        self._fakeOs.addMockForFunction('getcwd', currentPath)
        self._fakeOs.path.addMockForFunction('isfile', True)
        location = services.getFileLocationThroughoutCurrentPath(os.path.basename(filePath))
        self.assertEqual(filePath, location)

    def test_getFileLocationThroughoutCurrentPathUponNotExistingFile(self):
        filePath = os.path.join(*'/home/product/config.mak'.split('/'))
        currentPath = os.path.dirname(filePath)
        self._fakeOs.addMockForFunction('getcwd', currentPath)
        for dummyIndex in range(len(services.toPosixPath(filePath).split('/'))):
            self._fakeOs.path.addMockForFunction('isfile', False)
        location = services.getFileLocationThroughoutCurrentPath(os.path.basename(filePath))
        self.assertIsNone(location)

    def test_getFileLocationThroughoutCurrentPathUponFileFromSomeParentDirectory(self):
        filePath = os.path.join(*'/home/product/config.mak'.split('/'))
        cwdOffset = os.path.join(*'fw/module/src'.split('/'))
        currentPath = os.path.join(os.path.dirname(filePath), cwdOffset)
        self._fakeOs.addMockForFunction('getcwd', currentPath)
        for dummyIndex in range(len(services.toPosixPath(cwdOffset).split('/'))):
            self._fakeOs.path.addMockForFunction('isfile', False)
        self._fakeOs.path.addMockForFunction('isfile', True)
        location = services.getFileLocationThroughoutCurrentPath(os.path.basename(filePath))
        self.assertEqual(filePath, location)

    def test_listMakefiles(self):
        pathName = '.'
        makefiles = ['full_example.mak', 'simple.mak', 'simplified_example.mak']
        self.assertSameItems(makefiles, services.listMakefiles(pathName))

        exampleMakefiles = ['full_example.mak', 'simplified_example.mak']
        self.assertSameItems(exampleMakefiles, services.listMakefiles(pathName, '*example*.*'))

        noteOverlappingPatternFiles = ['full_example.mak', 'simple.mak']
        self.assertSameItems(noteOverlappingPatternFiles, services.listMakefiles(pathName, 'full*.*', 'simple*.*'))

        self.assertSameItems(makefiles, services.listMakefiles(pathName, '*example.*', 's*.*'))

        pathName = './' + PRODUCT_DIRECTORY
        makefiles = ['product.mak', 'product_derived.mak']
        self.assertSameItems(makefiles, services.listMakefiles(pathName))

        makefiles = ['product_derived.mak']
        self.assertSameItems(makefiles, services.listMakefiles(pathName, '*_*.*'))

        makefiles = ['product_ignored.mak']
        self.assertSameItems(makefiles, services.listMakefiles(pathName, 'product_ignored.mak'))

        self.assertSameItems([], services.listMakefiles(pathName, '*example*.*'))

    def test_readNonEmptyLines(self):
        filePath = '/c/some_file.txt'
        expected = ['first line', 'second line', 'third line']
        openPatcher = self.patchOpen()
        openPatcher.return_value.readlines.return_value = [' \n'] + [' ' + line + ' \n' for line in expected[:-1]] + expected[-1:]
        received = list(services.readNonEmptyLines(filePath))
        self.assertListEqual(expected, received)

    def test_readTextFileAtOnce(self):
        filePath = '/root/some_text_file.txt'
        expected = """
        Expected text-contents of the file,
        which shall be read by the 
        tested routine.
        
        Ta,
        Test
        """
        openPatcher = self.patchOpen(read_data=expected)
        received = services.readTextFileAtOnce(filePath)
        self.assertEqual(expected, received)
        self.assertCalls(openPatcher, [
            call(filePath, 'r'), call().__enter__(), call().read(), call().__exit__(None, None, None)
        ])

    def test_remove(self):
        self._emulateNonEmptyFileTree()
        services.remove(OUTPUT_DIRECTORY)
        self.assertFalse(os.path.isdir(OUTPUT_DIRECTORY))

    def test_removeUponAntiVirusLockups(self):
        retries = 3
        rmTreePatcher = self._patchRmtree(retries=retries)
        osRemovePatcher = self._patchOsRemove(retries=retries)

        self._emulateNonEmptyFileTree()

        services.remove(OUTPUT_DIRECTORY)

        self.assertFalse(osRemovePatcher.called)
        self.assertEqual([call(OUTPUT_DIRECTORY)] * (retries + 1), rmTreePatcher.call_args_list)

    def test_removeFile(self):
        retries = 2
        fileName = 'full_example.mak'
        filePath = os.path.join(OUTPUT_DIRECTORY, fileName)
        os.makedirs(OUTPUT_DIRECTORY)
        copyfile('full_example.mak', filePath)
        rmTreePatcher = self._patchRmtree(retries=retries)
        osRemovePatcher = self._patchOsRemove(retries=retries)

        services.remove(filePath)

        self.assertFalse(rmTreePatcher.called)
        self.assertEqual([call(filePath)] * (retries + 1), osRemovePatcher.call_args_list)

    def test_locateResource(self):
        resource = 'si4project.zip'
        expected = os.path.abspath(os.path.join('..', attributes.RESOURCES_DIRECTORY, resource))
        self.assertEqual(expected, services.locateResource(resource))

    def test_locateResourceForNonExisting(self):
        try:
            services.locateResource('non_existing.resource')
        except services.ServicesException:
            pass
        else:
            self.fail('The operation should have raised an exception')

    def test_formatMakeCommand_onLinux64(self):
        self.patch(CUT, services.getPlatform.__name__, return_value="Linux64")
        makeTool = attributes.MAKE_TOOL["Linux64"]
        filename = "some_make_file.mak"
        expected = [makeTool, "-f", filename]

        command = services.formatMakeCommand(filename)

        self.assertEqual(expected, command)

    def test_formatMakeCommand_onLinux32WithMakeInstalled(self):
        self.patch(CUT, services.getPlatform.__name__, return_value="Linux32")
        makeTool = "make"
        self.patch(CUT, services.locateFile.__name__, return_value=makeTool)
        filename = "some_make_file.mak"
        expected = [makeTool, "-f", filename]

        command = services.formatMakeCommand(filename)

        self.assertEqual(expected, command)

    def test_formatMakeCommand_simpleOnWindows32Bit(self):
        self.patch(CUT, services.getPlatform.__name__, return_value="Windows32")
        filename = "some_make_file.mak"
        makeTool = attributes.MAKE_TOOL["Windows32"]
        expected = [makeTool, "-f", filename]

        command = services.formatMakeCommand(filename)

        self.assertEqual(expected, command)

    def test_formatMakeCommand_simpleOnWindows64Bit(self):
        self.patch(CUT, services.getPlatform.__name__, return_value="Windows64")
        filename = "some_make_file.mak"
        makeTool = attributes.MAKE_TOOL["Windows64"]
        expected = [makeTool, "-f", filename]

        command = services.formatMakeCommand(filename)

        self.assertEqual(expected, command)

    def test_formatMakeCommand_withArguments(self):
        self.patch(CUT, services.getPlatform.__name__, return_value="Windows64")
        filename = "some_make_file.mak"
        makeTool = attributes.MAKE_TOOL["Windows64"]
        args = ["clean", "build"]
        expected = [makeTool, "-f", filename] + args

        command = services.formatMakeCommand(filename, args)

        self.assertEqual(expected, command)

    def test_formatMakeCommand_withArgumentsAndVars(self):
        self.patch(CUT, services.getPlatform.__name__, return_value="Windows64")
        filename = "some_make_file.mak"
        args = ["clean", "build"]
        expected = ["clean", "build", 'SOME_NAME="some-value"', 'ANOTHER="anotherValue"']

        command = services.formatMakeCommand(filename, args, SOME_NAME="some-value", ANOTHER="anotherValue")

        self.assertSameItems(expected, command[-4:])

    def test_formatMakeCommand_uponUnknownPlatform(self):
        self.patch(CUT, services.getPlatform.__name__, return_value="unknown-fake")
        filename = "some_make_file.mak"
        expected = ["make", "-f", filename]

        command = services.formatMakeCommand(filename)

        self.assertEqual(expected, command)

    def _patchRmtree(self, retries=0):
        self.__rmtreeRetries = retries

        def rmtreeFake(pathName):
            if self.__rmtreeRetries > 0:
                self.__rmtreeRetries -= 1
                raise OSError("Emulated lockup by Anti-Virus.")
            else:
                rmtree(pathName)

        patcher = self.patch('services', 'rmtree')
        self.patch('services', 'sleep')
        patcher.side_effect = rmtreeFake
        return patcher

    def _patchOsRemove(self, retries=0):
        self.__removeRetries = retries

        def osRemove(pathName):
            if self.__removeRetries > 0:
                self.__removeRetries -= 1
                raise OSError("Emulated lockup by Anti-Virus.")
            else:
                os.remove(pathName)

        patcher = self.patch('services', 'os.remove')
        self.patch('services', 'sleep')
        patcher.side_effect = osRemove
        return patcher

    @staticmethod
    def _emulateNonEmptyFileTree():
        def listByFileExtension(directory, extension):
            return (fileName for fileName in os.listdir(directory) if
                    os.path.isfile(fileName) and os.path.splitext(fileName)[1] == extension)

        os.makedirs(OUTPUT_DIRECTORY)
        for filename in listByFileExtension(directory='.', extension='.h'):
            copyfile(filename, os.path.join(OUTPUT_DIRECTORY, filename))

        for filename in listByFileExtension(directory='.', extension='.c'):
            copyfile(filename, os.path.join(OUTPUT_DIRECTORY, filename.replace('.c', '.obj')))


class TestLocateFile(FileBasedTestCase):

    def test_locateFile_overExplicitPath(self):
        filepath = services.locateFile("some_file.txt", path=".")
        self.assertEqual("", filepath)

        filepath = services.locateFile("simple.mak", path=".")
        self.assertEqual(os.path.join(".", "simple.mak"), filepath)

        filepath = services.locateFile("stat_another_example.c", path=['.', '..'])
        self.assertEqual("", filepath)

        filepath = services.locateFile("stat_another_example.c", path=['.', './tests/example', '..'])
        self.assertEqual(os.path.join("./tests/example", "stat_another_example.c"), filepath)

    def test_locateFile_inAllImplicitlyAvailableLocations(self):
        self.patchDict(os.environ, {"PATH": os.pathsep.join([os.path.abspath("./tests"),
                                                             os.path.abspath("./tests/example"),
                                                             os.path.abspath("./prducts")])})

        filepath = services.locateFile("simple.mak")
        self.assertEqual(os.path.abspath(os.path.join(".", "simple.mak")), filepath)

        filepath = services.locateFile("stat_another_example.c")
        self.assertEqual(os.path.abspath(os.path.join("./tests/example", "stat_another_example.c")), filepath)

    def test_locateFile_withExplicitAccessMode(self):
        filepath = services.locateFile("simple.mak", os.X_OK)
        self.assertEqual("", filepath)

    def test_locateFile_executableOnWindowsWithSpecifiedExtension(self):
        self.patchDict(os.environ, {"PATHEXT": os.pathsep.join([".EXE", ".COM"])})
        _isWindows = self.patch(CUT, isWindows.__name__)
        self.patchObject(os, os.access.__name__, return_value=True)

        _isWindows.return_value = False
        filepath = services.locateFile("simple.mak", os.X_OK)
        self.assertEqual(os.path.abspath(os.path.join(".", "simple.mak")), filepath)

        _isWindows.return_value = True
        filepath = services.locateFile("simple.mak", os.X_OK)
        self.assertEqual("", filepath)

    def test_locateFile_executableOnWindowsWithoutExtension(self):
        self.patchDict(os.environ, {"PATHEXT": os.pathsep.join([".bat", ".exe", ".com"])})
        self.patch(CUT, isWindows.__name__, return_value=True)
        self.patchObject(os, os.access.__name__, return_value=True)

        print(os.path.abspath(os.curdir))
        filepath = services.locateFile("vswhere", os.X_OK, "../resources")
        self.assertEqual(os.path.join("../resources", "vswhere.exe"), filepath)

        filepath = services.locateFile("vswhere", path="../resources")
        self.assertEqual("", filepath)


TEST_PATH = './{0}/path/to/check'.format(OUTPUT_DIRECTORY)


class TestMkdir(FileBasedTestCase):

    def setUp(self):
        services.remove(OUTPUT_DIRECTORY)

    def test_mkdir_basic(self):
        services.mkdir(TEST_PATH)
        self.assertTrue(os.path.isdir(TEST_PATH))

    def test_mkdir_illegalDuplication(self):
        services.mkdir(TEST_PATH)
        try:
            services.mkdir(TEST_PATH)
        except OSError:
            pass
        else:
            self.fail("An OS-Error exception is expected!")
        self.assertTrue(os.path.isdir(TEST_PATH))

    def test_mkdir_formalDuplication(self):
        services.mkdir(TEST_PATH)
        services.mkdir(TEST_PATH, exist_ok=True)
        self.assertTrue(os.path.isdir(TEST_PATH))


TEST_FAKE_OUTPUT = ['first line\n', 'second line\n', 'third line\n', '\n']
TEST_FAKE_RETURN_CODE = 0xC0DE
TEST_COMMAND_LINE = "{0} -m tests.test_services".format(
    "python" if sys.version_info < (3, 0) or isWindows() else "python3")


class TestExecute(AdvancedTestCase):

    def setUp(self):
        self.printMock = self.patchBuiltinObject('print')

    def test_executeWithSuccess(self):

        status, receivedOutput = services.execute(TEST_COMMAND_LINE + " --pass")

        self.assertEqual(0, status)
        self.assertEqual(TEST_FAKE_OUTPUT, receivedOutput)
        expected = [call(line, end='') for line in TEST_FAKE_OUTPUT]
        self.assertCalls(self.printMock, expected)

    def test_executeSilently(self):

        status, receivedOutput = services.execute(TEST_COMMAND_LINE + " --pass", beSilent=True)

        self.assertEqual(0, status)
        self.assertEqual(TEST_FAKE_OUTPUT, receivedOutput)
        self.assertCalls(self.printMock, [])

    def test_executeWithFailure(self):
        status, receivedOutput = services.execute(TEST_COMMAND_LINE + " --fail")

        self.assertNotEqual(0, status)
        self.assertEqual([], receivedOutput)
        self.assertCalls(self.printMock, [])

    def test_executeCorrectness(self):
        fakeCommand = "some fake command to passed as a list"
        pOpen = self.__patchPOpen()

        services.execute(fakeCommand)

        expected = [call(services.formatCommandLine(fakeCommand), bufsize=1, universal_newlines=True,
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT), call().communicate()]
        self.assertCalls(pOpen, expected)

    def test_executeCustomKwargs(self):
        fakeCommand = "some fake command to passed as a list"
        pOpen = self.__patchPOpen()

        services.execute(fakeCommand, env={})

        expected = [call(services.formatCommandLine(fakeCommand), bufsize=1, universal_newlines=True,
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env={}), call().communicate()]
        self.assertCalls(pOpen, expected)

    def __patchPOpen(self):
        pOpen = self.patch(CUT, '.'.join([subprocess.__name__, subprocess.Popen.__name__]))
        stdoutMock = Mock(spec=TextIOWrapper)
        stdoutMock.readline.side_effect = TEST_FAKE_OUTPUT
        process = pOpen.return_value
        type(process).stdout = PropertyMock(return_value=stdoutMock)
        type(process).returncode = PropertyMock(return_value=TEST_FAKE_RETURN_CODE)
        return pOpen


class TestExecuteForOutput(AdvancedTestCase):

    TEST_FAKE_OUTPUT = ''.join(TEST_FAKE_OUTPUT).strip()

    def test_executeForOutputWithSuccess(self):
        receivedOutput = services.executeForOutput(TEST_COMMAND_LINE + " --pass")
        self.assertEqual(self.TEST_FAKE_OUTPUT, receivedOutput)

    def test_executeForOutputWithFailure(self):
        receivedOutput = services.executeForOutput(TEST_COMMAND_LINE + " --fail")
        self.assertEqual('', receivedOutput)

    def test_executeForOutputCorrectness(self):
        fakeCommand = "some fake command to passed as a list"
        pOpen = self.patch(CUT, '.'.join([subprocess.__name__, subprocess.Popen.__name__]))
        pOpen.return_value.communicate.return_value = ('', None)

        services.executeForOutput(fakeCommand)

        expected = [call(services.formatCommandLine(fakeCommand), bufsize=1, universal_newlines=True,
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT), call().communicate()]
        self.assertCalls(pOpen, expected)

    def test_executeForOutputCustomKwargs(self):
        fakeCommand = "some fake command to passed as a list"
        pOpen = self.patch(CUT, '.'.join([subprocess.__name__, subprocess.Popen.__name__]))
        pOpen.return_value.communicate.return_value = ('', None)

        services.executeForOutput(fakeCommand, env={})

        expected = [call(services.formatCommandLine(fakeCommand), bufsize=1, universal_newlines=True,
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env={}), call().communicate()]
        self.assertCalls(pOpen, expected)


class TestWriteJsonFile(AdvancedTestCase):

    def setUp(self):
        self.open = self.patchOpen()
        self.dumpJson = self.patch(CUT, 'dumpJson')

    def test_writeJsonFile(self):
        fileName = 'some_file.json'
        data = {'Level-A': {'Level-B': ['results-1', 'results-2']}}

        services.writeJsonFile(fileName, data)

        self.assertCalls(self.open, [call(fileName, 'w'), call().__enter__(), call().__exit__(None, None, None)])
        self.assertCalls(self.dumpJson, [call(data, self.open.return_value, indent=3)])


if __name__ == '__main__':
    if sys.argv[1] == '--pass':
        for _line in TEST_FAKE_OUTPUT:
            print(_line.strip())
    elif sys.argv[1] == '--fail':
        sys.exit(-1)
