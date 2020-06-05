# Configuration File

The netcfgbu tool requires you to setup a TOML configuration file, by default
is called `netcfgbu.toml` and is searched for in the current working directory.
You can override this location using the -C <filepath> option or setting your
environment variable `NETCFGBU_CONFIG`.

(See [example config file](../netcfgbu.toml))

By default, without any OS specific configurations, when you run `netcfgbu
backup` the tool will attempt to login to the devices provided in the inventory
file using the username/password credentials, execute the `show running-config`
command, and save the contents to a file called _$host_.cfg into your current
directory.  For example, if you are using Arista devices `netcfgbu` will work
out of the box without any specific configuration.

Most devices, however, require you to disable paging.  Some devices use different
commands to obtain the running configuration.  `netcfgbu` allows you to map the OS name
values found in your inventory file to OS-name specific configuration sections.  This 
approach allows you full choice and control of commands so that you can easily
add new network OS devices without requiring code changes to `netcfgbu`.

In some cases a device may require a non-standard method for authenticating to
the device, above and beyond the standard SSH connection authentication
process.  In cases such as these the `netcfgbu` package will include additional
SSH connectors that address these use-cases, but do so in a way that is not
specific to any given vendor or product.  See [custom
connectors](custom-connectors.md) for details.

## Defaults

The configuration requires at a mininum the following items, all of which support the use
of environment variables.

**`inventory`**<br/>
File path to the inventory CSV. 

**`credentials.username`**<br/>
The default login user-name

**`credentials.password`**<br/>
The default login password.  You should always use envrionment variables here,
but you are not required to do so.

Example:
```toml
[defaults]
    inventory = "$PROJ_DIR/inventory.csv"
    credentials.username = 'nwkautomaniac'
    credentials.password = "$NETWORK_PASSWORD"
```

## Credentials

The `netcfgbu` tool will attempt to login to each device uses any of the
following credentials **_in this order_**:

   1. Host specific
   2. OS-name specific
   3. Default
   4. Global

One or more credentials can be defined in per OS-name and Global sections. You
can defined multiple credentials using TOML [Array of
Tables](https://github.com/toml-lang/toml#user-content-array-of-tables) syntax.
When multiple credentials are supplied in a given section `netcfgbu` will use
these credentials in the order that they are defined.

**Host specific credentials**<br/>
Must be provided in the inventory file using the `username` and `password` field-columns.
See the [inventory section](inventory.md) for details.

**OS-name specific credentials**<br/>

Example:
```toml
[os_name.asa]
    disable_paging = 'terminal pager 0'

    [[os_name.asa.credentials]]
        username = 'superBadSecOps'
        password = '$SECOPS_PASSWORD'
```

**Default credentials**<br/>
As defined in the `[defaults]` section.

Example:
```toml
[defaults]
    credentials.username = 'nwkautomaniac'
    credentials.password = "$NETWORK_PASSWORD"
```

**Global credentials**<br/>
The `netcfgbu` tool will use these credentials in the order that they 
are defined in the configuration file.

Example:
```toml
[[credentials]]
username = "superadmin"
password = "$ENABLE_PASSWORD"

[[credentials]]
username = "superadmin"
password = "$ENABLE_PASSWORD_1999"
````



## OS Name Specifications
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


## Changing Storage Directory
To change where the configuration files are stored you add the `config_dir`
variable to the defaults section, for example:

```toml
[defaults]
config_dir = "$PROJ_DIR/configs"
```


## Inventory Scripts

You can use `netcfgbu` to invoke a script that is used to extract inventory from
an external system and save it to the required inventory format.  You can define one
or more `[inventory]` sections for this purpose.

Example:
```toml
[[inventory]]
    script = "$PROJ_DIR/netcfgbu/examples/netbox_inventory.py --output inventory.csv"
```
You can find the Netbox code example [here](../examples/netbox_inventory.py).

You invoke the script by:
```shell script
$ netcfgbu inventory build
```

You can define multiple inventory sections and invoke them by name.

Example:
```toml
[[inventory]]
    name = "cmdb"
    script = "/usr/local/bin/cmdb-inventory.py > inventory.csv"

[[inventory]]
    name = "netbox"
    script = "$PROJ_DIR/netcfgbu/examples/netbox_inventory.py --output inventory.csv"
```

```shell script
$ netcfgbu inventory build --name netbox
```

If you do not provide a name `netcfgbu` will use the first configured inventory
section by default.

## Logging

To enable logging you can defined the `[logging]` section in the configuration
file. The format of this section is the standard Python logging module, as
documented [here]( https://docs.python.org/3/library/logging.config.html).

The logger name for `netcfgbu` is "netcfgbu".  

See the [sample netcfgbu.toml](../netcfgbu.toml) for further details.
