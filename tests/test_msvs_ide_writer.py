import os
import re
# noinspection PyUnresolvedReferences
from xml.dom.minidom import parseString as parseXmlString
from xml.sax.saxutils import escape

import stat_attributes as attributes
from build_tools_crawler import BuildToolsCrawler
from msvs_tools import MsvsTools
from ide_writer import IdeXmlWriter
from msvs_ide_writer import MsvsSolutionWriter, MsvsLegacyWriter, MsvsWriter, Msvs2010ProjectWriter
from services import locateResource, readTextFileAtOnce, toNativePath, isWindows, formatMakeCommand
from stat_makefile_project import StatMakefileProject
from tests.testing_tools import convertXmlToDictionary, FileBasedTestCase, Mock, PropertyMock, call


CUT = MsvsSolutionWriter.__module__

TEST_PROJECT_GUID = 'Project GUID'
TEST_MAKEFILE = 'simplified_example.mak'
TEST_PROJECT_NAME = TEST_MAKEFILE[:-4]
TEST_PROJECT_FILE_PATH = '/root/projects/project/file.project'
TEMPLATE_IMITATION = "format={format},version={version},year={year},name={name},project={project_file},guid={guid}"
TEST_SOLUTION_FORMAT = 11.0
TEST_VERSION = 15
TEST_YEAR = 2013
TEST_TOOL_PATH = '/root/tools/'
TEST_DEV_BATCH_FILE = '/root/tools/common/dev.bat'
TEST_MAKE_COMMAND = '/root/tools/bin/make.exe'
TEST_VCPROJ_TEMPLATE_FILE = './extra/template.vcproj'
TEST_VCXPROJ_TEMPLATE_FILE = './extra/template.vcxproj'


class MsvsWriterTestCase(FileBasedTestCase):

    def mockCommonObjects(self):
        self.tools = Mock(spec=MsvsTools)
        self.year = PropertyMock(return_value=TEST_YEAR)
        type(self.tools).path = PropertyMock(return_value=TEST_TOOL_PATH)
        type(self.tools).devBatchFile = PropertyMock(return_value=TEST_DEV_BATCH_FILE)
        type(self.tools).nmakeFilePath = PropertyMock(return_value='wrong_path')
        type(self.tools).versionId = PropertyMock(return_value=TEST_VERSION)
        type(self.tools).year = self.year
        type(self.tools).solutionFormat = PropertyMock(return_value=TEST_SOLUTION_FORMAT)
        self.makefileProject = StatMakefileProject(TEST_MAKEFILE)

    def formatCommandLine(self, target):
        command = formatMakeCommand(TEST_MAKEFILE, [target], STAT_NAMESPACE='ide_' + self.makefileProject.name)
        return escape("cd..&&" + " ".join(command), {'"': '&quot;', "'": "&apos;"})


class TestMsvsWriter(MsvsWriterTestCase):

    def setUp(self):
        self.mockCommonObjects()
        toolsCrawler = self.patch(CUT, BuildToolsCrawler.__name__)
        toolsCrawler.return_value.retrieveMsvs.return_value = self.tools
        self.msvsLegacyWriter = self.patch(CUT, MsvsLegacyWriter.__name__)
        self.msvs2010ProjectWriter = self.patch(CUT, Msvs2010ProjectWriter.__name__)

    def test_factory_uponLegacyToolsVersion(self):
        self.year.return_value = 2008
        writer = MsvsWriter(self.makefileProject)
        self.assertEqual(0, len(writer.writers))
        self.assertCalls(self.msvsLegacyWriter, [call(self.makefileProject, self.tools)])

    def test_factory_uponNewerToolsVersion(self):
        writer = MsvsWriter(self.makefileProject)
        self.assertEqual(0, len(writer.writers))
        self.assertCalls(self.msvs2010ProjectWriter, [call(self.makefileProject, self.tools)])


