ssh-tarpit
==========

SSH tarpit that slowly sends an endless banner. [Original idea by Chris Wellons](https://nullprogram.com/blog/2019/03/22/). This is Python 3 implementation focused on safety and correctness.

## Requirements

* Python 3.5.3+

## Installation


### From PyPI

Standard Python package installation. This package is available on PyPI:

```
pip3 install ssh-tarpit
```

### From source

Run within source directory:

```
pip3 install .
```

### Docker

Run:

```
docker run -d \
    --security-opt no-new-privileges \
    -p 22:2222 \
    --restart unless-stopped \
    --name ssh-tarpit \
    yarmak/ssh-tarpit
```

## Usage

Synopsis:

```
$ ssh-tarpit --help
usage: ssh-tarpit [-h] [--disable-uvloop] [-v {debug,info,warn,error,fatal}]
                  [-i INTERVAL] [-f [LOGFILE [LOGFILE ...]]] [-a BIND_ADDRESS]
                  [-p BIND_PORT] [-D]

SSH tarpit that slowly sends an endless banner

optional arguments:
  -h, --help            show this help message and exit
  --disable-uvloop      do not use uvloop even if it is available (default:
                        False)
  -v {debug,info,warn,error,fatal}, --verbosity {debug,info,warn,error,fatal}
                        logging verbosity (default: info)
  -i INTERVAL, --interval INTERVAL
                        interval between writes in seconds (default: 2.0)
  -f [LOGFILE [LOGFILE ...]], --logfile [LOGFILE [LOGFILE ...]]
                        file(s) to log to. Empty string argument represents
                        stderr. Flag without arguments disables logging
                        completely. Default is stderr only. (default: [''])

listen options:
  -a BIND_ADDRESS, --bind-address BIND_ADDRESS
                        bind address (default: 127.0.0.1)
  -p BIND_PORT, --bind-port BIND_PORT
                        bind port (default: 2222)
  -D, --dualstack       force dualstack socket mode. Sets socket IPV6_V6ONLY
                        option to 0 (default: False)

```
