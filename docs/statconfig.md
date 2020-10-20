# *`.statconfig`* options

File `.statconfig` is an optional file that contains configuration values and directives. If exists, it is located in the root directory (see [Getting Started](./stat_getting_started.md)) of the STAT instance within the code of the codebase.  

> Currently it supports only selection of MS-VS version selection.

## MS Visual Studio Version

This configuration parameter defines the version of
MS Visual-Studio that STAT shall seek to build the
test-packages. 

*For example:*  

    `MSVS_VERSION = 2008`

* The version shall be specified by the year
* The supported versions are from `2005` up to `2019`
* If the parameter is not explicitly specified, *STAT-framework determines the **latest** version* and uses it as a default choice

