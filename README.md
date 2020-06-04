![py38](docs/py38.svg)

# Network Configuration Backup

**THIS IS A WORK IN PROGRESS**

As a network engineer I need to backup my network configuration files into a
version control system, and I need a tool to automate this process.  My primary
means of accessing the devices is SSH.

**Primary Considerations**    
* I will have multi-vendor environment. I need to account for the different commands
that are used to obtain the running configuration and disable paging if required.

* I may need to try multiple SSH credendials.  I must not store my passwords in any configuration file,
so this tool must acquire passwords via environment variables.

* I will have a large number of devices (>1000) so I want this tool to take
advantage of any and all techniques that reduce the total amount of time.

* I do not want to write new code if I should introduce a new device type into my network.

# Usage

Once you've installed and setup the configuration file, you can backup all of
our configurations using the command:

```shell script
$ netcfgbu backup
```

You can selectively chose which devices you want from the inventory using the
`--limit` option, for example:

```shell script
$ netcfgbu backup --limit host=switch01
2020-06-04 08:02:22,284 INFO - LOGIN: switch01 (ios) as jeremy.schulman
2020-06-04 08:02:28,084 INFO - CONNECTED: switch01
2020-06-04 08:02:29,792 INFO - GET-CONFIG: switch01
2020-06-04 08:02:30,156 INFO - CLOSED: switch01
2020-06-04 08:02:30,161 INFO - DONE (1/1): switch01 : OK
# ------------------------------------------------------------------------------
Summary: TOTAL=1, OK=1, FAIL=0, ERROR=0
# ------------------------------------------------------------------------------
```

There are a number of other commands provided as shown via `--help`:

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
[TOML](https://github.com/toml-lang/toml) configuration file, by default is
called `netcfgbu.toml` and is searched for in the current working directory. 
You can override this location using the `-C <filepath>` option.

The file MUST contain at least the following:

  * Identifies the location of the inventory file
  * SSH credential(s)
  
## Inventory File

The inventory file is a CSV file that MUST contain at a minimum two columns: `host` and `os_name`, for example:

```csv
host,os_name
switch1,ios
switch2,nxos
fw1,asa
``` 

**NOTE**:  The values of `os_name` are entirely up to you as you will define OS
           specifications in the configuration file.  The `netcfgbu` tool does
           not include any hardcoded OS names.

If your host names cannot be resolved via DNS, then you MUST include the `ipaddr` column, for example:

```csv
host,os_name,ipaddr
switch1,ios,10.1.123.1
switch2,nxos,10.1.123.2
fw1,asa,10.1.123.254
``` 

## Configuration File

The configuration requires at a mininum the following items, all of which support the use
of environment variables.

**`inventory`**<br/>
File path to the inventory CSV. 

**`username`**<br/>
The default login user-name

**`password`**<br/>
The default login password.  You should always use envrionment variables here,
but you are not required to do so.

Example:
```toml
[defaults]
inventory = "$PROJ_DIR/inventory.csv"
username = 'nwkautomaniac'
password = "$NETWORK_PASSWORD"
```

Without any further configuration when you run `netcfgbu backup` the tool will
attempt to login to the devices provided in the inventory file using the
username/password credentials, execute the "show running-config" command, and
save the contents to a file called _$host_.cfg into your current directory.

#### OS Name Specifications
Most devices will require you to disable paging before getting the running
config.  To account for this, you need to define OS specification sections in
the configuration file.  For each `os_name` section you define you can configure
the following variables:  

**`disable_paging`**:<br/>
The command(s) required to disable paging so that when running the command(s) to
obtain the running config the SSH session is not blocked awaiting on a _More_ prompt.

**`get_config`**:<br/>
The command(s) required to obtain the running configuration.

Generally each of these variables is a single command, for example:

```toml
[os_name.ios]
   disable_paging = "terminal length 0"

[os_name.asa]
    disable_paging = 'terminal pager 0'

[os_name.nxos]
    get_config = 'show running-config | no-more'
```

If you need to provide multiple commands, define a list of commands, as described
[TOML Array](https://github.com/toml-lang/toml#user-content-array).

#### Global Credentials
You can define additional credentials to try should the default fail.  You can
defined multiple credentials using the TOML [Array of
Tables](https://github.com/toml-lang/toml#user-content-array-of-tables)
approach.  The `netcfgbu` tool will use these credentials in the order that they 
are defined in the configuration file.

Example:
```toml
[[credentials]]
username = "superadmin"
password = "$ENABLE_PASSWORD"

[[credentials]]
username = "superadmin"
password = "$ENABLE_PASSWORD_1999"
```

#### OS Specific Credentials
You can define one or more credentials within the OS specifications blocks.  If you provide more than
one credential, then they are tried in the order supplied in the configuration file. 

Example:
```toml
[os_name.asa]
    disable_paging = 'terminal pager 0'

    [[os_name.asa.credentials]]
    username = 'superBadSecOps'
    password = '$SECOPS_PASSWORD'
```

#### Changing Storage Directory
To change where the configuration files are stored you add the `config_dir`
variable to the defaults section, for example:

```toml
[defaults]
config_dir = "$PROJ_DIR/configs"
```
