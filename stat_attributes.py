VERSION = '2.1.31'

########################################################################################################################
def __getToolPath():
    import os # Prevent porting by those which import this file
    return os.path.dirname(os.path.relpath(__file__))
#-----------------------------------------------------------------------------------------------------------------------

TOOL_PATH = __getToolPath()
RESOURCES_DIRECTORY = 'resources'
DUMMIES_DIRECTORY = 'dummies'
PRODUCT_DIRECTORY = 'products'
LOGS_DIRECTORY = 'logs'
IDE_DIRECTORY = 'ide'
OUTPUT_DIRECTORY = 'output'
REPORT_FILENAME = "report.json"
CONFIG_FILENAME = '.statconfig'
MASTER_INCLUDE_PATH = OUTPUT_DIRECTORY + '/inc'
AUTO_GENERATED_MAKEFILE = '/'.join([OUTPUT_DIRECTORY, "stat.mak"])

OUTPUT_SUB_DIRECTORIES = ['inc', 'obj', 'bin']
ALL_OUTPUT_DIRECTORIES = [OUTPUT_DIRECTORY, IDE_DIRECTORY, LOGS_DIRECTORY]

