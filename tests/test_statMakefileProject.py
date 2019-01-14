import os

import stat_attributes as attributes
from testing_tools import FileBasedTestCase
from stat_makefile import StatMakefile
from stat_makefile_project import StatMakefileProject

class TestStatMakefileProject(FileBasedTestCase):
    PROJECT_EXAMPLE_PATH = "simplified_example.mak"
    PROJECT_EXAMPLE_NAME = PROJECT_EXAMPLE_PATH.split('.')[0]

    def test_projectInitialization(self):
        project = StatMakefileProject(self.PROJECT_EXAMPLE_PATH)
        makFile = StatMakefile(self.PROJECT_EXAMPLE_PATH)
        self.assertEqual(self.PROJECT_EXAMPLE_PATH, project.makeFile)
        self.assertEqual(self.PROJECT_EXAMPLE_NAME, project.projectName)
        self.assertEqual(makFile[StatMakefile.NAME], project.outputName)
        self.assertSameItems([makFile[key] for key in makFile], [project[key] for key in project])

    def test_definitionsProperty(self):
        expected = ['PROJECT_EXAMPLE', 'DEFINITION_VALUED=7', 'DEFINITION_SIMPLE']
        project = StatMakefileProject(self.PROJECT_EXAMPLE_PATH)
        self.assertSameItems(expected, project.definitions)

    def test_tree(self):
        expected = ([],
                    {'..':
                         ([],
                          {'unity':
                                   (['../unity/unity.c'] + getHeadersFromDirectory('../unity'), {}),
                            'lib':
                                  ([],
                                   {'src': (['../lib/src/stat.c', '../lib/src/stat_rng.c'], {}),
                                    'inc': (getHeadersFromDirectory('../lib/inc'), {}),
                                   })
                          }),
                     'dummies':
                         ([os.path.join(attributes.DUMMIES_DIRECTORY, file)
                           for file in ('first_dummy.h', 'second_dummy.h', 'duplicated.h')], {}),
                     'tests':
                         ([],
                          {'example':
                               (['tests/example/stat_test_example.c'], {}),
                           }),
                    })

        project = StatMakefileProject(self.PROJECT_EXAMPLE_PATH)
        self.__verifyTree(expected, project.tree)

    def test_files(self):
        expected = ['./tests/example/stat_test_example.c']
        expected += ['../unity/unity.c'] + ['../lib/src/stat.c', '../lib/src/stat_rng.c']
        expected += getHeadersFromDirectory("../unity")
        expected += getHeadersFromDirectory("../lib/inc")
        expected += [os.path.join(attributes.DUMMIES_DIRECTORY, fileName)
                         for fileName in ('first_dummy.h', 'second_dummy.h', 'duplicated.h')]

        project = StatMakefileProject(self.PROJECT_EXAMPLE_PATH)

        self.assertSameItems(expected, project.files())

    def test_sourcesTree(self):
        project = StatMakefileProject(self.PROJECT_EXAMPLE_PATH)
        expected = ([],
                    {'..':
                      ([],
                       {'unity':
                           (['../unity/unity.c'], {}),
                       'lib':
                           ([],
                            {'src':
                                (['../lib/src/stat.c', '../lib/src/stat_rng.c'], {})
                            })
                       }),
                     'tests':
                           ([],
                             {'example':
                                  (['tests/example/stat_test_example.c'], {}),
                             }),
                    })

        self.__verifyTree(expected, project.sources)

    def test_headersTree(self):
        project = StatMakefileProject(self.PROJECT_EXAMPLE_PATH)
        expected = ([], {'..':
                              ([], {'unity': (getHeadersFromDirectory('../unity'), {}),
                                    'lib':
                                        ([], {'inc':(getHeadersFromDirectory('../lib/inc'), {})
                                              })
                                   }),
                         'dummies':
                             ([os.path.join(attributes.DUMMIES_DIRECTORY, fileName)
                               for fileName in ('first_dummy.h', 'second_dummy.h', 'duplicated.h')], {})
                         })
        self.__verifyTree(expected, project.headers)

    def test_headerDuplicationConflictIsResolvedByOrderOfInclusion(self):
        project = StatMakefileProject(self.PROJECT_EXAMPLE_PATH)
        self.assertNotIn('duplicated.h', project.headers.files) # TODO: Remove after refactoring
        self.assertNotIn('duplicated.h', project.tree.files)

    def __verifyTree(self, expected, received):
        files, dirs = expected

        self.assertSameItems(files, [received[file] for file in received.files])
        self.assertSameItems(dirs, received.dirs)

        for dirNode in dirs:
            self.__verifyTree(dirs[dirNode], received[dirNode])

def getHeadersFromDirectory(dirName):
    dirContents = [os.path.join(dirName, fileName) for fileName in os.listdir(dirName)]
    return [filePath for filePath in dirContents if os.path.isfile(filePath) and '.h' == os.path.splitext(filePath)[1]]



