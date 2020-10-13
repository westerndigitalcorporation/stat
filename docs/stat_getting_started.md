# Getting Started <!-- omit in toc -->

## Introduction <!-- omit in toc -->

The ultimate goal that was stated for STAT-framework was to enable instant initiation of practicing TDD, with almost no requirements from the development platform and from everybody to commit to the process. 

>As it was mentioned in [README](../README.md) document STAT was designed to run on _Windows_ machine with only _Visual Studio_ and _Python_. But it being extended to support more (e.g. GCC, Linux).

## Table of Contents <!-- omit in toc -->

- [1. Framework Setup](#1-framework-setup)
  - [1.1. Retrieval of STAT-Framework](#11-retrieval-of-stat-framework)
  - [1.2. Integration into Codebase](#12-integration-into-codebase)
- [2. Test-package Setup](#2-test-package-setup)
  - [2.1. Initialization](#21-initialization)
  - [2.2. Test Source-File](#22-test-source-file)
  - [2.3. Test Setup and Teardown Handlers](#23-test-setup-and-teardown-handlers)
- [3. Product-Level Setup](#3-product-level-setup)
  - [3.1. Product-Level Setup and Teardown](#31-product-level-setup-and-teardown)
- [4. Directory Overview](#4-directory-overview)
  - [4.1. Files within Instance-Directory](#41-files-within-instance-directory)
  - [4.2. CFiles within Products-Directory](#42-cfiles-within-products-directory)

## 1. Framework Setup

### 1.1. Retrieval of STAT-Framework

The distribution of STAT-framework takes an idea from `repo` tool. One doesn't have to include it into the repository with the code base. It is enough to clone STAT-repository to one of the directories that are shared with the codebase-repository on the directory tree. The only requirement is to name the root-directory of STAT as `./stat`.

>For instance, directory `stat` can be located in the same directory with the root directory of the code-base repo.

### 1.2. Integration into Codebase

In the same codebase there can be several instances of STAT. Each such instance is like a separate unit-test workspace with its own configuration, absolutely independent from other instances within the codebase. This model can suit the products that are composed of several binaries that are not directly related (e.g. ROM code and RAM code), and thus have to be tested separately.

To create an instance one shall simply copy from the root-directory of STAT the folder named `distribution` to any sub-directory of the codebase. The name doesn't have to stay `distribution`. It can be anything else.  
This folder now represents an instance of STAT.

>For example, STAT-Framework itself has its own instance of itself, which is used to develop its built-in Mock library. It can be used as a reference on how to create such instance (see in [./lib/tests](../lib/tests)).

## 2. Test-package Setup

With STAT each CUT has its own test-package that is compiled into a separate executable. This ensures full decoupling between the packages of different CUTs. Therefore, if for some reason a certain package crashes, it has no impact on other packages at all.

### 2.1. Initialization

Each test-package in STAT-framework is represented by a simple text-file that uses semantics of a *makefile*. It doesn't require from the developer to be a makefile savvy to setup a package. However, some knowledge of its syntax might give certain benefits, but once again not mandatory.


_Test-package makefile has the following structure:_

```makefile
# Make-file for a Test-Package(STAT)
#
# SOURCES - list of all source files
# INCLUDES - list of all include directories
# DUMMY_INTERFACES - list of all dummy header-files to be used instead FW-version
# DEFINES - list of definitions to be invoked via command-line

# Source files
SOURCES = <source file to compile with a relative path> \
    <another source file to compile with a relative path> ...

# Include directories
INCLUDES = <1st relative path to add to inclusion paths> \  
    <2nd relative path to add to inclusion paths> ...

# Dummy interfaces used to replace real ones
DUMMY_INTERFACES = <dummy-header> <another dummy-header> ...

# Preprocessor definitions
DEFINES = <definition> <definition>=<value> ...

# Include the STAT build rules
include ./output/stat.mak
```

Whereas the last line in the file is for STAT-framework needs and shall be inserted as it is, other variables in the file have certain meaning: 

* `SOURCES` - a space-separated list of source files that shall compile for the test-package
* `INCLUDES` - a space-separated list of relative paths to be included by the test-package
* `DUMMY_INTERFACES` - a space-separated list of *Dummy Interfaces* to substitute original DOC API-header files
* `DEFINES` - a space-separated list of global definitions for the preprocessor to be applied to the test-package 
    
> Note that all paths in the *makefile* shall appear in POSIX format only.

### 2.2. Test Source-File

In addition to the makefile the developer is expected also to implement `_UU32 Stat_Main(void)` function. STAT-framework assumes this symbol upon linking and treats it as an entrance function of the test-package.

Each test package may have from one to several files with tests.  

If there is only one test source-file, it would be the one that will probably contain the implementation of `Stat_Main()`. In this case this function shall start with calling macro `UNITY_BEGIN()`, then `RUN_TEST` for each test, and finally it shall return with `UNITY_END()`.

_Example:_

```c
...
_UU32 Stat_Main(void)
{
  UNITY_BEGIN();
  RUN_TEST(Test_TestInitialization);
  RUN_TEST(Test_TestSomewhatUsecase);
  ...
  return UNITY_END();
}
...
```

However, the developer might want to create several test groups, most likely with a test source-file per group. In this case each file should have its own '*main()*' that shall start with `UNITY_BEGIN()` and return `UNITY_END()`.  
In this case `Stat_Main()` shell simply aggregate the return values of '*main*'-functions of all test groups and return a combined result.

_Example:_

```c
...
_UU32 Stat_Main(void)
{
  _UU32 status = 0;
  status |= Test_RunSomeTestGroup();
  status |= Test_RunAnotherTestGroup();
  ...
  return status;
}
...
```

### 2.3. Test Setup and Teardown Handlers

It is important to ensure each test has a clean start:
* Test should not assume that any preceding test leaves a certain state
* Test should not have any impact even from a failing test
 
In almost all frameworks there is a facility that allows installation of `setup` and `teardown` handlers, exactly for this purpose. STAT-framework is no different in this from other unit-tests solutions.

Before any group of test-registrations that issued with `RUN_TEST(...)` the developer may call the following API:

```c
  void Stat_SetTestSetupTeardownHandlers(STAT_HANDLER setup, STAT_HANDLER teardown) 
```

If at least one of the passed function-pointers points to a real function rather than NULL, it will be called automatically before and/or after each test depending on whether it's a setup or a teardown handler.

This API can be called several times in the same test-package. Each time it is called, it overrides the preceding call for all the tests registered after this one.


## 3. Product-Level Setup

STAT-framework supports product-level makefile. This file is mostly like a test-package, with only difference that it affects all test-packages. 

_Product-level makefile has the following format:_

```makefile
# Make-file for a Product configuration(STAT)
#
# PRODUCT_SOURCES - list of all source files
# PRODUCT_INCLUDES - list of all include directories
# DUMMY_INTERFACES - list of all dummy header-files to be used instead FW-version
# DEFINES - list of definitions to be invoked via command-line

# Source files
PRODUCT_SOURCES = <source file to compile with a relative path> \
    <another source file to compile with a relative path> ...

# Include directories
PRODUCT_INCLUDES = <1st relative path to add to inclusion paths> \  
    <2nd relative path to add to inclusion paths> ...

# Dummy interfaces used to replace real ones
PRODUCT_DUMMY_INTERFACES = <dummy-header> <another dummy-header> ...

# Preprocessor definitions
PRODUCT_DEFINES = <definition> <definition>=<value> ...
```

The meaning of each of the fields corresponds to those of a test-package makefile (see above).

There shall at least one product-level makefile, which maybe absolutely empty. However, STAT allows more then one product-level makefile. It might be handy, if the same codebase comprises several products/flavours with different sets of configuration toggles.  
In this case, it makes sense to run tests for each of the products, to make sure that changing some code for one product we don't break others.  

### 3.1. Product-Level Setup and Teardown

There are setup and teardown at the product-level, which are called for each test of all the test-packages:

* `void Stat_SetupProductTest(void)` – setup common for all test-packages
* `void Stat_TeardownProductTest(void)` – cleanup common for all test-packages

>Defining these handlers is a must, but can be empty functions.

## 4. Directory Overview

The instance directory has certain structure, which can be extended for the convenience of the user:

* `dummies` - this directory shall be used for 'Dummy Interfaces' (if this concept is followed)
  * It's not mandatory, but highly recommended
  * Please see [Conceptual Model](,/../conceptual_model.md) 
  for the description of this concept
* `[ide]` - this is an auto-created output directory that contains ide solutions/projects generated upon user's request
* `[log]` - this is an auto-created output directory that contains logs with verbose printout of the test-packages that have failed during the last run
* `[output]` - this is an auto-created output directory that contains all the compiled/linked artifacts/object-files/etc that are generated as a result of framework run
    * Unlike other output directories, this one is rather for the internal use of STAT  
* `products` - this directory contains product-level makefiles 
* `shared` - like directory `dummies`, this directory is not mandatory, but strongly advised for keeping the shared test-doubles that are implemented generic enough to serve more then single test-package

>Note that all directory names highlighted with square brackets are of directories auto-created by STAT.

>It is highly recommended to add a directory for the source files of the test-packages, e.g. by name `tests`. Moreover, for more convenient navigation through out this directory it is also recommended to maintain the tree structure close to the one of the code-base.  
>The same should be applied to the contents of directory `shared`.

### 4.1. Files within Instance-Directory

The the instance directory also has the following files:

* `makestat.py` - this is the execution script of STAT-framework
    * See guide for STAT [*command-line options*](./stat_commandline.md)
* `.statignore` - an optional file that similar to `.gitignore` is used to make STAT ignore certain test-package
    * This file might contain file-names and wildcards
* `.statconfig` - an optional file that contains configuration values and directives, see all [*'.statconfig'* options](./statconfig.md)
* `[report.json]` - an automatically generated report describing the latest run of the framework; written in '*json*' format
* `*.mak` - many makefiles, each representing a certain test-package

### 4.2. CFiles within Products-Directory 

The `products` directory in the root of STAT instance is dedicated to contain everything related to the product-level:
*   It contains at least one makefile (i.e.`*.mak`) that configures a specific product
    *   There can be more than single product-level makefile
* `.statignore` - an optional file that similar to `.gitignore` is used to make STAT ignore certain product-level makefiles
    * This file might contain file-names and wildcards
    * This can be used to share configurations between products 
        *   Create a basic product-level `makefile`
        *   Add it to the `.statignore` file
        *   Than create the all the anticipated product-level `makefiles` and make them include the first ignored
        
This directory can be also used to contain header-files and source-files that are intended to compile for all test-packages, i.e. on a product-level. 
