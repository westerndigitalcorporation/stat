from __future__ import print_function

import sys
import os
from shutil import rmtree
from unittest import TestCase
# noinspection PyUnresolvedReferences
from xml.dom.minidom import Text

from services import isWindows

try:
    from unittest.mock import Mock, patch, call, mock_open, PropertyMock  # pylint: disable=no-name-in-module
except ImportError:
    from mock import Mock, patch, call, mock_open, PropertyMock  # pylint: disable=no-name-in-module

import stat_attributes as attributes

BUILTINS_NAME = builtinsModuleName = '__builtin__' if sys.version_info.major < 3 else 'builtins'


def isUnderIde():
    return "PYCHARM_HOSTED" in os.environ or 'VSCODE_PID' in os.environ or \
        os.getenv("SESSIONNAME") == "Console" or os.getenv("TERM_PROGRAM") == "vscode"


def readFileLines(filePath):
    report = open(filePath, 'r')
    lines = report.readlines()
    report.close()
    return lines


def convertXmlToDictionary(xml):
    def recursive_dict(element):
        if isinstance(element, Text):
            return "#text", str(element.data)
        contents = {}
        if element.attributes is not None:
            for name, value in element.attributes.items():
                contents.setdefault(str(name), []).append(str(value))
        children = map(recursive_dict, element.childNodes)
        if children:
            for name, value in children:
                if not isWindows():
                    value = str(value).replace("\\", "/")
                contents.setdefault(str(name), []).append(value)
        return str(element.nodeName), contents
    return dict(map(recursive_dict, xml.childNodes))


class AdvancedTestCase(TestCase):
    __assertSameItems = None

    def skipWindowsTest(self):
        if not isWindows():
            self.skipTest("This test supported in Windows only")

    @staticmethod
    def getModuleName(*args):
        return '.'.join([obj.__name__ for obj in args])

    def patch(self, moduleName, objectName, *args, **kwargs):
        """
        :rtype: MagicMock
        """
        target = '{0}.{1}'.format(moduleName, objectName)
        patcher = patch(target, *args, **kwargs)
        self.addCleanup(patcher.stop)
        return patcher.start()

    def patchMultiple(self, moduleName, objectName, *args, **kwargs):
        """
        :rtype: Dict(str, MagicMock)
        """
        target = '{0}.{1}'.format(moduleName, objectName)
        patcher = patch.multiple(target, *args, **kwargs)
        self.addCleanup(patcher.stop)
        return patcher.start()

    def patchOpen(self, return_value=None, side_effect=None, read_data=''):
        newCallable = mock_open(read_data=read_data) if read_data else mock_open()
        patcher = self.patch(BUILTINS_NAME, 'open', newCallable)
        if return_value:
            patcher.return_value = return_value
        if side_effect:
            patcher.side_effect = side_effect
        return patcher

    def patchBuiltinObject(self, objectName, *args, **kwargs):
        patcher = self.patch(BUILTINS_NAME, objectName, *args, **kwargs)
        return patcher

    def patchWithSpy(self, moduleName, objectName):
        patcher = patch('{0}.{1}'.format(moduleName, objectName), SpyClass.getSpy(objectName, moduleName))
        self.addCleanup(patcher.stop)
        return patcher.start()

    def assertSameItems(self, first, second, msg=None):
        if self.__assertSameItems is None:
            self.__assertSameItems = getattr(self, 'assertCountEqual', getattr(self, 'assertItemsEqual', None))
        self.__assertSameItems(first, second, msg)

    @staticmethod
    def getMockCalls(patchedObject):
        def __isDebuggerCall(callEntry):
            callDescription = tuple(callEntry)[0]
            result = callDescription.find('__str__') + callDescription.find('__eq__')
            return result >= 0
        return [aCall for aCall in patchedObject.mock_calls if not __isDebuggerCall(aCall)]

    def assertCalls(self, patchedObject, expectedCalls, ordered=True):
        receivedCalls = self.getMockCalls(patchedObject)
        if ordered:
            self.assertEqual(expectedCalls, receivedCalls)
        else:
            self.assertSameItems(expectedCalls, receivedCalls)


