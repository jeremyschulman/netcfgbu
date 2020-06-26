# SSH Config Options
You may need to provide SSH configuration options such as Key Exchange or
Cipher options.  The `netcfgbu` tool uses [AsyncSSH](https://github.com/ronf/asyncssh) as an underlying transport.
You can provide any SSH Configuration option supported by AsyncSSH either at
the global level or at the OS-spec level.

For example at the global level:
```toml
[ssh_configs]
   kex_algs = ["ecdh-sha2-nistp256", "diffie-hellman-group14-sha1"]
   encryption_algs = [
      "aes128-cbc,3des-cbc",
      "aes192-cbc,aes256-cbc",
      "aes256-ctr,aes192-ctr",
      "aes128-ctr"]
```

Or at an OS-spec level:
```toml
[os_name.aireos]
   ssh_configs.kex_algs =  ["ecdh-sha2-nistp256", "diffie-hellman-group14-sha1"]
   ssh_configs.encryption_algs = ["aes128-cbc,3des-cbc"]
```

If both global and OS-spec SSH configuration options are provided the OS-spec
option will be used; i.e. overrides the specific option if it was present
in the global options.

For details on the specific SSH options, refer to the AsyncSSH option names, [here](https://asyncssh.readthedocs.io/en/stable/api.html#asyncssh.SSHClientConnectionOptions)
and supported option values, [here](https://asyncssh.readthedocs.io/en/stable/api.html#supported-algorithms).

*NOTE: A future version of AsyncSSH will support the use of ssh_config file(s)*