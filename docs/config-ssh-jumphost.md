# Configuration for Use with Jump Hosts

*Added in 0.5.0*

You can configure one or more jump host proxy servers.  Each ``[jumphost]]``
section supports the following fields:

   * `proxy` - Defines the jump host proxy destination.  This string value can
     be in the form "[user@]host[:port]". If `user` is not provided, then `$USER`
     from the environment will be used

   * `include` - A list of [filter](usage-filtering.md) expressions that identify
   which inventory records will be matched to use this jump host

   * `exclude` - *(Optional)* A list of [filter](usage-filtering.md) expressions that identify
   which inventory records will be matched to use this jumphost

   * `timeout` - *(Optional)* A timeout in seconds when connecting to the jump host server.  If
   not provided, will use the default connection timeout value (30s)

Using jump hosts currently requires that you are also using an ssh-agent and have
loaded any ssh-keys so that the `$SSH_AUTH_SOCK` environment variable exists
and running `ssh-add -l` shows that your ssh keys have been loaded for use.

### Examples

For any inventory item that matches the host with a suffix of ".dc1" use the jump server
"dc1-jumpie.com" with login user-name "jeremy"

```toml
[[jumphost]]
    proxy = "jeremy@dc1-jumpie.com"
    include = ['host=.*\.dc1']
```

Exclude any devices that are role equal to "firewall"; this presumes that your
inventory contains a field-column called role.

```toml
[[jumphost]]
    proxy = "jeremy@dc1-jumpie.com"
    include = ['host=.*\.dc1']
    exclude = ['role=firewall']
```

Assuming your inventory has a field-column site, use jump host with IP address
192.168.10.2 for any device with site equal to "datacenter1" or "office1".

```toml
[[jumphost]]
    proxy = "192.168.10.2"
    include = ['site=datacenter1|office1']
```
