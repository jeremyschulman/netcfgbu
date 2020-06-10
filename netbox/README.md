# Netbox Integration

As a User of Netbox I want to use the Devices as the inventory for my backup process.  I want to dynamically
create the `netcfgbu` inventory.csv file based on Netbox inventory filters such as site, region, or tags.  I
only want to include devices that are in the "Active" status and have a Primary IP address assigned.

You can find the example Netbox script [netbox_inventory.py](netbox_inventory.py):

```shell script
usage: netbox_inventory.py [-h] [--site SITE] [--region REGION] [--role ROLE] [--exclude-role EXCLUDE_ROLE]
                           [--exclude-tag EXCLUDE_TAG] [--output OUTPUT]

optional arguments:
  -h, --help            show this help message and exit
  --site SITE           limit devices to site
  --region REGION       limit devices to region
  --role ROLE           limit devices with role
  --exclude-role EXCLUDE_ROLE
                        exclude devices with role
  --exclude-tag EXCLUDE_TAG
                        exclude devices with tag
  --output OUTPUT
```

## Setup

#### Environment
To use the `netbox_inventory.py` script you will need to export two environment variables:

**NETBOX_ADDR**<br/>
The URL to your netbox server, for example: "https://netbox.mycorp.com"

**NETBOX_TOKEN**<br/>
The Netbox API token that has read access to the system.

#### Configuration File
    
Ensure your `netcfgbu.toml` file includes an `[inventory]` definition to execute the script to generate 
the inventory.csv file.  

The following example has the script located in /usr/local/bin, will exclude
any device that has a tag "no-backup", and will save the contents to the file
"inventory.csv"

Example:
```toml
[[inventory]]
    name = 'netbox'
    script = "/usr/local/bin/netbox_inventory.py --exclude-tag no-backup --output inventory.csv"
```

## Execution

To build the inventory run the following command:

```shell script
$ netcfgbu inventory build --name netbox
``` 

As output you will see similar:
```shell script
2020-06-09 20:03:35,412 INFO: Executing script: [/usr/local/bin/netbox_inventory.py --exclude-tag no-backup --output inventory.csv]
```

When the build completes you can get a summary of the inventory:

```shell script
$ netcfgbu inventory ls --brief
```

## Limitations

This netbox_inventory.py script is currently written to work with Netbox 2.6,
but a near-term future release will include support for later releases; as
Netbox 2.7 API changed.