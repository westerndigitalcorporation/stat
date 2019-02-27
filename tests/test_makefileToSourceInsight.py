import os

from makefile_source_insight import MakefileToSourceInsight
from services import StatConfiguration
from stat_makfile_project import StatMakefileProject
from tests.testing_tools import FileBasedTestCase
from shutil import rmtree

class TestMakefileToSourceInsight(FileBasedTestCase):
    TEST_MAKEFILE = 'simplified_example.mak'
    SOURCE_INSIGHT_PROJECT_FOLDER = \
        MakefileToSourceInsight.PROJECT_FOLDER_NAME.format(basePath=StatConfiguration().OUTPUT_DIRECTORY,
                                                           name=TEST_MAKEFILE[:-len('.mak')])
    SOURCE_INSIGHT_FILE_LIST = "{path}/si_filelist.txt".format(path=SOURCE_INSIGHT_PROJECT_FOLDER)

    def setUp(self):
        self.__cleanup()
        self.builder = MakefileToSourceInsight(self.TEST_MAKEFILE)
        self.builder.buildProject()


    def tearDown(self):
        self.__cleanup()

    @staticmethod
    def __cleanup():
        config = StatConfiguration()
        if os.path.isdir(config.OUTPUT_DIRECTORY):
            rmtree(config.OUTPUT_DIRECTORY)

    def test_buildSourceInsightProject(self):
        projectFile = '{path}/{fileName}'.format(path=self.SOURCE_INSIGHT_PROJECT_FOLDER, fileName = 'stat.siproj')

        self.assertTrue(os.path.isfile(projectFile))
        self.assertTrue(os.path.isfile(self.SOURCE_INSIGHT_FILE_LIST))
        pass

    def test_sourceInsightFileListCreation(self):
        fileListFile = open(self.SOURCE_INSIGHT_FILE_LIST, 'r')
        generatedFileList = [line.strip() for line in fileListFile.readlines()]
        fileListFile.close()

        makefile = StatMakefileProject(self.TEST_MAKEFILE)
        expectedFileList = [self.TEST_MAKEFILE] + list(makefile.files())
        self.assertSameItems(expectedFileList, generatedFileList)
        pass

    def test_onlyFileListIsGeneratedUponExistingProject(self):
        os.remove(self.SOURCE_INSIGHT_FILE_LIST)

        self.builder.buildProject()
        self.assertTrue(os.path.isfile(self.SOURCE_INSIGHT_FILE_LIST))
        pass


