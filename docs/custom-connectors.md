# Custom SSH Connectors

You may encounter network devices that require additional steps beyond the standard login
process.  For example, the Cisco WLC product requires the Username and Password values to be
provided, even after the SSH connection was established using the same credentials.

In such cases the goal of `netcfgbu` is to provide the necessary SSH connector, but in such
a way that it is not specifically tied to a network vendor or OS.  For example there may be
other network devices that behave the same way as the WLC, and you could use the same connector
for the WLC and this other device type.

To use a custom connector type you can add the `connection` value in
the OS section of your [configuration file](configuration-file.md).  

Example for Cisco WLC:
```toml
[os_name.aireos]
    show_running = "show run-config commands"
    disable_paging = "config paging disable"
    connection = "netcfgbu.connectors.ssh.LoginPromptUserPass"
```

The `connection` value identifies the python module location where this
connector can be found. In the above example, you can find
[LoginPromptUserPass here](../netcfgbu/connectors/ssh.py). This approach
allows you to use a connector that is either packaged with `netcfgbu` or use
one that can be found in another python package should that be necessary.

If you have a need for a custom connector and would like it written for you,
please [open an issue](https://github.com/jeremyschulman/netcfgbu/issues).