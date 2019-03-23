ssh-tarpit
==========

SSH tarpit that slowly sends an endless banner. [Original idea by Chris Wellons](https://nullprogram.com/blog/2019/03/22/). This is Python 3 implementation focused on safety and correctness. Project is now in "work in progress" stage.

## Requirements

* Python 3.5.3+

## Installation

Standard Python package installation. This package is available on PyPI:

```
pip3 install ssh-tarpit
```

## Usage

Synopsis:

```
$ ssh-tarpit --help
usage: ssh-tarpit [-h] [-v {debug,info,warn,error,fatal}] [-i INTERVAL]
                  [-a BIND_ADDRESS] [-p BIND_PORT] [-D]

SSH tarpit that slowly sends an endless banner

optional arguments:
  -h, --help            show this help message and exit
  -v {debug,info,warn,error,fatal}, --verbosity {debug,info,warn,error,fatal}
                        logging verbosity (default: info)
  -i INTERVAL, --interval INTERVAL
                        interval between writes in seconds (default: 2.0)

listen options:
  -a BIND_ADDRESS, --bind-address BIND_ADDRESS
                        bind address (default: 127.0.0.1)
  -p BIND_PORT, --bind-port BIND_PORT
                        bind port (default: 2222)
  -D, --dualstack       force dualstack socket mode. Sets socket IPV6_V6ONLY
                        option to 0 (default: False)

```
