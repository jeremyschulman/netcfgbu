# Filtering Inventory

This page describes how you can filter the inventory file so that only the
desired items are used in the execution of a command.  There are two methods
for filtering records: by field-name(s) and by file-contents.

Use the `--limit` option to include only those items that match on the filter criteria.
Use the `--exclude` option to exclude inventory items based on the filter criteria.

You can provide multiple filter options on the command-line to mix and match how you
want to filter the inventory.

## Filter by Field Names

You can filter using the inventory field names: `host` and `os_name`.  The
filter values are [regular expressions](https://regex101.com/).

Example: Select a single host called myswitch1

```shell script
$ netcfgbu backup --limit host=myswitch1
```

Example: Select all hosts that use "iosxe" or "nxos" as the network os_name:
```shell script
$ netcfgbu backup --limit 'os_name=iosxe|nxos'
```

Example: Select all hosts that do _not_ "iosxe" or "nxos" as the network os_name:
```shell script
$ netcfgbu backup --exclude 'os_name=iosxe|nxos'
```

Example: Select all hosts that use "iosxe" or "nxos" **and** have a name suffix of "mycorp.com"
```shell script
$ netcfgbu backup --limit 'os_name=iosxe|nxos' --limit 'host=.*mycorp.com'
```

Example: Select a host with a specific IP addresses:
```shell script
$ netcfgbu backup --limit "ipaddr=10.0.20.10"
```

Example: Select all hosts with IP addresses in a given prefix:
```shell script
$ netcfgbu backup --limit "ipaddr=2620:10:abcd::/64"
```

Example: Select all hosts with IP addresses that match a regex:
```shell script
$ netcfgbu backup --limit "ipaddr=10.(10|30).5.\d+"
```




## Filter by CSV File Contents
If the filter expression begins with an at-symbol (@), then the contents of the
file are used to filter the inventory.  Any line that begins with a hash (#)
will be ignored.  The CSV file must contain the `host` column-field.

Example:
```shell script
$ netcfgbu backup --exclude @failures.csv
```
