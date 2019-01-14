import os
import re
from xml.dom.minidom import parseString as parseXmlString
from mock import Mock, PropertyMock, call

import stat_attributes as attributes
from ide_writer import IdeXmlWriter
from msvs_ide_writer import MsvsSolutionWriter, MsvsLegacyWriter, MsvsWriter
from services import locateResource, readTextFileAtOnce, toNativePath
from stat_configuration import StatConfiguration
from stat_makefile_project import StatMakefileProject
from testing_tools import AdvancedTestCase
from vs_tools import MsvsTools

CUT = MsvsSolutionWriter.__module__

TEST_PROJECT_GUID = 'Project GUID'
TEST_MAKEFILE = 'simplified_example.mak'
TEST_PROJECT_NAME = TEST_MAKEFILE[:-4]
TEST_PROJECT_FILE_PATH = '/root/projects/project/file.project'
TEMPLATE_IMITATION = "format={format},version={version},year={year},name={name},project={project_file},guid={guid}"
TEST_SOLUTION_FORMAT = 11.0
TEST_VERSION = 117
TEST_YEAR = 2037
TEST_TOOL_PATH = '/root/tools/'
TEST_DEV_BATCH_FILE = '/root/tools/common/dev.bat'
TEST_NMAKE_FILE = '/root/tools/bin/nmake.exe'
TEST_VCPROJ_TEMPLATE_FILE = './extra/template.vcproj'


class MsvsWriterTestCase(AdvancedTestCase):

    def mockCommonObjects(self):
        self.tools = Mock(spec=MsvsTools)
        type(self.tools).path = PropertyMock(return_value=TEST_TOOL_PATH)
        type(self.tools).devBatchFile = PropertyMock(return_value=TEST_DEV_BATCH_FILE)
        type(self.tools).nmakeFilePath = PropertyMock(return_value=TEST_NMAKE_FILE)
        type(self.tools).versionId = PropertyMock(return_value=TEST_VERSION)
        type(self.tools).year = PropertyMock(return_value=TEST_YEAR)
        type(self.tools).solutionFormat = PropertyMock(return_value=TEST_SOLUTION_FORMAT)
        self.makefileProject = StatMakefileProject(TEST_MAKEFILE)

class TestMsvsWriter(MsvsWriterTestCase):

    def setUp(self):
        self.mockCommonObjects()
        getMsvsTools = '.'.join([StatConfiguration.__name__, StatConfiguration.getMsvsTools.__name__])
        self.getMsvsTools = self.patch(CUT, getMsvsTools, return_value=self.tools)
        self.msvsLegacyWriter = self.patch(CUT, MsvsLegacyWriter.__name__)

    def test_factory(self):
        writer = MsvsWriter(MsvsWriter.IDE, self.makefileProject)
        self.assertEqual(0, len(writer.writers))
        self.assertCalls(self.msvsLegacyWriter, [call(MsvsWriter.IDE, self.makefileProject, self.tools)])


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
        cls.PROJECT_TEMPLATE = re.sub(r">[\s\n\r]+<", '><', readTextFileAtOnce(TEST_VCPROJ_TEMPLATE_FILE))

    def setUp(self):
        self.mockCommonObjects()
        self.msvsSolutionWriter = self.patch(CUT, MsvsSolutionWriter.__name__, autospec=True)
        self.ideXmlWriter_write = self.patch(CUT, '{0}.{1}'.format(IdeXmlWriter.__name__, IdeXmlWriter.write.__name__))

        self.writer = MsvsLegacyWriter('msvs', self.makefileProject, self.tools)

    def test_init(self):
        actual = self.writer._doc.toprettyxml()
        output = os.path.join('..', attributes.OUTPUT_DIRECTORY, "bin",
                              "{0}.exe".format(self.makefileProject.outputName))
        expected = parseXmlString(self.PROJECT_TEMPLATE.format(
            version=TEST_VERSION, name=self.makefileProject.projectName, guid=self.writer._PROJECT_GUID,
            nmake=TEST_NMAKE_FILE, filename=TEST_MAKEFILE, output=output,
            definitions=";".join(self.makefileProject.definitions)
        )).toprettyxml()
        self.assertEqual(expected, actual)

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
                         "vs_" + self.makefileProject.projectName + ".vcproj"), call().write()]
        self.assertCalls(self.msvsSolutionWriter, expected)

    def __getElements(self, tagName, **xmlAttributes):
        tags = self.writer._doc.getElementsByTagName(tagName)
        for tag in tags:
            for attribute, value in xmlAttributes.items():
                if not tag.getAttribute(attribute) == value:
                    break
            else:
                yield tag
