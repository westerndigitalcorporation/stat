# Changelog

[![The format is based on Keep a Changelog](https://img.shields.io/badge/Keep%20a%20Changelog-1.0.0-brightgreen?style=plastic)](https://keepachangelog.com/en/1.0.0/)
[![The project adheres to](https://img.shields.io/badge/Semantic%20Versioning-v2.0.0-brightgreen?style=plastic)](https://semver.org/spec/v2.0.0.html)
[![Date Format follows ISO-8601](https://img.shields.io/badge/ISO-8601%20Date%20Format%20-brightgreen?style=plastic)](http://www.iso.org/iso/home/standards/iso8601.htm)

All notable changes to this project will be documented in this file.

<!-- Types of changes:
### Added       - for new features.
### Changed     - for changes in existing functionality.
### Deprecated  - for soon-to-be removed features.
### Removed     - for now removed features.
### Fixed       - for any bug fixes.
### Security    - in case of vulnerabilities.

Release name format: [2.2.1] - 2020-02-02
-->

## [Unreleased]

None

##  [1.2.2] - 2020-08-24:

### Fixed 

- Fixed an issue related to inconsistency of NMAKE to deal with assignments of environment variables, which caused occasional failures of incremental build

##  [1.2.1] - 2020-08-17:

### Fixed 

- Fixed issues with incremental build that caused failures due to extreme over-checking of warnings fired by the linker

### Changed

- Improved the performance of the incremental build mode to ensure efficient running for automation
- Added a rule to MSVS core-makefiles that bypasses an issue with makefiles having bad syntax that caused incremental build to fail

##  [1.2.0] - 2020-08-12:

### Added

- Added several types of building options (e.g. incremental build, rebuild)

### Changed

- Modified the way that tool's root-path is referred to allow more flexibility
    - Supports execution of STAT-own unit-test from different IDEs (e.g. VS Code, PyCharm)
    - Reduces full-path references to minimum -> replaced (where possible) with relative path

### Fixed 

- Fixed the limitation within MSVS IDE that prevented compilation errors from being clickable from the debugger

##  [1.1.0] - 2020-07-05:

### Added

- Added support for Python 3 series (verified on versions 3.5 - 3.8, using Conda)
- Added support to several versions of Python Mock module in unit-tests of the framework

### Changed

- Changed processor counting method so that it doesn't mandatory requires `psutil` package
- Made additional adjustments to handling of `multiprocessing`-related flows, based on: 
    - Issues discovered during Python 3 adjustments  
    and
    - Issues reported by other developers in the community
- Code-style changes to meet pep-8 (except for naming conventions)

## [1.0.0] - 2020-06-26 

### Added

- First official release of STAT-framework to the open-source
- Added CHANGELOG.md following format defined by "[Keep a Changelog](https://keepachangelog.com/en/1.0.0/)"
- Added licensing information for the documentation of the framework
- Finished first draft of STAT-Framework documentation
- Added complete support to multiple versions of MS Visual Studio
- Added support for [Source Insight IDE](https://www.sourceinsight.com/)
- Added an option to boost performance by multiprocessing
- Added ability to force order-tracking for consumption of Mock-objects
- Added API to add multiple Mock-objects in one call
- Added support for _Jumbo RAM Buffer_ to allow bigger database of Mock-objects

### Changed

- Adjusted README.md to fit format defined by [standard-readme](https://github.com/RichardLitt/standard-readme) 
- Licensing ths entire repo with MIT license
- Changed response to redundant arguments from termination to warning
- Upgraded _Unity_ harness to latest version 

### Removed

- Cleaned outdated history preceding the deployment to Open Source 
