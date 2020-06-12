# Inventory Integration
You can use `netcfgbu` to invoke a script that is used to extract inventory from
an external system and save it to the required inventory format.  You can define one
or more `[inventory]` sections for this purpose.

Example:
```toml
[[inventory]]
    script = "$PROJ_DIR/netcfgbu/examples/netbox_inventory.py --output inventory.csv"
```
You can find the Netbox code example [here](../examples/netbox_inventory.py).

You invoke the script by:
```shell script
$ netcfgbu inventory build
```

You can define multiple inventory sections and invoke them by name.

Example:
```toml
[[inventory]]
    name = "cmdb"
    script = "/usr/local/bin/cmdb-inventory.py > inventory.csv"

[[inventory]]
    name = "netbox"
    script = "$PROJ_DIR/netcfgbu/examples/netbox_inventory.py --output inventory.csv"
```

```shell script
$ netcfgbu inventory build --name netbox
```

If you do not provide a name `netcfgbu` will use the first configured inventory
section by default.
