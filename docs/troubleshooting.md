# Troubleshooting

#### Too many open files (EMFILE)

If you see an error that includes the word `EMFILE` it means that netcfgbu
is attempting to open more files than your system is currently allowed.  If you
are on a Unix or MacOS based system, you can observe the maximum allowed open
files using the `ulimit` command, as shown:

```shell script
$ ulimit -a
-t: cpu time (seconds)              unlimited
-f: file size (blocks)              unlimited
-d: data seg size (kbytes)          unlimited
-s: stack size (kbytes)             8192
-c: core file size (blocks)         0
-v: address space (kbytes)          unlimited
-l: locked-in-memory size (kbytes)  unlimited
-u: processes                       1418
-n: file descriptors                256
```

Change the `file descriptors` value to a larger value, for example 4096:

```shell script
$ ulimit -n 4096
``` 

#### Unable to SSH due to mismatch SSH-configs

You may encouter a failure to SSH login/backup a device due to the
fact that the device requires the use of legacy SSH config settings, and modern
SSH implementations are starting to remove weaker algorithms be default.  This
is a typical problem if you are running some older network operating systems that
used an older version of SSH libraries in their products.

To troubleshot these issues used the CLI option `--debug-ssh=2` when running
the login subcommmand.  You will observe the following logging information:

```shell script
2020-06-21 14:11:00,954 DEBUG: [conn=0] Received key exchange request
2020-06-21 14:11:00,954 DEBUG: [conn=0]   Key exchange algs: curve25519-sha256@libssh.org,ecdh-sha2-nistp521,ecdh-sha2-nistp256,ecdh-sha2-nistp384,diffie-hellman-group14-sha1
2020-06-21 14:11:00,954 DEBUG: [conn=0]   Host key algs: rsa-sha2-512,rsa-sha2-256,ssh-rsa,ecdsa-sha2-nistp521,ssh-ed25519
2020-06-21 14:11:00,954 DEBUG: [conn=0]   Client to server:
2020-06-21 14:11:00,954 DEBUG: [conn=0]     Encryption algs: aes256-gcm@openssh.com,aes128-gcm@openssh.com,aes256-ctr,aes192-ctr,aes128-ctr
2020-06-21 14:11:00,954 DEBUG: [conn=0]     MAC algs: hmac-sha2-512-etm@openssh.com,hmac-sha2-256-etm@openssh.com,hmac-sha1-etm@openssh.com,hmac-sha2-512,hmac-sha2-256,hmac-sha1
2020-06-21 14:11:00,954 DEBUG: [conn=0]     Compression algs: none,zlib@openssh.com
2020-06-21 14:11:00,954 DEBUG: [conn=0]   Server to client:
2020-06-21 14:11:00,954 DEBUG: [conn=0]     Encryption algs: aes256-gcm@openssh.com,aes128-gcm@openssh.com,aes256-ctr,aes192-ctr,aes128-ctr
2020-06-21 14:11:00,954 DEBUG: [conn=0]     MAC algs: hmac-sha2-512-etm@openssh.com,hmac-sha2-256-etm@openssh.com,hmac-sha1-etm@openssh.com,hmac-sha2-512,hmac-sha2-256,hmac-sha1
2020-06-21 14:11:00,954 DEBUG: [conn=0]     Compression algs: none,zlib@openssh.com
```

Using the information provded update your configuration file to include the required
exchange settings, either in the global `[ssh_configs]` section or in the `[os_name.$name.ssh_configs] section.
There is an example of such a configuration is the sample [netcfgbu.toml](../netcfgbu.toml).

For addition information refer to the [SSH-config options](config-ssh-options.md) documentation page. 