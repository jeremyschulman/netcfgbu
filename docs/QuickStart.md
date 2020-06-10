# Quick Start

If you are a Netbox user you can dynamically build the inventory.csv file as
described [here](../netbox/README.md).

You can use the provided configuration file [netcfgbu.toml](../netcfgbu.toml) as
a starting point and customize it as necessary.  See [Configuration](configuration-file.md)
for details.

If you want to run a probe test to verify SSH access to all your devices
you can run:

```shell script
$ netcfgbu probe
``` 

When the command completes you will see a report similar:
```shell script
# ------------------------------------------------------------------------------
Summary: TOTAL=1463, OK=1463, FAIL=0
         START=2020-Jun-09 08:09:52 PM, STOP=2020-Jun-09 08:09:53 PM
         DURATION=0.358s
# ------------------------------------------------------------------------------
```

If you want to run a login test to verify that your configured credentials
are working you can run:

```shell script
$ netcfgbu login
```

When the command completes you will see a report similar:
```shell script
# ------------------------------------------------------------------------------
Summary: TOTAL=1463, OK=1462, FAIL=1
         START=2020-Jun-09 08:10:40 PM, STOP=2020-Jun-09 08:11:52 PM
         DURATION=71.797s


FAILURES: 1
host               os_name    reason
-----------------  ---------  -------------------------------
switch01           iosxe      ConnectionLost: Connection lost
# ------------------------------------------------------------------------------
```

Any errors will be logged to a file called `failures.csv`, which you can then
use to exclude on future commands.

When you want to run a backup of your configs you can run:

```shell script
$ netcfgbu backup
```

Or to exclude any devices that failed the login test:

```shell script
$ netcfgbu backup --exclude @failures.csv
````

When the backup completes you will see a report similar:

```shell script
# ------------------------------------------------------------------------------
Summary: TOTAL=1462, OK=1462, FAIL=0
         START=2020-Jun-09 08:14:36 PM, STOP=2020-Jun-09 08:18:29 PM
         DURATION=80.672s
# ------------------------------------------------------------------------------
```
