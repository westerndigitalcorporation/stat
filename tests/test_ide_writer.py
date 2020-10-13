# noinspection PyUnresolvedReferences
from xml.dom.minidom import Element, Document

import stat_attributes as attributes
from ide_writer import IdeWriter, IdeCompositeWriter, IdeXmlWriter, IdeWorkspaceWriter
from services import toNativePath
from stat_makefile_project import StatMakefileProject
from tests.testing_tools import AdvancedTestCase, FileBasedTestCase, Mock, call

CUT = IdeWriter.__module__
TEST_MAKEFILE = 'simplified_example.mak'


class IdeWriterTestExampleA(IdeWriter):
    IDE = 'exampleA'


class IdeWriterTestExampleB(IdeWriterTestExampleA):
    IDE = 'exampleB'


class IdeWriterTestExampleC(IdeWriterTestExampleA):
    IDE = None


class TestIdeWriter(AdvancedTestCase):

    def setUp(self):
        self.contents = Mock(spec=StatMakefileProject)

    def test_factory(self):
        instanceA = IdeWriter.create(IdeWriterTestExampleA.IDE, self.contents)
        instanceB = IdeWriter.create(IdeWriterTestExampleB.IDE, self.contents)
        instanceC = IdeWriter.create(IdeWriterTestExampleC.IDE, self.contents)

        self.assertIsInstance(instanceA, IdeWriterTestExampleA)
        self.assertIsInstance(instanceB, IdeWriterTestExampleB)
        self.assertIsInstance(instanceC, IdeWriter)


class TestIdeCompositeWriter(AdvancedTestCase):

    def setUp(self):
        self.contents = Mock()
        self.writerA = Mock(spec=IdeWriter)
        self.writerB = Mock(spec=IdeWriter)

        class IdeCompositeWriterTestClass(IdeCompositeWriter):
            writers = [self.writerA, self.writerB]

        self.writer = IdeCompositeWriterTestClass(self.contents)

    def test_init(self):
        self.assertCalls(self.writerA, [call(self.contents, ())])
        self.assertCalls(self.writerB, [call(self.contents, ())])

    def test_create_root_token(self):
        self.writerA.return_value.createRootToken.return_value = 'TOKEN-A'
        self.writerB.return_value.createRootToken.return_value = 'TOKEN-B'

        tokens = self.writer.createRootToken()
        self.assertEqual(['TOKEN-A', 'TOKEN-B'], tokens)
        for writer in self.writer.writers:
            self.assertCalls(writer, [call(self.contents, ()), call().createRootToken()])

    def test_create_directory_token(self):
        parentTokens = ['PARENT-TOKEN-A', 'PARENT-TOKEN-B']
        self.writerA.return_value.createDirectoryToken.return_value = 'DIR-TOKEN-A'
        self.writerB.return_value.createDirectoryToken.return_value = 'DIR-TOKEN-B'

        tokens = self.writer.createDirectoryToken('directory', parentTokens)
        self.assertEqual(['DIR-TOKEN-A', 'DIR-TOKEN-B'], tokens)
        for writer, parent in zip(self.writer.writers, parentTokens):
            self.assertCalls(writer, [call(self.contents, ()), call().createDirectoryToken('directory', parent)])

    def test_add_file(self):
        parentTokens = ['PARENT-TOKEN-A', 'PARENT-TOKEN-B']

        self.writer.addFile('file-path', parentTokens)
        for writer, parent in zip(self.writer.writers, parentTokens):
            self.assertCalls(writer, [call(self.contents, ()), call().addFile('file-path', parent)])

    def test_write(self):
        self.writer.write()
        for writer in self.writer.writers:
            self.assertCalls(writer, [call(self.contents, ()), call().write()])


