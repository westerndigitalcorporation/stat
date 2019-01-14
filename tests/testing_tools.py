import sys
import os
from unittest import TestCase
from services import isWindows

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

try:
    from unittest.mock import patch, call, mock_open
except ImportError:
    from mock import patch, call, mock_open


def readFileLines(filePath):
    report = open(filePath, 'r')
    lines = report.readlines()
    report.close()
    return lines

class AdvancedTestCase(TestCase):
    __assertSameItems = None

    def skipWindowsTest(self):
        if not isWindows():
            self.skipTest("This test supported in Windows only")

    def patch(self, moduleName, objectName, *args, **kwargs):
        patcher = patch('{0}.{1}'.format(moduleName, objectName), *args, **kwargs)
        self.addCleanup(patcher.stop)
        return patcher.start()

    def patchOpen(self):
        builtinsModuleName = '__builtin__' if sys.version_info.major < 3 else 'builtins'
        return self.patch(builtinsModuleName, 'open', new_callable=mock_open())

    def patchWithSpy(self, moduleName, objectName):
        patcher = patch('{0}.{1}'.format(moduleName, objectName), SpyClass.getSpy(objectName, moduleName))
        self.addCleanup(patcher.stop)
        return patcher.start()

    def assertSameItems(self, first, second, msg=None):
        if self.__assertSameItems is None:
            self.__assertSameItems = getattr(self, 'assertCountEqual', getattr(self, 'assertItemsEqual', None))
        self.__assertSameItems(first, second, msg)

    def assertCalls(self, patchedObject, expectedCalls):
        def __isDebuggerCall(callEntry):
            callDescription = tuple(callEntry)[0]
            result = callDescription.find('__str__')
            return result >= 0
        receivedCalls = [aCall for aCall in patchedObject.mock_calls if not __isDebuggerCall(aCall)]
        self.assertEqual(expectedCalls, receivedCalls)

class FileBasedTestCase(AdvancedTestCase):
    __cwd = None
    __TEST_PATH = "./files"

    @classmethod
    def setUpClass(cls):
        cls.__cwd = os.getcwd()
        os.chdir(cls.__TEST_PATH)

    @classmethod
    def tearDownClass(cls):
        os.chdir(cls.__cwd)

class StdOutputSubstitution(object):
    def __init__(self):
        self.output = StringIO()
        self.__stdOut = sys.stdout
        self.__stdErr = sys.stderr
        sys.stdout = self.output
        sys.stderr = self.output

    def __del__(self):
        if self.__stdOut is not None:
            self.restoreStdOutputs()
        self.output.close()

    def restoreStdOutputs(self):
        sys.stdout = self.__stdOut
        sys.stderr = self.__stdErr
        self.__stdOut = None
        self.__stdErr = None

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
    def __init__(self, moduleToSpy = None, scriptToSubstituteModuleIn = None):
        self.__moduleToSpy = moduleToSpy
        self.__originalSubstitutedModule = sys.modules[moduleToSpy] if not moduleToSpy is None else None
        self.__scriptToSubstituteModuleIn = scriptToSubstituteModuleIn
        if not scriptToSubstituteModuleIn is None and not moduleToSpy is None:
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

    def _substituteFunctionCall(self, functionName, arguments = SpyArguments()):
        self[functionName].append(arguments)
        if functionName in self.__callMocks:
            return self._extractMockReturnValue(functionName)
        else:
            return None

    def _extractMockReturnValue(self, functionName):
        if len(self.__callMocks[functionName]) == 0:
            raise TestingToolsException("To many calls to the function '{0}' of the spied module '{1}'".format(functionName, self.__originalSubstitutedModule))
        mock = self.__callMocks[functionName][0]
        self.__callMocks[functionName] = self.__callMocks[functionName][1:]
        return mock

    def __issueActualFunctionCall(self, functionName, *args, **kwargs):
        if not self.__originalSubstitutedModule is None and not self.__moduleToSpy is None:
            return getattr(self.__originalSubstitutedModule, functionName)(*args, **kwargs)

    def restoreOriginalModule(self):
        if self.__scriptToSubstituteModuleIn is not None:
            setattr(sys.modules[self.__scriptToSubstituteModuleIn], self.__moduleToSpy, self.__originalSubstitutedModule)


class FakeOs(SpyModule):
    class FakePath(SpyModule):
        def __init__(self):
            SpyModule.__init__(self, 'os.path')

    def __init__(self, scriptToSubstituteModuleIn = None):
        SpyModule.__init__(self, 'os', scriptToSubstituteModuleIn)
        self.path = self.FakePath()

    def symlink(self, source, target):
        self['symlink'].append(SpyArguments(source = source, target = target))

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

    def __init__(self, scriptToSubstituteModuleIn = None):
        SpyModule.__init__(self, 'subprocess', scriptToSubstituteModuleIn)
        self.processes = [self.FakeProcess() for index in range(self.__MAX_SUPPORTED_PROCESS)]

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
