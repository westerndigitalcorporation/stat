import os
from shutil import rmtree

import stat_attributes as attributes
from services import readTextFileAtOnce
from si_ide_writer import WORKSPACE_PATH, SourceInsightWriter
from stat_makefile_project import StatMakefileProject
from testing_tools import FileBasedTestCase

TEST_MAKEFILE = 'simplified_example.mak'
TEST_TARGET_NAME = TEST_MAKEFILE[:-len('.mak')]
TEST_WORKSPACE_PATH = \
    WORKSPACE_PATH.format(basePath=attributes.IDE_DIRECTORY, name=TEST_TARGET_NAME)
SOURCE_INSIGHT_FILE_LIST = "{path}/si_filelist.txt".format(path=TEST_WORKSPACE_PATH)

class TestSourceInsightWriter(FileBasedTestCase):

    def setUp(self):
        if not os.path.isdir(attributes.IDE_DIRECTORY):
            os.mkdir(attributes.IDE_DIRECTORY)
        self.contents = StatMakefileProject(TEST_MAKEFILE)
        self.writer = SourceInsightWriter(SourceInsightWriter.IDE, self.contents)

    def tearDown(self):
        if os.path.isdir(attributes.IDE_DIRECTORY):
            rmtree(attributes.IDE_DIRECTORY)

    def test_tokenCreation(self):
        writer = self.writer
        self.assertEqual(None, writer.createRootToken())
        self.assertEqual(None, writer.createDirectoryToken('Some-Name', None))

    def test_write(self):
        self.writer.write()

        actual = [fn.split('.')[0] for fn in os.listdir(TEST_WORKSPACE_PATH) if fn not in ['si_filelist.txt']]
        expected = [TEST_TARGET_NAME] * len(actual)
        self.assertEqual(expected, actual)
        projectFile = '{path}/{fileName}.siproj'.format(path=TEST_WORKSPACE_PATH, fileName=TEST_TARGET_NAME)
        self.assertTrue(os.path.isfile(projectFile))
        self.assertEqual(TEST_MAKEFILE, readTextFileAtOnce(SOURCE_INSIGHT_FILE_LIST))

    def test_addFile(self):
        for filename in self.contents.files():
            self.writer.addFile(filename, None)
        self.writer.write()

        expected = '\n'.join([TEST_MAKEFILE] + [filename for filename in self.contents.files()])
        self.assertEqual(expected, readTextFileAtOnce(SOURCE_INSIGHT_FILE_LIST))

    def test_updatedWrite(self):
        self.writer.write()

        self.writer.addFile(SOURCE_INSIGHT_FILE_LIST, None)
        self.writer.write()

        expected = '\n'.join([TEST_MAKEFILE, SOURCE_INSIGHT_FILE_LIST])
        self.assertEqual(expected, readTextFileAtOnce(SOURCE_INSIGHT_FILE_LIST))