class TestIdeXmlWriter(AdvancedTestCase):

    def setUp(self):
        self.mdomDocument = self.patch(CUT, Document.__name__)
        self.contents = Mock(spec=StatMakefileProject)

        self.writer = IdeXmlWriter(self.contents)

    def test_init(self):
        self.assertEqual(self.contents, self.writer._contents)
        self.assertEqual(None, self.writer._filename)
        self.assertCalls(self.mdomDocument, [call()])

    def test_composeElement(self):
        elementMock = Mock(spec=Element)
        self.mdomDocument.return_value.createElement.return_value = elementMock
        elementAttributes = {'first': 1111, 'second': 2222, 'another': 'some text', 'boolean': True}

        element = self.writer.composeElement("nameOfElement", **elementAttributes)
        self.assertEqual(elementMock, element)
        self.mdomDocument.assert_has_calls([call(), call().createElement("nameOfElement")])
        expected = [call.setAttribute(attribute, value) for attribute, value in elementAttributes.items()]
        self.assertCalls(elementMock, expected, ordered=False)

    def test_composeElement_withContextValue(self):
        elementMock = Mock(spec=Element)
        self.mdomDocument.return_value.createElement.return_value = elementMock
        self.mdomDocument.return_value.createTextNode.side_effect = lambda x: "value is {0}".format(x)
        elementAttributes = {'first-attribute': 101010, 'second-one': 'some text'}

        element = self.writer.composeElement("nameOfElement", context=17, **elementAttributes)
        self.assertEqual(elementMock, element)
        self.mdomDocument.assert_has_calls([call(), call().createElement("nameOfElement")])
        expected = [call.appendChild("value is {0}".format(17))]
        expected.extend([call.setAttribute(attribute, elementAttributes[attribute]) for attribute in elementAttributes])
        self.assertCalls(elementMock, expected, ordered=False)

    def test_composeElement_withContextOfElements(self):
        elements = [Mock(spec=Element) for _dummy in range(4)]
        self.mdomDocument.return_value.createElement.side_effect = elements
        self.mdomDocument.return_value.createTextNode.side_effect = lambda x: "value is {0}".format(x)
        elementAttributes = {'the-attribute': 'the attribute value', 'another-one': 'the text of the another one'}
        contextElements = {'elementA': 'the A text', 'elementB': 57, 'elementC': 'the C text'}

        element = self.writer.composeElement("nameOfElement", context=contextElements, **elementAttributes)

        self.assertEqual(elements[0], element)
        expected = [call(), call().createElement("nameOfElement")]
        expected.extend([call().createElement(name) for name in contextElements])
        self.mdomDocument.assert_has_calls(expected, any_order=True)

        expected = [call.setAttribute(attribute, elementAttributes[attribute]) for attribute in elementAttributes]
        expected.extend([call.appendChild(child) for child in elements[1:]])
        self.assertCalls(element, expected, ordered=False)

        for element, contents in zip(elements[1:], contextElements):
            expected = [call.appendChild("value is {0}".format(contextElements[contents]))]
            self.assertCalls(element, expected, ordered=False)

    def test_write(self):
        FILENAME_MOCK = 'example_filename.ext'
        self.writer._filename = FILENAME_MOCK
        self.osOpen = self.patchOpen()

        self.writer.write()
        expected = [call(self.__getTargetPath(FILENAME_MOCK), 'w'), call().flush(), call().close()]
        self.assertCalls(self.osOpen, expected)
        expected = [call(), call(self.osOpen.return_value, indent="", addindent="\t", newl="\n", encoding="utf-8")]
        self.assertCalls(self.mdomDocument, expected)

    @staticmethod
    def __getTargetPath(filename):
        return "./{0}/{1}".format(attributes.IDE_DIRECTORY, filename)


ROOT_TOKEN = 'root-token'
TEST_IDE_NAME = 'Test-IDE'
TEST_IDE_OUTPUT = 'Output:'


class IdeTestWriter(IdeWriter):

    def __init__(self, ide, contents):
        super(IdeTestWriter, self).__init__(contents)
        self.tokens = []
        self.files = []
        self.output = ''

    def createRootToken(self):
        return ROOT_TOKEN

    def createDirectoryToken(self, name, parentDirectoryToken):
        token = '>'.join([parentDirectoryToken, name])
        self.tokens.append(token)
        return token

    def addFile(self, filePath, parentDirectoryToken):
        self.files.append('{0} -[{1}]'.format(filePath, parentDirectoryToken))

    def write(self):
        self.output = TEST_IDE_OUTPUT + str(self.tokens)


class TestIdeWorkspaceWriter(FileBasedTestCase):

    def setUp(self):
        self.contents = StatMakefileProject(TEST_MAKEFILE)
        self.testWriter = IdeTestWriter('TEST', self.contents)
        self.statMakefileProject = self.patch(CUT, StatMakefileProject.__name__, autospec=True,
                                              return_value=self.contents)
        self.ideWriterCreate = self.patch(CUT, 'IdeWriter.create', return_value=self.testWriter)
        self.mkdir = self.patch(CUT, 'mkdir')

        self.writer = IdeWorkspaceWriter(TEST_IDE_NAME, TEST_MAKEFILE)

    def test_init(self):
        self.assertCalls(self.statMakefileProject, [call(TEST_MAKEFILE)])
        self.assertCalls(self.ideWriterCreate, [call(TEST_IDE_NAME, self.contents)])

    def test_write(self):
        self.writer.write()

        self.assertCalls(self.mkdir, [call(attributes.IDE_DIRECTORY, exist_ok=True)])
        tokens, files = self.__getTreeItems(self.contents.tree, ROOT_TOKEN)
        self.assertSameItems(tokens, self.testWriter.tokens)
        self.assertSameItems(files, self.testWriter.files)
        self.assertEqual(TEST_IDE_OUTPUT + str(tokens), self.testWriter.output)

    def __getTreeItems(self, tree, parentToken):
        """
        :type tree: DirectoryTreeNode
        """
        tokens = []
        files = ['{0} -[{1}]'.format(toNativePath(tree[aFile]), parentToken) for aFile in tree.files]
        for directory in tree.dirs:
            token = '>'.join([parentToken, directory])
            tokens.append(token)
            childDirectories, childFiles = self.__getTreeItems(tree[directory], token)
            tokens.extend(childDirectories)
            files.extend(childFiles)
        return tokens, files