class TestMsvsSolutionWriter(MsvsWriterTestCase):
    def setUp(self):
        self.mockCommonObjects()
        self.osOpen = self.patchOpen(read_data=TEMPLATE_IMITATION)

        self.writer = MsvsSolutionWriter(self.makefileProject, self.tools, TEST_PROJECT_GUID, TEST_PROJECT_FILE_PATH)

    def test_write(self):
        self.writer.write()

        templatePath = locateResource(self.writer._TEMPLATE_FILENAME)
        solutionFilename = "./{0}/{1}".format(attributes.IDE_DIRECTORY,
                                              self.writer._SOLUTION_FILENAME.format(name=TEST_PROJECT_NAME))
        solutionContents = TEMPLATE_IMITATION.format(
            format=TEST_SOLUTION_FORMAT, version=TEST_VERSION, year=TEST_YEAR, name=TEST_PROJECT_NAME,
            project_file=TEST_PROJECT_FILE_PATH, guid=TEST_PROJECT_GUID
        )
        expected = [
            call(templatePath), call().read(), call().close(),
            call(solutionFilename, 'w'), call().write(solutionContents), call().flush(), call().close(),
        ]
        self.assertCalls(self.osOpen, expected)


class TestMsvsLegacyWriter(MsvsWriterTestCase):

    @classmethod
    def setUpClass(cls):
        MsvsWriterTestCase.setUpClass()
        cls.PROJECT_TEMPLATE = re.sub(r">[\s\n\r]+<", '><', readTextFileAtOnce(TEST_VCPROJ_TEMPLATE_FILE))
        if not isWindows():
            cls.PROJECT_TEMPLATE = cls.PROJECT_TEMPLATE.replace("\\", "/")

    def setUp(self):
        self.mockCommonObjects()
        self.msvsSolutionWriter = self.patch(CUT, MsvsSolutionWriter.__name__, autospec=True)
        self.ideXmlWriter_write = self.patch(CUT, '{0}.{1}'.format(IdeXmlWriter.__name__, IdeXmlWriter.write.__name__))

        self.writer = MsvsLegacyWriter(self.makefileProject, self.tools)

    def test_init(self):
        actual = convertXmlToDictionary(self.writer._doc)
        target = 'ide_' + self.makefileProject.name
        output = os.path.join('..', attributes.OUTPUT_DIRECTORY, self.makefileProject.outputName, target)
        expected = convertXmlToDictionary(
            parseXmlString(self.PROJECT_TEMPLATE.format(
                version=TEST_VERSION, name=self.makefileProject.name, guid=self.writer._PROJECT_GUID, output=output,
                build=self.formatCommandLine("build"),
                rebuild=self.formatCommandLine("rebuild"),
                clean=self.formatCommandLine("clean"),
                executable="{0}.exe".format(self.makefileProject.outputName),
                definitions=";".join(self.makefileProject.definitions)
            )))
        self.assertSameItems(expected, actual)

    def test_createRootToken(self):
        writer = self.writer

        rootToken = writer.createRootToken()
        expected, = writer._doc.getElementsByTagName("Files")
        self.assertEqual(expected, rootToken)

    def test_createDirectoryToken(self):
        writer = self.writer
        name = "stat_directory"
        rootToken = writer.createRootToken()

        directoryToken = writer.createDirectoryToken(name, rootToken)

        self.assertIn(directoryToken, rootToken.childNodes)
        self.assertEqual("Filter", directoryToken.nodeName)
        self.assertEqual(name, directoryToken.getAttribute("Name"))

        self.assertEqual(directoryToken, writer.createDirectoryToken(name, rootToken))

    def test_addFile(self):
        fileInRoot = 'root_file.c'
        otherFile = 'some/other/another/other_file.c'
        writer = self.writer
        rootToken = writer.createRootToken()
        otherDirectory = writer.createDirectoryToken("other_directory", rootToken)

        writer.addFile(fileInRoot, rootToken)
        files = list(self.__getElements("File", RelativePath=os.path.join("..", fileInRoot)))
        self.assertEqual(1, len(files))
        self.assertIn(files[0], rootToken.childNodes)

        writer.addFile(otherFile, otherDirectory)
        files = list(self.__getElements("File", RelativePath=toNativePath(os.path.join("..", otherFile))))
        self.assertEqual(1, len(files))
        self.assertIn(files[0], otherDirectory.childNodes)

    def test_write(self):
        writer = self.writer

        writer.write()

        self.assertCalls(self.ideXmlWriter_write, [call()])
        expected = [call(self.makefileProject, self.tools, MsvsLegacyWriter._PROJECT_GUID,
                         "vs_" + self.makefileProject.name + ".vcproj"), call().write()]
        self.assertCalls(self.msvsSolutionWriter, expected)

    def __getElements(self, tagName, **xmlAttributes):
        tags = self.writer._doc.getElementsByTagName(tagName)
        for tag in tags:
            for attribute, value in xmlAttributes.items():
                if not tag.getAttribute(attribute) == value:
                    break
            else:
                yield tag


