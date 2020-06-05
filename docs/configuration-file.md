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

The `netcfgbu` tool will attempt to login to each device using any of the
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
Host specific credentials must be provided in the inventory file using the
`username` and `password` field-columns. See the [inventory
section](inventory.md) for details.

**OS-name specific credentials**<br/>


Example:
```toml
[os_name.asa]
    disable_paging = 'terminal pager 0'

    [[os_name.asa.credentials]]
        username = 'superBadSecOps'
        password = '$SECOPS_PASSWORD'
```

NOTE: The indentation here is only for human-eyeballs.  If you were to add a
variable after the credentials section it would **not** be part of the
`[os_name.asa]` section, but rather a new global variable.


**Default credentials**<br/>

Defined in the `[defaults]` section.

Example:
```toml
[defaults]
    credentials.username = 'nwkautomaniac'
    credentials.password = "$NETWORK_PASSWORD"
```

**Global credentials**<br/>
`netcfgbu` will use these credentials in the order that they are defined in the
configuration file.

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
config.  To account for this, you need to define OS specification sections. For
each `[os_name.$name]` section you can configure the following variables:

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

## Custom Connections
In some cases an OS may require a non-standard process to login to the device
above and beyond the standard SSH connection authentication process.  In such
cases you can configure the use of a custom connector. The `netcfgbu` package
will include additional SSH connectors to address these use-cases, but do so in
a way that is not specific to any given vendor or product.

The Cisco WLC AirEOS for example requires the username and password to be
provided in the CLI, even after establishing an SSH connection via standard
authentication.  The OS specific configuration for WLC would be:

Example:
```toml
[os_name.aireos]
    show_running = "show run-config commands"
    disable_paging = "config paging disable"
    connection = "netcfgbu.connectors.ssh.LoginPromptUserPass"
```

For more details see [custom connector](custom-connectors.md).

## Logging

To enable logging you can defined the `[logging]` section in the configuration
file. The format of this section is the standard Python logging module, as
documented [here]( https://docs.python.org/3/library/logging.config.html).

The logger name for `netcfgbu` is "netcfgbu".  

See the [sample netcfgbu.toml](../netcfgbu.toml) for further details.
