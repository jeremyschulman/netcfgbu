# Configuration File

`netcfgbu` requires you to setup a TOML configuration file.  The default
file name is `netcfgbu.toml` and is searched for in the current working directory.
You can override this location using the -C <filepath> option or setting your
environment variable `NETCFGBU_CONFIG`.

(See [example config file](../netcfgbu.toml))

By default, without any OS specific configurations, when you run `netcfgbu
backup` the tool will attempt to login to the devices provided in the inventory
file using username/password credentials, execute the `show running-config`
command, and save the contents to a file called _$host_.cfg into your current
directory.  For example, if you are using Arista EOS or Cisco IOS-XE devices
`netcfgbu` will work out-of-the box without any OS specific configuration.

Most devices, however, require you to disable paging.  Some devices use
different commands to obtain the running configuration.  `netcfgbu` allows you
to map the OS name values found in your inventory file to OS-name specific
configuration sections.  This approach allows you full choice and control of
commands so that you can easily add new network OS devices without requiring
code changes to `netcfgbu`.

## Defaults

All of the default values support the use of environment variables as shown
in the example below.  All of these defaults also support the use
of `NETCFGBU_` environment variables as described [here](environment_variables.md).

**`inventory`**<br/>
File path to the inventory CSV.

**`credentials.username`**<br/>
The default login user-name

**`credentials.password`**<br/>
The default login password.  You should always use environment variables here,
but you are not required to do so.

Example:
```toml
[defaults]
    inventory = "$PROJ_DIR/inventory.csv"
    credentials.username = 'nwkautomaniac'
    credentials.password = "$NETWORK_PASSWORD"
```

## Changing Storage Directory
To change where the configuration files are stored you add the `config_dir`
variable to the defaults section, for example:

```toml
[defaults]
configs_dir = "$PROJ_DIR/configs"
```

## Logging
To enable logging you can defined the `[logging]` section in the configuration
file. The format of this section is the standard Python logging module, as
documented [here]( https://docs.python.org/3/library/logging.config.html).

The logger name for `netcfgbu` is "netcfgbu".
See the [sample netcfgbu.toml](../netcfgbu.toml) for further details.