class TestMsvs2010ProjectWriter(MsvsWriterTestCase):

    @classmethod
    def setUpClass(cls):
        MsvsWriterTestCase.setUpClass()
        cls.PROJECT_TEMPLATE = re.sub(r">[\s\n\r]+<", '><', readTextFileAtOnce(TEST_VCXPROJ_TEMPLATE_FILE))

    def setUp(self):
        self.mockCommonObjects()
        self.msvsSolutionWriter = self.patch(CUT, MsvsSolutionWriter.__name__, autospec=True)
        self.ideXmlWriter_write = self.patch(CUT, '{0}.{1}'.format(IdeXmlWriter.__name__, IdeXmlWriter.write.__name__))

        self.writer = Msvs2010ProjectWriter(self.makefileProject, self.tools)

    def test_init(self):
        self.maxDiff = None
        actual = convertXmlToDictionary(self.writer._doc)
        target = 'ide_' + self.makefileProject.name
        output = os.path.join('..', attributes.OUTPUT_DIRECTORY, self.makefileProject.outputName, target)
        expected = convertXmlToDictionary(parseXmlString(self.PROJECT_TEMPLATE.format(
            version=TEST_VERSION, name=self.makefileProject.name, guid=self.writer._PROJECT_GUID, output=output,
            build=self.formatCommandLine("build"),
            rebuild=self.formatCommandLine("rebuild"),
            clean=self.formatCommandLine("clean"),
            executable="{0}.exe".format(self.makefileProject.outputName),
            definitions=";".join(self.makefileProject.definitions)
        )))
        self.assertSameItems(expected, actual)

    def test_addFile_forSourceFiles(self):
        sources = ['./root_main.c', './sub_directory/file_a.c', './sub_directory/file_b.c']

        for source in sources:
            self.writer.addFile(source, None)

        tags = self.writer._doc.getElementsByTagName("ClCompile")
        received = [tag.getAttribute("Include") for tag in tags]
        expected = [os.path.join("..", source) for source in sources]
        self.assertSameItems(expected, received)

    def test_addFile_forHeaderFiles(self):
        sources = ['./main_api.h', './sub_directory/inc/header_a.h', './inc/sub_api.h']

        for source in sources:
            self.writer.addFile(source, None)

        tags = self.writer._doc.getElementsByTagName("ClInclude")
        received = [tag.getAttribute("Include") for tag in tags]
        expected = [os.path.join("..", source) for source in sources]
        self.assertSameItems(expected, received)

    def test_write(self):
        writer = self.writer

        writer.write()

        self.assertCalls(self.ideXmlWriter_write, [call()])
        expected = [call(self.makefileProject, self.tools, MsvsLegacyWriter._PROJECT_GUID,
                         "vs_" + self.makefileProject.name + ".vcxproj"), call().write()]
        self.assertCalls(self.msvsSolutionWriter, expected)
