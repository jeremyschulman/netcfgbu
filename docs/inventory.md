# Inventory File

The inventory file is a CSV file that MUST contain at a minimum two columns:
`host` and `os_name`, for example:

Example:
```csv
host,os_name
switch1,ios
switch2,nxos
fw1,asa
```

**NOTE**:  The values of `os_name` are entirely up to you as you will define OS
           specifications in the configuration file.  The `netcfgbu` tool does
           not include any hardcoded OS names.

If your host names cannot be resolved via DNS, then you MUST include the `ipaddr` column, for example:

Example:
```csv
host,os_name,ipaddr
switch1,ios,10.1.123.1
switch2,nxos,10.1.123.2
fw1,asa,10.1.123.254
```

If you need to provide host specific credentials, then you can add the columns `username` and `password`.
Both of these columns support the use of environment variables.

Example:
```csv
host,os_name,ipaddr,username,password
switch1,ios,10.1.123.1
switch2,nxos,10.1.123.2
fw1,asa,10.1.123.254,SecOpsAdmin,$SECOPS_PASSWORD
```

You can add any additional columns, and use those column names for filtering purposes.
See [Filtering Usage](usage-filtering.md) for additional information.

