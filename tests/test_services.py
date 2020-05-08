#!/usr/bin/env python
import subprocess
from io import TextIOWrapper
from shutil import copyfile
from mock import Mock, PropertyMock

from stat_attributes import OUTPUT_DIRECTORY, PRODUCT_DIRECTORY
from testing_tools import *
import services

CUT = services.__name__

def _rmtree(treePath):
    if os.path.isdir(treePath):
        rmtree(treePath)

class TestServices(FileBasedTestCase):

    def setUp(self):
        self._fakeOs = FakeOs('services')
        _rmtree(OUTPUT_DIRECTORY)

    def tearDown(self):
        self._fakeOs.restoreOriginalModule()
        _rmtree(OUTPUT_DIRECTORY)

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

        commandLine = 'cmd /c mklink "{target}" "{source}"'.format(target = services.toWindowsPath(target),
            source = services.toWindowsPath("../../../product/fw/inc/example.h"))
        self.assertCalls(patcher, [call.Popen(commandLine, shell=True),call.Popen().wait()])
        self.assertEqual(0, len(self._fakeOs['symlink']))

    def test_createLinkOnWindowsForDirectory(self):
        patcher = self.patch(CUT, subprocess.__name__)
        self.patch(CUT, 'platform.system', return_value='Windows')
        self._fakeOs.path.addMockForFunction('isdir', True)

        source = "/home/product/fw/inc"
        target = "/home/tests/fw/inc"
        services.createLink(source, target)

        self.assertEqual(0, len(self._fakeOs['symlink']))
        commandLine = 'cmd /c mklink /D "{target}" "{source}"'.format(target = services.toWindowsPath(target),
            source = services.toWindowsPath("../../product/fw/inc"))
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
        patcher = self.patch(CUT, 'os.path.isdir', side_effect=[False,False,True])
        self.assertEqual(expected, services.findSubFolderOnPath(subFolder, startingPath))
        self.assertCalls(patcher,[
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
        for i in range(len(services.toPosixPath(filePath).split('/'))):
            self._fakeOs.path.addMockForFunction('isfile', False)
        location = services.getFileLocationThroughoutCurrentPath(os.path.basename(filePath))
        self.assertIsNone(location)

    def test_getFileLocationThroughoutCurrentPathUponFileFromSomeParentDirectory(self):
        filePath = os.path.join(*'/home/product/config.mak'.split('/'))
        cwdOffset = os.path.join(*'fw/module/src'.split('/'))
        currentPath = os.path.join(os.path.dirname(filePath), cwdOffset)
        self._fakeOs.addMockForFunction('getcwd', currentPath)
        for i in range(len(services.toPosixPath(cwdOffset).split('/'))):
            self._fakeOs.path.addMockForFunction('isfile', False)
        self._fakeOs.path.addMockForFunction('isfile', True)
        location = services.getFileLocationThroughoutCurrentPath(os.path.basename(filePath))
        self.assertEqual(filePath, location)

    def test_listMakfiles(self):
        pathName = '.'
        makfiles = ['full_example.mak', 'simple.mak', 'simplified_example.mak']
        self.assertSameItems(makfiles, services.listMakefiles(pathName))

        exampleMakfiles = ['full_example.mak', 'simplified_example.mak']
        self.assertSameItems(exampleMakfiles, services.listMakefiles(pathName, '*example*.*'))

        noteOverlappingPatternFiles = ['full_example.mak', 'simple.mak']
        self.assertSameItems(noteOverlappingPatternFiles, services.listMakefiles(pathName, 'full*.*', 'simple*.*'))

        self.assertSameItems(makfiles, services.listMakefiles(pathName, '*example.*', 's*.*'))

        pathName = './' + PRODUCT_DIRECTORY
        makfiles = ['product.mak', 'product_derived.mak']
        self.assertSameItems(makfiles, services.listMakefiles(pathName))

        makfiles = ['product_derived.mak']
        self.assertSameItems(makfiles, services.listMakefiles(pathName, '*_*.*'))

    def test_readTextFileLines(self):
        filePath ='/c/some_file.txt'
        expected = ['first line', 'second line', 'third line']
        openPatcher = self.patchOpen()
        openPatcher.return_value.readlines.return_value = [line + '\n' for line in expected]
        received = list(services.readTextFileLines(filePath))
        self.assertListEqual(expected, received)
        self.assertCalls(openPatcher, [call(filePath), call().readlines(), call().close()])

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
        expected = os.path.join('..', attributes.RESOURCES_DIRECTORY, resource)
        self.assertEqual(expected, services.locateResource(resource))

    def test_locateResourceForNonExisting(self):
        try:
            services.locateResource('non_existing.resource')
        except services.ServicesException:
            pass
        else:
            self.fail('The operation should have raised an exception')

    def _patchRmtree(self, retries = 0):
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

    def _patchOsRemove(self, retries = 0):
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


TEST_PATH = './{0}/path/to/check'.format(OUTPUT_DIRECTORY)
class TestMkdir(FileBasedTestCase):

    def setUp(self):
        _rmtree(OUTPUT_DIRECTORY)

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

TEST_FAKE_OUTPUT = ['first line\n', 'second line\n', 'third line\n', '']
TEST_FAKE_RETURN_CODE = 0xC0DE
class TestExecute(AdvancedTestCase):

    def setUp(self):
        process = Mock(spec=subprocess.Popen)
        stdoutMock = Mock(spec=TextIOWrapper)
        stdoutMock.readline.side_effect = TEST_FAKE_OUTPUT
        returnCode = PropertyMock(return_value=TEST_FAKE_RETURN_CODE)
        type(process).stdout = PropertyMock(return_value=stdoutMock)
        type(process).returncode = returnCode
        self.pOpen = self.patch(CUT, '.'.join([subprocess.__name__, subprocess.Popen.__name__]), return_value=process)
        self.process = process
        self.printMock = self.patchBuiltinObject('print')
        self.returnCode = returnCode

    def test_execute_simple(self):
        fakeCommand = "some fake command"

        status, receivedOutput = services.execute(fakeCommand)

        expected = [call(fakeCommand, bufsize=1, universal_newlines=True,
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT)]
        self.assertCalls(self.pOpen, expected)
        self.assertCalls(self.process, [call.wait()])
        self.assertEqual(TEST_FAKE_RETURN_CODE, status)
        expected = TEST_FAKE_OUTPUT[:-1]
        self.assertEqual(expected, receivedOutput)
        expected = [call(line, end='') for line in expected]
        self.assertCalls(self.printMock, expected)

    def test_execute_silent(self):
        fakeCommand = "some fake command to be executed silently"

        status, receivedOutput = services.execute(fakeCommand, beSilent=True)

        expected = [call(fakeCommand, bufsize=1, universal_newlines=True,
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT)]
        self.assertCalls(self.pOpen, expected)
        self.assertCalls(self.process, [call.wait()])
        self.assertEqual(TEST_FAKE_RETURN_CODE, status)
        expected = TEST_FAKE_OUTPUT[:-1]
        self.assertEqual(expected, receivedOutput)
        self.assertCalls(self.printMock, [])

    def test_execute_withCustomKwargs(self):
        fakeCommand = "some fake command to be executed silently"

        status, receivedOutput = services.execute(fakeCommand, beSilent=False, bufsize=0, env={})

        expected = [call(fakeCommand, bufsize=0, universal_newlines=True,
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env={})]
        self.assertCalls(self.pOpen, expected)
        expected = TEST_FAKE_OUTPUT[:-1]
        self.assertEqual(expected, receivedOutput)

    def test_execute_withCommandList(self):
        fakeCommand = "some fake command to passed as a list"

        status, receivedOutput = services.execute(fakeCommand.split(), beSilent=False)

        expected = [call(fakeCommand, bufsize=1, universal_newlines=True,
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT)]
        self.assertCalls(self.pOpen, expected)
        expected = TEST_FAKE_OUTPUT[:-1]
        self.assertEqual(expected, receivedOutput)

    def test_executeForOutput(self):
        expected = "full_example.mak, simple.mak, simplified_example.mak"
        command = 'ls -m *.mak'
        execute = self.patch(CUT, services.execute.__name__, return_value=(0, [expected]))

        received = services.executeForOutput(command, shell=True)

        self.assertEqual(expected, received)
        self.assertCalls(execute, [call(command, beSilent=True, shell=True)])

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