class FileBasedTestCase(AdvancedTestCase):
    RUN_ROOT = os.getcwd()

    @classmethod
    def setUpClass(cls):
        cls.enterTestsDirectory()
        cls.rmtree(attributes.OUTPUT_DIRECTORY)

    @classmethod
    def tearDownClass(cls):
        for outputDirectory in attributes.ALL_OUTPUT_DIRECTORIES:
            cls.rmtree(outputDirectory)
        os.chdir(cls.RUN_ROOT)

    @staticmethod
    def rmtree(treeRoot):
        if os.path.isdir(treeRoot):
            rmtree(treeRoot)

    @staticmethod
    def enterTestsDirectory():
        testsPath = os.path.dirname(os.path.relpath(__file__))
        if testsPath:
            os.chdir(testsPath)


class SpyArguments(object):
    def __init__(self, *args, **kwargs):
        self.args = args
        self.__kwargs = kwargs

    def __getattr__(self, item):
        return self.__kwargs[item]

    def __setitem__(self, key, value):
        self.__kwargs[key] = value


class SpyClass(object):
    def __new__(cls, classToSpy):
        class TheSpyMetaClass(type):
            def __getattr__(self, attribute):
                def spyCall(*args, **kwargs):
                    return getattr(classToSpy, attribute)(*args, **kwargs)
                if hasattr(getattr(classToSpy, attribute), '__call__'):
                    return spyCall
                else:
                    return getattr(classToSpy, attribute)

        class Instance(object):
            def __init__(self, spiedCalls):
                self.__calls = spiedCalls

            def getArguments(self, method, callId):
                return self.__calls[method][callId]

            def getCallCount(self, method):
                return len(self.__calls[method]) if method in self.__calls else 0

        class TheSpy(object):
            __metaclass__ = TheSpyMetaClass
            instances = []
            mocks = {}

            @classmethod
            def addMock(cls, attribute, mockValue):
                if not cls.__isManagedByMocks(attribute):
                    cls.mocks[attribute] = []
                cls.mocks[attribute].append(mockValue)

            @classmethod
            def __isManagedByMocks(cls, attribute):
                return attribute in cls.mocks and len(cls.mocks[attribute])

            @classmethod
            def __extractMock(cls, attribute):
                mockValue = cls.mocks[attribute][0]
                cls.mocks[attribute].remove(mockValue)
                if hasattr(mockValue, '__call__'):
                    return mockValue()
                else:
                    return mockValue

            def __init__(self, *args, **kwargs):
                self.__calls = {}
                self.__addSpiedCall('__init__', SpyArguments(*args, **kwargs))
                self._spied = classToSpy(*args, **kwargs)
                self.instances.append(Instance(self.__calls))

            def __getattr__(self, attribute):
                def spyCall(*args, **kwargs):
                    self.__addSpiedCall(attribute, SpyArguments(*args, **kwargs))
                    if self.__isManagedByMocks(attribute):
                        return self.__extractMock(attribute)
                    return getattr(self._spied, attribute)(*args, **kwargs)

                if hasattr(getattr(self._spied, attribute), '__call__'):
                    return spyCall
                elif self.__isManagedByMocks(attribute):
                    return self.__extractMock(attribute)
                else:
                    return getattr(self._spied, attribute)

            def __addSpiedCall(self, methodName, arguments):
                if methodName not in self.instances:
                    self.__calls[methodName] = []
                self.__calls[methodName].append(arguments)

        return TheSpy

    @staticmethod
    def getSpy(className, inScript):
        substituted = getattr(sys.modules[inScript], className)
        return SpyClass(substituted)


