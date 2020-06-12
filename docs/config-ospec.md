## OS Specifications
Most devices will require you to disable paging before getting the running
config.  To account for this, you need to define OS specification sections. For
each `[os_name.$name]` section you can configure the following variables:

**`pre_get_config`**:<br/>
The command(s) required to disable paging so that when running the command(s) to
obtain the running config the SSH session is not blocked awaiting on a _More_ prompt.

**`get_config`**:<br/>
The command(s) required to obtain the running configuration.

***`timeout`***<br/>
The time in seconds to await the collection of the configuration before
declaring a timeout error.  Default is 60 seconds.

***`linter`***<br/>
Identifies the Linter specification to apply to the configuration once it
has been retrieved.  See [Linters](#Linters) in next section.

Examples:
```toml
[os_name.ios]
   pre_get_config = "terminal length 0"
   linter = "ios"

[os_name.asa]
    timeout = 120
    pre_get_config = 'terminal pager 0'

[os_name.nxos]
    get_config = 'show running-config | no-more'
```

If you need to provide multiple commands, define a list of commands, as described
[TOML Array](https://github.com/toml-lang/toml#user-content-array).

## Linters
Linters post-process the configuration once it has been retrieved from the device.
At present there are two variables you can define:

**config_starts_after**<br/>
A regular-expression or value that designates the line before
the configuration file contents.  Different operating systems have a
different "starting line", for example:

```toml
[linters.iosxr]
    config_starts_after = 'Building configuration'

[linters.ios]
    config_starts_after = 'Current configuration'
```

**config_ends_at**<br/>
You can configure this value to identify a line of text that marks the end of
the configuration.

For example for Palto Alto systems the ommand to get the configuration is
`show` from within the OS configure mode.  When that command completes the next
prompt is `[edit]`; so we use this value to indicate the end of the
configuration.

```toml
[linters.panos]
    config_ends_at = "[edit]"
```