# SPDX-FileCopyrightText: (c) 2020 Western Digital Corporation or its affiliates,
#                             Arseniy Aharonov <arseniy.aharonov@gmail.com>
#
# SPDX-License-Identifier: MIT

class StatReport(object):
    REPORT_FILENAME = "report.json"

    def __init__(self):
        self.__file = open(self.REPORT_FILENAME, 'w')
        self.__file.writelines(['{\n', '\t"Tests": [\n'])
        self.__failedFiles = []

    def addRecord(self, makfile, status, info):
        self.__file.writelines('\t\t{{"Test File": {filename}, "Status": "{status}", "Info": "{information}"}},\n'.format(filename=makfile,
            status="FAILED" if status else "PASSED", information=info))
        if status:
            self.__failedFiles.append(makfile)

    def completeReport(self):
        self.__file.writelines(['\t]\n', '}\n'])
        self.__file.close()
        self.__file = None
        if self.__failedFiles:
            messageLines = '\n\t'.join([StatReportException.REPORT_CONTAINS_FAILURES] + self.__failedFiles)
            raise StatReportException(messageLines)

    def __del__(self):
        if self.__file is not None:
            self.completeReport()

class StatReportException(Exception):
    """
    Custom exception for StatReport parser
    """
    REPORT_CONTAINS_FAILURES = "The report contains failures:"