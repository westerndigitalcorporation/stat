import os

from stat_report import StatReport, StatReportException
from testing_tools import FileBasedTestCase, readFileLines, StdOutputSubstitution


class TestStatReport(FileBasedTestCase):

    def setUp(self):
        pass

    def tearDown(self):
        if os.path.isfile(StatReport.REPORT_FILENAME):
            os.remove(StatReport.REPORT_FILENAME)

    def test__init__reportFileCreation(self):
        expected = ['{', '"Tests": [', ']', '}']
        report = StatReport()
        report.completeReport()
        self.assertTrue(os.path.isfile(StatReport.REPORT_FILENAME))
        lines = self.__readReportLines()
        self.assertEqual(expected, lines)

    def test_addRecord(self):
        argumentList = [('makfile-A', False, 'info-A'), ('makfile-X', True, 'info-Z')]
        expected = ['{{"Test File": {0}, "Status": "{1}", "Info": "{2}"}},'.format(fileName, "FAILED" if status else "PASSED", text)
                    for fileName, status, text in argumentList]
        report = StatReport()
        for args in argumentList:
            report.addRecord(*args)
        try:
            report.completeReport()
        except StatReportException:
            pass
        lines = [line.strip() for line in readFileLines(StatReport.REPORT_FILENAME)]
        lines = lines[2:-2]
        self.assertEqual(expected, lines)

    def test_completeReport(self):
        argumentList = [('makfile-A', 0, 'info-A'), ('makfile-X', 0, 'info-Z')]
        report = self.__createReportFromArgumentList(argumentList)
        report.completeReport()

        argumentList = [('makfile-A', 0, 'info-A'), ('makfile-K', -1, 'info-M'), ('makfile-X', 0, 'info-Z'),
                        ('makfile-F', -1, 'info-Y')]
        failedMakfiles = ['\t' + args[0] for args in argumentList if args[1] != 0]
        expectedMessage = "\n".join([StatReportException.REPORT_CONTAINS_FAILURES] + failedMakfiles)
        report = self.__createReportFromArgumentList(argumentList)
        try:
            report.completeReport()
        except StatReportException as e:
            self.assertEqual(expectedMessage, str(e))
        else:
            self.fail("An exception was expected!")

    @staticmethod
    def __readReportLines():
        report = open(StatReport.REPORT_FILENAME, 'r')
        lines = [line.strip() for line in report.readlines()]
        report.close()
        return lines

    @staticmethod
    def __createReportFromArgumentList(argumentList):
        report = StatReport()
        for args in argumentList:
            report.addRecord(*args)
        return report


