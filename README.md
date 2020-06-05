![py38](docs/py38.svg) 

![version](docs/version.svg)

# Network Configuration Backup

As a network engineer I need to backup my network configuration files into a
version control system, and I need a tool to automate this process.  My primary
means of accessing the devices is SSH.

**Primary Considerations**    
* I will have multi-vendor environment. I need to account for the different commands
that are used to obtain the running configuration and disable paging if required.

* I want to provide my network inventory in a simple CSV format.  I want to pull
content dynamically from one or more sources, for example Netbox.  I want the
ability to filter this inventory to include and exclude items based.

* I may need to try multiple SSH credendials.  I must not store my passwords in any configuration file,
so this tool must acquire passwords via environment variables.

* I will have a large number of devices (>1000) so I want this tool to take
advantage of any and all techniques that reduce the total amount of time.


The general approach to `netcfgbu` is a configuration based methodology so as
to not hardcoded the tool to work with specific network OS type device drivers,
so that it avoids the complexity and dependency of including an array of
3rd-party libraries specific to network devices.  See the
[configuration](docs/configuration-file.md) for details.

Document [starts here](docs/TOC.md).


# Introduction

Once you've setup the [configuration](docs/configuration-file.md) file and
[inventory](docs/inventory.md) file you can backup all of our configurations using
the command:

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
  inventory  [ls, build, ...]
  login      Verify SSH login to devices.
  probe      Probe device for SSH reachablility.
```

# Setup

The `netcfgbu` tool requires you to setup a
[TOML](https://github.com/toml-lang/toml)
[configuration](docs/configuration-file.md) file, by default is called
`netcfgbu.toml` and is searched for in the current working directory. You can
override this location using the `-C <filepath>` option.

At a minimum you need to designate the [inventory](docs/inventory.md) file and
a default set of SSH login credentials.  The network device configs will be
stored in the current working directory, or as specified in the `configs_dir`
option.  The configuration-file supports the use of enviornment variables.

Example:
```toml
[defaults]
    inventory = "$PROJ_DIR/inventory.csv"
    configs_dir = "$PROJ_DIR/configs"
    credentials.username = "$NETWORK_USERNAME"
    credentials.password = "$NETWORK_PASSWORD"
```

### System Requirements and Installation

This tool requires the use of Python3.8.  You will need to git-clone this repository
and run `python setup.py` to install it into your environment.

### Questions or Suggestions?

Please open a github issue if you have any questions or suggestions.

Thank you!