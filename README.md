# STAT <small>*(Unit-test Framework)*</small>

STAT stands for <u>**ST**</u>and<u>**A**</u>lone unit-<u>**T**</u>esting 
framework. It is based on a really great open-source project named
[Unity](http://www.throwtheswitch.org/unity) (can be found also on 
[GitHub](https://github.com/ThrowTheSwitch/Unity)).  

STAT was designed to promote an instant assimilation of the TDD 
methodology in ad-hock conditions of a heavy-legacy codebase, 
and with emphasis on embedded environments.

##### *The motto is:* 
>"*Don't wait for everything to align and coincide
>and for everybody to commit!  
>Start TDD today - one piece of the code at a time!*"

##### *Disclaimer*

>*It is highly recommended to get acquainted with chapter
>"Problem Statement" and the
>[theoretical background](docs/stat_theoretical_background.md)
>that underlies the design of STAT-Framework. It will provide an 
>essential advantage for working with the framework and maximize 
>the benefit from it.* 

### Terminology

* **STAT** – stands for standalone testing framework
* **CUT** – means Code Under Test; 
    usually it is a module or a submodule that is tested
* **DOC** – means Depended-on Component; 
    in the literature this term is used to describe 
    external dependencies that our CUT depends on
* **CUT-Isolation** – is a method of decoupling the CUT 
    from the other parts of FW-Code for unit-testing purposes, 
    meaning how we deal with DOCs in our unit-tests
* **FW** - Firmware
* **Test-Double** – is a substitution of an operational version of DOC 
    with a test-version that emulates a real interface, 
    but serves testing goals
* **Test-package** – in terms of STAT-framework, it represents 
    a group of unit-tests that run as a single executable; 
    it usually covers a specific CUT
* **TDD** - [Test-Driven Development](https://www.agilealliance.org/glossary/tdd)
    * see also [TDD](https://martinfowler.com/bliki/TestDrivenDevelopment.html)
    for more details

### Guides and Help-Documentation

It is highly recommended initially to get acquainted with 
[**Theoretical Background**](docs/stat_theoretical_background.md) underlying
the design of the STAT framework.  
Please also refer the guides of the framework and its comprising components:
1. [**Getting Started**](./docs/stat_getting_started.md) -
user-guide describing how to setup the framework and unit-test packages
2. [**Commandline**](docs/stat_commandline.md) -
full description of all possible commandline arguments to control behavior of STAT
3. [***Unity*** **Assertions Reference**](./unity/docs/UnityAssertionsReference.md) - 
the original '*Unity*' user-guide with usage-description of assertion macros
4. [**STAT-Mock Library**](./docs/stat_mock.md) -
user-guide describing how to use built-in Mock library of STAT framework

Here is additional helpful documentation:
* [Unity Assertions Cheat Sheet](./unity/docs/UnityAssertionsCheatSheetSuitableforPrintingandPossiblyFraming.pdf) - 
a cook-book with Unity macros worth printing and framing
* [Unity Configuration Guide](./unity/docs/UnityConfigurationGuide.md) - 
the default configuration of Unity defined within STAT can be overwritten

### Goals

We tried several unit-test frameworks, and there are quite a few
really great products. So, we stated the following goals for the 
framework we were looking for:

* *Simplicity* – test-setup shall be simple, fast and intuitive
* *Speed* – compilation and execution shall be fast and focused 
  to support TDD short cycles and encourage refactoring
* *Lightweight* – it shall enable portability to embedded platforms 
  (we plan to support it in the future)
* *Comprehensive feedback* – better logging &rArr; 
  lesser step-by-step debugging &rArr; greater efficiency
  * R&D should really stand for Research and Development, 
    rather than for Research and Debugging  
* *Reproducibility*– tests shall be reproducible
  * Non-reproducible tests are nothing but annoying reminder for
  an existing bug that we fail to identify
* *Test-code sharing* – reduce the inevitable code-duplication 
  * Test-doubles contain word duplication in their very name.  
  * It'd be better to enable easy sharing of such components
* *Automation* – test automation shall be very simple to achieve
* <u>***CUT-Isolation***</u> – pure unit-testing without noise of 
  other FW-code, HW or OS
  * achieving static polymorphism to substitute the need of dynamic
  * reduction of DOC-s (dependent-on components)
  * standalone (per CUT) development

_The last one we found as most critical one for our needs due 
to constraints mentioned in "Problem Statement" chapter._ This is 
were most of the evaluated solutions failed so far. But, there
were some simply technical reasons that also made frameworks
existing at that time less suitable. Our lab machines were
beyond control of our team, and they were equipped with 
*Windows* OS, *Python* 2.7, *MS Visual Studio* and our target build 
toolchain.
  
>No Rubi, lua, CMake or any other things of that kind.

### Unity Harness

Eventually, we decided to build our own framework that will fit
the bill. Despite that decision we also understood that though
the evaluated frameworks couldn't fit all of our requirements,  
there are still those ones that are very close. 
[***Unity***](http://www.throwtheswitch.org/unity) harness was 
that great almost-match, and thus we decided to build ours 
based on it due to the following clear advantages of 
the Unity harness:

* Minimalistic in size and dependencies on system libraries
* Can be compiled almost on any platform
* Provides rich and strong assertion mechanism
* Prints very comprehensive logging and results
* Tolerant to test-failures
    * Failing test (if properly built) doesn't crash the
    subsequent tests 

An additional advantage worthy of a separate discussion is
the very fact that Unity is written in C. This is the same
language we use to write our production code.  
It is  better to prevent developers from constantly 
switching between different language paradigms. 
In addition, writing in the same language gives a developer 
the same sense of experience whether writing production code or 
unit-test code. 
