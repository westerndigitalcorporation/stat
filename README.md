# STAT _(Unit-test Framework)_ <!-- omit in toc -->

![Programming C](https://img.shields.io/badge/programming-TDD%20|%20Embedded-orange.svg?style=flat&logo=c&logoColor=white)
![MSVS](https://img.shields.io/badge/MSVS-2005--2008%20|%202010--2019-blue?style=flat&logo=Visual-Studio&logoColor=white)
![Windows](https://img.shields.io/badge/Windows-7%20|%2010-blue?style=flat&logo=Windows&logoColor=white)
![python](https://img.shields.io/badge/python-2.7%20|%203.5--3.8-blue?style=flat&logo=Python&logoColor=white)  
[![standard-readme compliant](https://img.shields.io/badge/readme_style-standard-brightgreen)](https://github.com/RichardLitt/standard-readme)
[![REUSE Compliance](https://github.com/westerndigitalcorporation/stat/workflows/REUSE%20Compliance/badge.svg?branch=master)](https://api.reuse.software/info/git.fsfe.org/reuse/api)
[![Regression](https://github.com/westerndigitalcorporation/stat/workflows/Regression/badge.svg?branch=master)](https://github.com/westerndigitalcorporation/stat/actions?query=workflow%3ARegression+branch%3Amaster)

<u>**St**</u>and<u>**A**</u>lone unit-<u>**T**</u>esting framework for software written in C

STAT is designed to promote an instant assimilation of Test-Driven Development in conditions of large-scale codebases that are constrained with *heavy load of legacy code*. 
The framework was conceived with special regard to limitations of embedded environments and to implementation-concepts widely accepted in embedded programming.
It is based on a really great open-source project named [Unity](http://www.throwtheswitch.org/unity) (which can be found also on [GitHub](https://github.com/ThrowTheSwitch/Unity)).

## Table of Contents <!-- omit in toc -->

- [1. Background](#1-background)
  - [1.1. Unity Harness](#11-unity-harness)
- [2. Install](#2-install)
- [3. Usage](#3-usage)
- [4. Integration](#4-integration)
  - [4.1. OS](#41-os)
  - [4.2. Build Tools](#42-build-tools)
  - [4.3. IDEs](#43-ides)
- [5. Maintainer](#5-maintainer)
- [6. Contributing](#6-contributing)
  - [6.1. Contributors](#61-contributors)
- [7. License](#7-license)
  - [7.1. Imported Components](#71-imported-components)
- [8. Definitions](#8-definitions)

## 1. Background

We tried several unit-test frameworks, and there are quite a few really great products. 
So, we stated the following principles for the framework we were looking for:

* *Simplicity* – test-setup shall be simple, fast and intuitive
* *Speed* – execution shall be fast and focused to support TDD short cycles
* *Lightweight* – portability to embedded platforms shall be simple (planned for the future)
* *Comprehensive feedback* – better logging &rArr; lesser step-by-step debugging &rArr; better efficiency  
* *Reproducibility*– tests shall be reproducible and deterministic
* *Test-code sharing* – reduce the inevitable code-duplication (e.g. test-doubles)
* *Automation* – test automation shall be very simple to achieve
* <u>***CUT-Isolation***</u> – decouple from noise-impact of other FW-components, HW or OS

_The last one we found most critical for our needs due to constraints described in [Conceptual Model](./docs/conceptual_model.md)._ 

The *CUT-Isolation* principle was the one where most of the evaluated solutions failed to meet our expectations. 
In addition, there were some simply technical reasons that also made frameworks existing at that time less suitable. 
Our lab machines were beyond control of our team, and those were equipped with *Windows* OS, *Python* 2.7, *MS Visual Studio* and our target build tool-chain.
  
>No lua, Ruby, CMake or any other things of that kind.

Eventually, it was decided to build our own framework that will fit the bill. 

### 1.1. Unity Harness

Though we couldn't find the framework that will answer all our requirements, still there are those ones that are very close.
[*Unity harness*](http://www.throwtheswitch.org/unity) was that great "almost"-match.
Therefore, we decided to build our framework based on it, due to the following clear advantages of the Unity harness:

* Minimalistic in size and dependencies on system libraries
* Can be compiled almost on any platform
* Provides rich and strong assertion mechanism
* Prints very comprehensive logging and results
* Tolerant to test-failures
    * Failing test (if properly built) doesn't crash the
    subsequent tests 

An additional advantage worthy of a separate discussion is the very fact that Unity is written in C. 
This is the same language we use to write our production code.  
It is  better to prevent developers from constantly switching between different language paradigms. 
In addition, writing in the same language gives a developer the same sense of experience whether writing production code or unit-test code. 

## 2. Install

Please refer the [*Getting Started*](./docs/stat_getting_started.md) user-guide describing how to install and to setup the framework and unit-test packages.

## 3. Usage

Please refer the following user-guides describing how to work with STAT framework:

1. [*Command-line*](docs/stat_commandline.md) - full description of all possible command-line arguments to control behavior of STAT
2. [*Unity Assertions Reference*](./unity/docs/UnityAssertionsReference.md) - the original '*Unity*' user-guide with usage-description of assertion macros
3. [*STAT-Mock Library*](./docs/stat_mock.md) - user-guide describing how to use built-in Mock library of STAT framework

Here is additional helpful Unity documentation:

* [Conceptual Model](./docs/conceptual_model.md) - conceptual model underlying the design of the framework, a valuable knowledge to become Pro with STAT
* [*Unity Assertions Cheat Sheet*](./unity/docs/UnityAssertionsCheatSheetSuitableforPrintingandPossiblyFraming.pdf) - a cook-book with macros worth printing and framing
* [*Unity Configuration Guide*](./unity/docs/UnityConfigurationGuide.md) - the default configuration of Unity defined within STAT can be overwritten

## 4. Integration

### 4.1. OS

STAT-framework is built to run both on Windows and Linux.

### 4.2. Build Tools

STAT-framework has an integrated support for build-tools, which are determined based on OS, localy instlled tools and user-configuration:

- On Windows: _Microsoft Visual Studio_ including all versions from 2005 up to 2019 (any edition, i.e. Community, Professional and Enterprise).  

- On Linux: _GNU Compiler_, i.e. GCC

STAT is designed to minimize its requirements from the system. Therefore, it uses a precompiled _GNU Make Tool_ (included in the repo) instead of complimentary ones like CMake.  

> This decision was dictated by restrictions of our lab, which didn't allow installing of any additional software.

***MSVS Versioning***

If not explicitly specified in file "[.statconfig](./docs/statconfig.md)", the latest MSVS version on the machine gets identified and gets set as active build-tools. Otherwise, the specified version is selected instead. The latter is useful to fixate on common single version for all developer and lab machines.

### 4.3. IDEs

Framework provides services to generate project files for certain IDEs, by the means of [command-line](docs/stat_commandline.md). The following IDEs are currently supported:
* _Microsoft Visual Studio_ of version corresponding to the selected [build-tools](#build-tools).
  * The generated project file for this IDE support step-by-step debugging 
* _Source Insight 4.0_ - it is a unique IDE, which also is a code-analyzer, actually one of a kind.

>There is an effort to add support for some additional IDEs, e.g. VS Code

## 5. Maintainer

&nbsp;&nbsp;&nbsp;*Arseniy Aharonov* - maintainer and main contributor  
&nbsp;&nbsp;&nbsp;[![GitHub](https://img.shields.io/badge/%20-@are&minus;scenic-blue.svg?style=social&logo=GitHub)](https://github.com/are-scenic) [![GitHub](https://img.shields.io/badge/Contact-@arseniy@aharonov.icu-blue.svg?style=social)](mailto:arseniy@aharonov.icu)

## 6. Contributing

Feel free to impact! [Open an issue](https://github.com/westerndigitalcorporation/stat/issues).  

<!--
STAT framework follows the [Contributor Covenant](http://contributor-covenant.org/version/1/3/0/) Code of Conduct.
-->

### 6.1. Contributors

An open source project thrives on contribution of different people, and it may come in many forms. Some develope the very code, others provide constructive feedback, and some share wisdom through guidance and consultation. And all of these are very valuable contributions made by very valuable contributors:  

* Eitan Talianker  
[![GitHub](https://img.shields.io/badge/@etalianker-blue.svg?style=social&logo=GitHub)](https://github.com/etalianker)
* Dr.Eitan Farchi  
[![GitHub](https://img.shields.io/badge/@farchi@il.ibm.com-blue.svg?style=social&logo=IBM)](mailto:farchi@il.ibm.com)
* Udi Arie  
[![GitHub](https://img.shields.io/badge/@udiarie-blue.svg?style=social&logo=GitHub)](https://github.com/udiarie)
* Oran DeBotton    
[![GitHub](https://img.shields.io/badge/SolarEdge-@oran.debotton@SolarEdge.com-blue.svg?style=social)](mailto:oran.debotton@SolarEdge.com)

## 7. License

The base-code of the STAT framework is licensed under [MIT license](LICENSES/MIT.txt). In addition, this repo contains a binary of GNU-Make tool, which is distributed under [GPLv3+ license](LICENSES/GPL-3.0-or-later.txt).

### 7.1. Imported Components

STAT wasn't build from scratch. Several valuable components underlay the framework:

* Unity harness source-files - a [key component](#unity-harness) for the framework
  * License: [MIT](./unity/LICENSE.txt)
  * Source: [on GitHub](https://github.com/ThrowTheSwitch/Unity)
* Visual Studio Locator (a.k.a. `vswhere`) - a utility to locate Visual Studio in newer versions of MSVS. 
  * License: [MIT](https://github.com/microsoft/vswhere/blob/ded0fdd04473772af1dd001d82b6e3c871731788/LICENSE.txt)
  * Source: [on GitHub](https://github.com/Microsoft/vswhere/releases)
* GNU Make tool - controls generation of executables from sources based on makefiles
  * License: [GPLv3+ license](LICENSES/GPL-3.0-or-later.txt)
  * Source: [on GNU.org](https://www.gnu.org/software/make/)


## 8. Definitions

_These definitions are provided to clarify terms used above._

* **STAT** – stands for standalone testing framework
* **CUT** – means Code Under Test; usually it is a module or a sub-module that is tested
* **DOC** – means Depended-on Component; in the literature this term is used to describe external dependencies that our CUT depends on
* **CUT-Isolation** – is a method of decoupling the CUT from the other parts of FW-Code for unit-testing purposes, meaning how we deal with DOCs in our unit-tests
* **FW** - Firmware
* **Test-Double** – is a substitution of an operational version of DOC with a test-version that emulates a real interface, but serves testing goals
* **Test-package** – in terms of STAT-framework, it represents a group of unit-tests that run as a single executable; it usually covers a specific CUT
* **TDD** - [Test-Driven Development](https://www.agilealliance.org/glossary/tdd), see also [TDD](https://martinfowler.com/bliki/TestDrivenDevelopment.html) for more details
