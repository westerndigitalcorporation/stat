# STAT Command-line

***synopsis***

```shell
makestat.py [-h] [-r | -b | -vc | -vs | -si] [-c] [-s | -g [{2-12}]]
            [-p <product> | -a]
            [<mak file> [<mak file> ...]]
```

***description***

A root directory of each STAT instantiation within the codebase shall have file `makestat.py`, see ['Getting Started'](stat_getting_started.md) for details. This is the central script of the STAT framework. It shall be called for every request that can be served by the framework. The operability of the script is carried out with the help of different command-line arguments.

***positional arguments:***

- `<mak file>` - a list of makefile names/wildcards to process

***optional arguments:***

- `-h`, `--help` - show help message
- `-r`, `--run` - (default) compile and execute test-packages
  - implicitly assumed upon no other user-choice
- `-b`, `--build-only` - only compile, don not run the test-package executables
- `-vc`, `--vs-code`        - creates VS-Code Workspace for the makefile
- `-vs`, `--visual-studio`  - creates Visual Studio Solution for the makefile
- `-si`, `--source-insight` - creates Source-Insight project for the makefile
  - currently only version 4.xx is supported
- `-c`, `--clean-build` - increase level of cleaning efforts preceding the build:
  - [_not specified_] = incremental build, i.e no preceding cleaning
  - `-c` = rebuild the target by just overwriting the artifact of previous build
- `-cc` = clear the artifacts of previous build and rebuild the target from scratch
- `-s`, `-silent`, `--silent` - set "silent-mode" on
  - suppresses detailed output on the display
- `-g [{2-<n>}]`, `--gear [{2-<n>}]` - boost performance with multiprocessing
  - if specified without a number, it defaults to `<n>`,
      where `(n+1)` is a number of available CPU cores
  - implicitly sets "silent-mode" on to lower concurrency
- `-p <product>`, `--product <product>` - run one of the product configurations:
  - `[<product name> [<product name> ...]]`
- `-a`, `--all-products` -   run all product configurations

## Usage Examples

### Basic Command-line

The simplest command-line is the one without any arguments:  

```bash
makestat.py
```

This command-line is equivalent to calling the script with the argument `-r`. This option commands STAT-framework to compile, to link and to execute every single test-package. However, it excludes the makefiles that are mentioned within the `.statignore` file.

### Running Specific Test-Packages

For a specific test-package one shall mention it explicitly in the command-line:

```bash
makestat.py example_test_package.mak
```

Several test-packages and even wildcards are supported too:

```bash
makestat.py basic*.* example.mak *simple*.*
```

### Compiling only

The framework can be launched only to build test-packages without execution:

```bash
makestat.py my_tests.mak some_tests.mak -b
```

Adding an argument `-b` tells the framework only to compile and to link the executables without executing them. This option can be used with any amount of makefiles. If it is given with no makefiles specified, the framework compiles all makefiles (excluding those referred by `.statignore`)

### Multiple Products/Configurations

STAT supports several configurations at product level (see ['Getting Started'](stat_getting_started.md)). When [basic command-line](#basic-command-line) is issued first time the framework runs the test-packages several times, once for each product configuration. All subsequent calls of this command-line will run each package only once using the last product-configuration *by default*.  

The framework allows explicit request to run over all product-configurations:

```bash
makestat.py -a
```

Argument `-a` in the command-line commands the framework to run the given test-packages once per each product-configuration.

The user may change the default product-configuration at any time:

```bash
makestat.py -p some_config
```

One needs to add an argument `-p` followed by the name of the desired product configuration. It tells the framework to run for this product configuration, and also to make it the *default configuration* for the subsequent calls until one of the arguments `-a` and `-p` is specified in the command-line again.

### Parallelism Gear

The framework allows better utilization of CPU-power for better performance:

```bash
makestat.py -g 4
```

This command-line tells framework to use 4 cores of the CPU to boost performance by multi-processing.

Specifying the explicit amount of cores to be used is not mandatory:

```bash
makestat.py my*.* -
```

When `-g` argument is specified without an explicit amount of cores, the framework sets this number according to the maximal amount of cores of the given CPU. By default, STAT attempts to configure gear with parallelism of `(C-1)`, where `C` is the total amount of cores of the given CPU.

> Note that setup of several processes also takes time. Therefore, using `-g` option is beneficial when there is a considerable amount of test-packages to run, when the execution time of these test-packages in overall out-weighs the time penalty of a multi-processing setup.

### IDE-Project Generation

For debugging purposes, STAT framework provides means to generate Visual-Studio solution for any test-package:

```bash
makestat.py my_package.mak -vs
```

This command-line results in generation of a valid Visual-Studio solution for the specified test-package ("my_package" in this example). The solution is generated to the `./ide` directory.

The framework also supports project-generation for Source-Insight IDE (version 4.xx):

```bash
makestat.py may_package.mak -si
```

While Source-Insight is a very powerful tool to write the new code and to navigate through the depth of the existing code, it has no integrated debugger-functionality. When TDD methodology is used properly, debugging functions are rarely used. Runtime feedback printed either to standard output or written to a log-file (look inside the `./logs` directory) is usually sufficient for the identification of the failure-reason. Moreover, Visual Studio project can be used for those rare occasions when step-by-step debugging is unavoidable.

On Linux platform the framework supports generation fo VS-Code workspace:

```bash
makestat.py my_package.mak -vc
```

This command-line results in generation of a valid Visual-Studio Code workspace file for the specified test-package ("my_package" in this example). The `*.workspace` file is generated into the `./ide` directory.

> The command-line that generates IDE-Project assumes only single test-package. For several test-packages, one shall call the command-line for each one separately.

### Clean Build

The framework by default performs build in an incremental mode. One can force makestat to rebuild the target:

```bash
makestat.py some_tests.mak -c
```

The command-line argument `-c` tells STAT that all the sources have to be recompiled over the existing ones and to re-link the executable again. The user may also request the framework also to erase first all the artifacts and the executable first, and only then rebuild it from the scratch by specifying `-c` argument twice:

```bash
makestat.py some_tests.mak
```

> Note that duplicated `-c` argument can be declared in several ways: "`-cc`" (as in the example above), "`-c -c`" or even "`--clean-build --clean-build`".
