[![Python 3.8](https://img.shields.io/badge/python-3.8-blue.svg)](https://www.python.org/downloads/release/python-380/)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

![version](docs/version.svg)

# Network Configuration Backup

As a network engineer I need to backup my network configuration files into a
version control system, and I need a tool to automate this process.  My primary
means of accessing the devices is SSH.

**Supported Devices**<br/>
The `netcfgbu` tool was built specifically to backup network operating system (NOS)
configurations that are monolithic in nature.  That is to say the entire
configuration can be captured using a command such as "show running-config".  Any
NOS that provides a monolithic configuration should be supported by `netcfgbu`.

**Primary Considerations**
* I have a multi-vendor environment. I need to account for the different commands
that are used to obtain the running configuration and disable paging if
required.

* I want to provide my network inventory in a simple CSV format.  I want to
create this inventory dynamically from one or more sources, for example Netbox.
I want the ability to filter this inventory with limit and exclude constraints.

* I may need to try multiple SSH credentials.  I must not store my passwords in
any configuration file, so this tool must acquire passwords via environment
variables.

* I will have a large number of devices (>1000) so I want this tool to take
advantage of any and all techniques that reduce the total amount of time.

---


The general approach to `netcfgbu` is a configuration based methodology so as
to not hardcode the tool to work with specific network device drivers
and avoid the complexity and dependency of including a collection of 3rd-party
libraries specific to network devices.

Read the Documenttion [here](docs/TOC.md).<br/>
Read the Quick Start [here](docs/QuickStart.md)<br/>
[Example netcfgbu.toml configuration](netcfgbu.toml)<br/>

# Introduction

Once you've setup the [configuration](docs/configuration-file.md) file and
[inventory](docs/inventory.md) file you can backup all of your configurations
using the command:

```shell script
$ netcfgbu backup
```

At the end of the run, you will see a report, for example:

```shell script
# ------------------------------------------------------------------------------
Summary: TOTAL=1482, OK=1482, FAIL=0
         START=2020-Jun-05 01:48:55 PM, STOP=2020-Jun-05 01:50:08 PM
         DURATION=72.566s
# ------------------------------------------------------------------------------
```

There are a number of other [commands](docs/commands.md) provided as shown via `--help`:

```text
Usage: netcfgbu [OPTIONS] COMMAND [ARGS]...

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:
  backup     Backup network configurations.
  inventory  Inventory subcommands.
  login      Verify SSH login to devices.
  probe      Probe device for SSH reachablility.
  vcs        Version Control System subcommands.
```

# Setup

The `netcfgbu` tool does not require you to create a configuration file, but
for practical purposes you will generally need one.  The file is
[TOML](https://github.com/toml-lang/toml) format.  The default file is
`netcfgbu.toml` and `netcfgbu` searches for in the current working directory.
You can override this location using the `-C <filepath>` option or using the
environment variable `NETCFGBU_CONFIG`

At a minimum you need to designate the [inventory](docs/inventory.md) CSV file and
a default set of SSH login credentials.  The network device configs will be
stored in the current working directory, or as specified in the `defaults.configs_dir`
option.  The configuration-file supports the use of environment variables.

Example:
```toml
[defaults]
    inventory = "$PROJ_DIR/inventory.csv"
    configs_dir = "$PROJ_DIR/configs"
    credentials.username = "$NETWORK_USERNAME"
    credentials.password = "$NETWORK_PASSWORD"
```

The `netcfgbu` defines the use of specific [Environment Variables](docs/environment_variables.md).  Their
use is the equivalent of the following configuration file.  That is to say, if you did not provide `netcfgbu` a
configuration file, this would be used:

```toml
[defaults]
    inventory = "$NETCFBU_INVENTORY"
    configs_dir = "$NETCFGBU_CONFIGSDIR"
    credentials.username = "$NETCFGBU_DEFAULT_USERNAME"
    credentials.password = "$NETCFGBU_DEFAULT_PASSWORD"
```

### System Requirements and Installation

This tool requires the use of Python3.8.<br/>
Installation available via PyPI:

```shell script
$ pip install netcfgbu
```

### Questions or Suggestions?

Please open a github issue if you have any questions or suggestions.

Thank you!