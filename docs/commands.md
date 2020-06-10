# Commands

This page presents an overview of the `netcfgbu` commands.  For full command details use the 
CLI `--help` option.

For any devices that fail during a command, the `netcfgbu` tool will generate a
file called `failures.csv` You can use this file in future command to retry
using the `--limit @failures.csv`.  Or you can use this file to exclude these
devices using `--exlcude @failures.csv`.  For more details see
[filtering](filtering.md)

**inventory**<br/>
The `inventory ls` command is used to list the contents of the current inventory file.  This
is useful for when you want to test your filtering expressions before you try to run a backup.

Example:
```shell script
$ netcfgbu inventory ls --limit os_name=eos --brief
```

The `inventory build` command is used to invoke your inventory script that will create the inventory
file.

Example:
```shell script
$ netcfgbu inventory build --name netbox
```

**probe**<br/>
The `probe` command is used to determine if the SSH port is available on the target device.  This
is a useful first step before attempting to run a backup.  This probe does **not** attempt to
login / authenticate with SSH. 

```shell script
$ netcfgbu probe
```  

**login**<br/>
The `login` command is used to determine if the `netcfgbu` is able to authenticate with the
device SSH, and reports the credential username value that was used.  This is useful to
ensure that not only is the device reachable with SSH open, but the that `netcfgbu` is configured
with the correct credentials to allow a connection.

```shell script
$ netcfgbu probe
```  

**backup**<br/>
This `backup` command is used to login to the device via SSH, extract the
running configuration, and save it to a file called $host.cfg, where $host is
the value defined in the inventory item.  For example if an inventory item has
a host value of "myswitch1", then the file "myswitch1.cfg" is created upon
successful backup.  The backup files are stored in either the current working
directory, or the directory designated by the `config_dir` value in the
[configuration file](configuration-file.md#Changing-Storage-Directory)