# STAT Command-line

Each STAT instance root directory contains a file `makestat.py`. This is the execution script of the STAT framework, see ['Getting Started'](stat_getting_started.md).  
It has quite a few command-line arguments.

```shell
makestat.py [-h] [-c | -run | -vs | -si] [-s | -g [{2-12}]]
            [-p <product> | -a]
            [<mak file> [<mak file> ...]]
```

## positional arguments:

* `<mak file>`           - a list of makefile names/wildcards to process

## optional arguments:

*  `-h`, `--help` -           show help message
*  `-c`, `--compile-only` -   only compile, don not run the executables
*  `-run` -                   a deprecated method, has no impact
*  `-vs`, `--visual-studio` - creates Visual Studio Solution for the makefile
*  `-si`, `--source-insight` -
                        creates Source-Insight project for the
                        makefile; currently only version 4.0 is supported
*  `-s`, `-silent`, `--silent` -
                        set "silent-mode" on, suppresses detailed output on
                        the display
*  `-g [{2-12}]`, `--gear [{2-12}]` - 
                        boost performance with multiprocessing; if specified
                        without a number, it defaults to 11(cores); implicitly
                        sets "silent-mode" on to lower concurrency
*  `-p <product>`, `--product <product>` -
                        run one of the product configurations: 
                        `[<product name> [<product name> ...]]`
*  `-a`, `--all-products` -   run all product configurations
