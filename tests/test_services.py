#!/usr/bin/env python
from shutil import copyfile, rmtree

from testing_tools import *
import services

CUT = 'services'

class TestServices(FileBasedTestCase):
    OUTPUT_DIRECTORY = services.config.OUTPUT_DIRECTORY

    def setUp(self):
        self._fakeOs = FakeOs('services')
        if os.path.isdir(self.OUTPUT_DIRECTORY):
            rmtree(self.OUTPUT_DIRECTORY, ignore_errors=True)

    def tearDown(self):
        self._fakeOs.restoreOriginalModule()
        if os.path.isdir(self.OUTPUT_DIRECTORY):
            rmtree(self.OUTPUT_DIRECTORY, ignore_errors=True)

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

    def test_execute(self):
        patcher = self.patch(CUT, 'subprocess')
        fakeExecutable = "/home/bin/executable.exe"
        services.execute(fakeExecutable)
        self.assertCalls(patcher,
                         [call.Popen('/home/bin/executable.exe', stdout=patcher.PIPE, shell=True),call.Popen().wait()])

    def test_executeForOutput(self):
        expected = "full_example.mak, simple.mak, simplified_example.mak"
        received = services.executeForOutput(['ls', '-m', '*.mak'])
        self.assertEqual(expected, received)

    def test_createLinkOnLinux(self):
        patcher = self.patch(CUT, 'subprocess')
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
        patcher = self.patch(CUT, 'subprocess')
        self.patch(CUT, 'platform.system', return_value='Windows')

        source = "/home/product/fw/inc/example.h"
        target = "/home/tests/fw/inc/example.h"
        services.createLink(source, target)

        commandLine = 'cmd /c mklink "{target}" "{source}"'.format(target = services.toWindowsPath(target),
            source = services.toWindowsPath("../../../product/fw/inc/example.h"))
        self.assertCalls(patcher, [call.Popen(commandLine, stdout=patcher.PIPE, shell=True),call.Popen().wait()])
        self.assertEqual(0, len(self._fakeOs['symlink']))

    def test_createLinkOnWindowsForDirectory(self):
        patcher = self.patch(CUT, 'subprocess')
        self.patch(CUT, 'platform.system', return_value='Windows')
        self._fakeOs.path.addMockForFunction('isdir', True)

        source = "/home/product/fw/inc"
        target = "/home/tests/fw/inc"
        services.createLink(source, target)

        self.assertEqual(0, len(self._fakeOs['symlink']))
        commandLine = 'cmd /c mklink /D "{target}" "{source}"'.format(target = services.toWindowsPath(target),
            source = services.toWindowsPath("../../product/fw/inc"))
        self.assertCalls(patcher, [call.Popen(commandLine, stdout=patcher.PIPE, shell=True), call.Popen().wait()])

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

        pathName = './' + services.StatConfiguration.PRODUCT_DIRECTORY
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

    def test_vsTools(self):
        self.assertEqual(services.VsTools(), services.vsTools)

    def test_config(self):
        self.assertEqual(services.StatConfiguration(), services.config)

    def test_remove(self):
        self._emulateNonEmptyFileTree()
        services.remove(self.OUTPUT_DIRECTORY)
        self.assertFalse(os.path.isdir(self.OUTPUT_DIRECTORY))

    def test_removeUponAntiVirusLockups(self):
        retries = 3
        rmTreePatcher = self._patchRmtree(retries=retries)
        osRemovePatcher = self._patchOsRemove(retries=retries)

        self._emulateNonEmptyFileTree()

        stdOutput = StdOutputSubstitution()
        services.remove(self.OUTPUT_DIRECTORY)
        stdOutput.restoreStdOutputs()

        self.assertFalse(osRemovePatcher.called)
        self.assertEqual([call(self.OUTPUT_DIRECTORY)] * (retries + 1), rmTreePatcher.call_args_list)

    def test_removeFile(self):
        retries = 2
        fileName = 'full_example.mak'
        filePath = os.path.join(self.OUTPUT_DIRECTORY, fileName)
        os.makedirs(self.OUTPUT_DIRECTORY)
        copyfile('full_example.mak', filePath)
        rmTreePatcher = self._patchRmtree(retries=retries)
        osRemovePatcher = self._patchOsRemove(retries=retries)

        stdOutput = StdOutputSubstitution()
        services.remove(filePath)
        stdOutput.restoreStdOutputs()

        self.assertFalse(rmTreePatcher.called)
        self.assertEqual([call(filePath)] * (retries + 1), osRemovePatcher.call_args_list)


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

    def _emulateNonEmptyFileTree(self):
        def listByFileExtension(directory, extension):
            return (fileName for fileName in os.listdir(directory) if
                    os.path.isfile(fileName) and os.path.splitext(fileName)[1] == extension)
        def constructSubFolder(name):
            return os.path.join(self.OUTPUT_DIRECTORY, name)

        os.makedirs(self.OUTPUT_DIRECTORY)
        for filename in listByFileExtension(directory='.', extension='.h'):
            copyfile(filename, os.path.join(self.OUTPUT_DIRECTORY, filename))

        for filename in listByFileExtension(directory='.', extension='.c'):
            copyfile(filename, os.path.join(self.OUTPUT_DIRECTORY, filename.replace('.c', '.obj')))


