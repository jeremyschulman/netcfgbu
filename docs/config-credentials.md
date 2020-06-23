# Credentials

The `netcfgbu` tool requires that any credentials you use will have the
necessary priveledge to execute any of the `pre_get_config` and `get_config`
commands without having to change the priveldge level.  The `netcfgbu` tool
does not support the capabilty of changing priveldge levels.

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
