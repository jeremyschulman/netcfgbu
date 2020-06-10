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


Example: Select all hosts that use "iosxe" or "nxos" **and** have a name suffix of "mycorp.com"
```shell script
$ netcfgbu backup --limit 'os_name=iosxe|nxos' --limit 'host=.*mycorp.com'
```


## Filter by File Contents
If the filter expression begins with an at-symbol (@), then the contents of the file
are used to filter the inventory.  You can use either CSV files or plain-text files.
In both cases any line that begins with a hash (#) will be ignored.

### CSV Files
When using a CSV file, you must ensure the file extension is `.csv` and that the first
line includes a field-header row with a `host` column. 

### Plain-Text Files
When using a plain-text file the first word on each line will be used as the host value
for filtering purposes.