class SpyModule(object):
    def __init__(self, moduleToSpy=None, scriptToSubstituteModuleIn=None):
        self.__moduleToSpy = moduleToSpy
        self.__originalSubstitutedModule = sys.modules[moduleToSpy] if moduleToSpy is not None else None
        self.__scriptToSubstituteModuleIn = scriptToSubstituteModuleIn
        if scriptToSubstituteModuleIn is not None and moduleToSpy is not None:
            setattr(sys.modules[scriptToSubstituteModuleIn], moduleToSpy, self)
        self.__callMocks = {}
        self.__callsHistory = {}

    def addMockForFunction(self, functionName, returnMockValue):
        if functionName not in self.__callMocks:
            self.__callMocks[functionName] = []
        self.__callMocks[functionName].append(returnMockValue)

    def __getitem__(self, functionName):
        if functionName not in self.__callsHistory:
            self.__callsHistory[functionName] = []
        return self.__callsHistory[functionName]

    def __getattr__(self, functionName):
        def spyHandler(*args, **kwargs):
            self[functionName].append(SpyArguments(*args, **kwargs))
            if functionName in self.__callMocks:
                return self._extractMockReturnValue(functionName)
            else:
                return self.__issueActualFunctionCall(functionName, *args, **kwargs)
        return spyHandler

    def _substituteFunctionCall(self, functionName, arguments=SpyArguments()):
        self[functionName].append(arguments)
        if functionName in self.__callMocks:
            return self._extractMockReturnValue(functionName)
        else:
            return None

    def _extractMockReturnValue(self, functionName):
        if len(self.__callMocks[functionName]) == 0:
            raise TestingToolsException("To many calls to the function '{0}' of the spied module '{1}'".format(
                functionName, self.__originalSubstitutedModule))
        mock = self.__callMocks[functionName][0]
        self.__callMocks[functionName] = self.__callMocks[functionName][1:]
        return mock

    def __issueActualFunctionCall(self, functionName, *args, **kwargs):
        if self.__originalSubstitutedModule is not None and self.__moduleToSpy is not None:
            return getattr(self.__originalSubstitutedModule, functionName)(*args, **kwargs)

    def restoreOriginalModule(self):
        if self.__scriptToSubstituteModuleIn is not None:
            setattr(sys.modules[self.__scriptToSubstituteModuleIn],
                    self.__moduleToSpy,
                    self.__originalSubstitutedModule)


class FakeOs(SpyModule):
    class FakePath(SpyModule):
        def __init__(self):
            SpyModule.__init__(self, 'os.path')

    def __init__(self, scriptToSubstituteModuleIn=None):
        SpyModule.__init__(self, 'os', scriptToSubstituteModuleIn)
        self.path = self.FakePath()

    def symlink(self, source, target):
        self['symlink'].append(SpyArguments(source=source, target=target))


class FakeSubprocess(SpyModule):
    __MAX_SUPPORTED_PROCESS = 5

    PIPE = 'PIPE'
    STDOUT = 'STDOUT'

    class FakeProcess(SpyModule):
        def __init__(self):
            SpyModule.__init__(self)
            self.stdout = SpyModule()

        def wait(self):
            return self._substituteFunctionCall('wait')

    def __init__(self, scriptToSubstituteModuleIn=None):
        SpyModule.__init__(self, 'subprocess', scriptToSubstituteModuleIn)
        self.processes = [self.FakeProcess() for _dummyIndex in range(self.__MAX_SUPPORTED_PROCESS)]

    def Popen(self, *args, **kwargs):
        self['Popen'].append(SpyArguments(*args, **kwargs))
        callIndex = len(self['Popen']) - 1
        return self.processes[callIndex]


class TestingToolsException(Exception):
    """
    Custom exception for STAT mak-file parser
    """


if __name__ == '__main__':
    spy = SpyModule('os')
    cwd = spy.getcwd()
    print(cwd)
    print(spy['getcwd'])
    spy = SpyModule('os.path')
    print(spy.splitext('example.exe'))
