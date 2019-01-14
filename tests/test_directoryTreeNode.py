import os
from unittest import TestCase

from directory_tree_node import DirectoryTreeNode, DirectoryTreeNodeException


class TestDirectoryTreeNode(TestCase):
    FILE_IN_ROOT_DIRECTORY = 'file_in_root.c'
    FILE_IN_SUB_DIRECTORY = 'mak_examples/simple.mak'
    FIRST_FILE_IN_SUB_TREE = 'tests/example/stat_test_example.c'
    SECOND_FILE_IN_SUB_TREE = 'tests/example/stat_another_example.c'

    def test_addFileWithinCurrentDirectory(self):
        node = DirectoryTreeNode()
        node.addFile(self.FILE_IN_ROOT_DIRECTORY)
        self.assertEqual([self.FILE_IN_ROOT_DIRECTORY], node.files)
        self.assertEqual([], node.dirs)
        self.assertEqual(self.FILE_IN_ROOT_DIRECTORY, node[self.FILE_IN_ROOT_DIRECTORY])

    def test_addFileWithCurrentDirectoryPrefix(self):
        node = DirectoryTreeNode()
        node.addFile("/".join(['.', self.FILE_IN_ROOT_DIRECTORY]))
        self.assertEqual([self.FILE_IN_ROOT_DIRECTORY], node.files)
        self.assertEqual([], node.dirs)
        self.assertEqual(self.FILE_IN_ROOT_DIRECTORY, node[self.FILE_IN_ROOT_DIRECTORY])

    def test_addFileWithinSubdirectory(self):
        node = DirectoryTreeNode()
        node.addFile(self.FILE_IN_SUB_DIRECTORY)
        subdirName, fileName = os.path.split(self.FILE_IN_SUB_DIRECTORY)
        self.assertEqual([], node.files)
        self.assertEqual([subdirName], node.dirs)
        self.assertTrue(subdirName in node)
        dirNode = node[subdirName]
        self.assertEqual([fileName], dirNode.files)
        self.assertEqual([], dirNode.dirs)
        self.assertEqual(self.FILE_IN_SUB_DIRECTORY, dirNode[fileName])

    def test_addFileWithinSubtree(self):
        node = DirectoryTreeNode()
        node.addFile(self.FIRST_FILE_IN_SUB_TREE)
        fileName = os.path.basename(self.FIRST_FILE_IN_SUB_TREE)
        dirName, subdirName = os.path.dirname(self.FIRST_FILE_IN_SUB_TREE).split('/')
        self.assertEqual([], node.files)
        self.assertEqual([dirName], node.dirs)
        dirNode = node[dirName]
        self.assertEqual([], dirNode.files)
        self.assertEqual([subdirName], dirNode.dirs)
        self.assertTrue(subdirName in dirNode)
        subdirNode = dirNode[subdirName]
        self.assertEqual([fileName], subdirNode.files)
        self.assertEqual([], subdirNode.dirs)
        self.assertEqual(self.FIRST_FILE_IN_SUB_TREE, subdirNode[fileName])

    def test_addMultipleFilesWithinSingleDirectory(self):
        files = [self.FIRST_FILE_IN_SUB_TREE, self.SECOND_FILE_IN_SUB_TREE]
        node = DirectoryTreeNode()
        for filePath in files:
            node.addFile(filePath)
        dirName, subdirName = os.path.dirname(self.FIRST_FILE_IN_SUB_TREE).split('/')
        self.assertEqual([], node.files)
        self.assertEqual([dirName], node.dirs)
        dirNode = node[dirName]
        self.assertEqual([], dirNode.files)
        self.assertEqual([subdirName], dirNode.dirs)
        self.assertTrue(subdirName in dirNode)
        subdirNode = dirNode[subdirName]
        self.assertEqual([os.path.basename(filePath) for filePath in files], subdirNode.files)
        self.assertEqual([], subdirNode.dirs)
        for filePath in files:
            self.assertEqual(filePath, subdirNode[os.path.basename(filePath)])

    def test_addNoneExistingFile(self):
        nonExistingFile = './non_existing_path/non_existing_file.c'
        node = DirectoryTreeNode()
        try:
            node.addFile(nonExistingFile)
        except DirectoryTreeNodeException as e:
            self.assertEqual("The file '{fileName}' doesn't exist!".format(fileName = nonExistingFile), str(e))
        else:
            self.fail('The operation should have raised an exception')

    def test_getFiles(self):
        expectedFiles = [self.FILE_IN_ROOT_DIRECTORY, self.FILE_IN_SUB_DIRECTORY,
                         self.FIRST_FILE_IN_SUB_TREE, self.SECOND_FILE_IN_SUB_TREE]
        node = DirectoryTreeNode()
        for filePath in expectedFiles:
            node.addFile(filePath)

        receivedFiles = node.getAllFilePaths()
        for filePath in expectedFiles:
            self.assertIn(filePath, receivedFiles)


