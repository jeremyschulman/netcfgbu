# Motivation for Netcfgbu
I hope to share some of my design goals and considerations for creating
`netcfgbu`.  We are all on this network automation journey, and this is a bit
of story-time-around-the-campfire.  Please enjoy.

### Preface
As the lead network automation software engineer responsible for building and
maintaining tools and systems in support of a multi-vendor network, I need a
reliable and simple to use tool to perform network configuration backups and
store those configurations in a version control systems, in my case Github.  I
looked around the open-source ecosystem for existing tools and found
[Oxidized](https://github.com/ytti/oxidized) as a more modern version of the
legacy [Rancid](https://shrubbery.net/rancid/) system.  I decided against
spending time with Oxidized primarily because it was not written in Python. My
experience with open-source projects is at some point I will need to dig
through the code and either fix issues that I experience in my network or add
features that I need.  I have a very long career developing commercial and
open-source products in many languages, including Perl (Rancid) and Ruby
(Oxidized).  That said, as a member of the network automation community in 2020
I find myself working with Python as the de-facto programming language promoted
and presented as "The Next Thing".

### Guiding Principles
As a member of the network automation community every tool or system that I
build is done with the following two principles in mind.  First and foremost is
to make decisions that will increase reliability so that Users will build trust
and confidence is using the tool.  Second is to make decisions that reduce
operator friction in installing, configuring, and using the tool.  Ideally a
User should be able to install and start using the tool very quickly so they
get that first "Ah ha!" experience with little to no effort.

### Influences
There are many tools that I've used over the years that have influenced the design
and implementation decisions put into `netcfgbu`.  There are many experiences
that I have had working with open-source projects that have been influences.

#### Limit Dependencies
I wanted to build `netcfgbu` with the minimum number of dependencies in terms
of 3rd-party packages.  There are many network device driver libraries out
there, such as [Netmiko](https://github.com/ktbyers/netmiko),
[NAPALM](https://github.com/napalm-automation/napalm), and
[PyATS](https://github.com/CiscoTestAutomation/pyats) to name a few.  These
libraries are great in their own regards and can be used to build very
sophisticated tools.  That said, the `netcfgbu` tool does not need these
libraries to perform the very simple function that it is defined to do.  While
I could have used an amalgamation of these libraries to quickly create
`netcfgbu` it would mean that I would be "dragging along" a lot of dependencies
that I did not need.  My experience with open-source projects is that at
some point you end up in a "dependency Hellscape" sorting out conflicting
package requirements.  As a means to reduce complexity and increase reliability
the `netcfgbu` is built upon a single SSH library, [asyncssh](https://github.com/ronf/asyncssh).

#### Simplifying Constraints
A simplifying constraint is a "rule" that allows you to make an implementation
decision that results in less complex code.  For example, the `netcfgbu` tool
requires that any credential you use **MUST** allow the necessary `get_config`
and `pre_get_config` commands without having to execute any privledge enable
commands.  This simplifying constraint results in the fact that the `netcfgbu`
tool does not need to account for running any privilege mode commands or
dealing with the complexity associated with those mechanisms.

I would further go so far as to submit that as a network automation best-practice
you should create a specific login account to perform the config backup service, for example
"backup-svcadmin", whose command privileges were limited to only those
required by the `get_config` and `pre_get_config` commands to ensure that this
account could do nothing more than perform network backups.

#### Decouple the What from the How
A tool like `netcfgbu` needs to process a list of devices.  This inventory
needs to originate from somewhere whether it is a CSV file or a source of truth
system like Netbox.  In any case a User's inventory system(s) is going to
maintain specific fields for each device record, for example `hostname` or
`name` or `os_family` or `platform` or `management_ipaddr`.  A User could
potentially have multiple "sources of truths" spreadsheets that need to all be
considered for use.  Regardless of the origin format and field names, the
`netcfgbu` tool operates using a simple CSV file system. As a User of `netcfgbu` you are required to create an inventory CSV file based
on your inventory sources and adhere to a few basic field-name requirements, as
described in the [Inventory](inventory.md) docs.  You could create this file by
hand, or you could build it dynamically from a SoT such as Netbox.  As a result
of this decision, the `netcfgbu` provides the subcommand `inventory build` so
that you can run a script that will generate your inventory CSV file on demand
as needed.  This approach was loosely inspired by the concept of the Ansible
dynamic-inventory script mechanisms.

Another very important decoupling decision was made with regard to notion of
"supported network devices."  I wanted to build a tool that did not have a list
of "supported devices".  All devices that adhere to `netcfgbu` design
principles are supported; and you will not need to wait for your device to be
supported. The way this decision was approached was through the use of the
inventory field `os_name`.  `os_name` is used to uniquely identify the device
operating system name (and potentially version). The value that you use in the
field *is completely up to you*.  There is no hard-coded mapping of supported OS
names because `netcfgbu` is not built following a supported OS model design.
For example you can use the value "nxos" or "nexus" or "nx-os" as your
`os_name` for Cisco NX-OS based devices **so long as** you create the necessary
configuration using that same name.

By way of example from the [netcfgbu.toml](../netcfgbu.toml) sample,
the following section says that any inventory item with the `os_name` field equal to "nxos"
will use the command `show running-config | no-more` as the command to obtain
the running configuration file.

```toml
[os_name.nxos]
    get_config = 'show running-config | no-more'
```

But if instead my inventory file used the `os_name` equal to "nexus", then my
configuration file would be:

```toml
[os_name.nexus]
    get_config = 'show running-config | no-more'
```

#### Filtering Choice and Control
One of the features that I really like with Ansible is the `--limit` option
that allows you to target specific devices in your inventory so that you have
fine-grain control over which devices you want to apply the command.  Using
that idea the `netcfgbu` provides both `--limit` and `--exclude` options, as
described in the [Filtering](usage-filtering.md) docs.  These options apply to
any field in your inventory CSV, including any that you define for your own purposes.
For example, the example [netbox_inventory.py](../netbox/netbox_inventory.py) script
will create an inventory CSV file with fields "site", "role", and "region".  As a
result you can then use those fields in your `--limit` and `--exclude` options,
for example:

```shell script
$ netcfgbu login --limit site=dc1 --exclude role=leaf
```

The `netcfgbu` also supports the @<filename> construct again borrowed from
Ansible so that you can filter based on host names present in the file.  The
example of retry-last-failed devices would look like this:

```shell script
$ netcfgbu login --limit @failures.csv
```

#### Troubleshooting
I wanted `netcfgbu` to assist in the troubleshooting processes to determine
that a device SSH port was open (probe) and that the configured credentials
(login) would work.  These two subcommands `probe` and `login` are provided for
such a purpose so that you can determine if there would be any issues prior to
executing the `backup` subcommand.  I found that some of my older network
infrastructure was running code that uses legacy SSH config-options, and I needed
to make adjustments to the [SSH config-options](config-ssh-options.md) to account
for them according.  As such the `netcfgbu` includes a `--debug-ssh=[1-3]` option
that will provide very detailed information about the SSH exchange so you can
determine the root cause of any SSH login failure.

#### Credentials
Once of the more esoteric issues with network login is having to deal with the
potential of having to try different credentials for login.  You may find
yourself at times with devices that, for some reason or another, cannot access
your AAA server and you need to use the "break-glass" locally configured
credential.  Or you may have specific types of devices, for example firewalls,
that use a different set of credentials for access.  The `netcfgbu` tool was
designed so that you can configure many different credentials that will be
attempted in a specific order; see [Credentials](config-credentials.md) for
further details.

#### Speed
Execution speed was a factor in the design decision as applied to the goal
of reducing User friction.  There are automation use-cases that follow
a general pattern:

   step-1: take snapshot of network configs before making changes to network
   step-2: make network config changes
   step-3: validate network is working as expected
   step-4: take snapshot of network configs

And if step-3 should fail we can revert to the configs in step-1.

To design goal for speed to to reduce the amount of time spent in step-1 so
that we can get to the actual work of steps 2 and 3.  Consider the difference
in User experience it would mean if step-1 took 60 minutes vs. 60 seconds.

With that design goal in mind I chose to take advantage of the modern Python 3.8
asyncio features rather than using a traditional threading approach.  I have many
years experience of software experience dealing with multi-threaded applications and
my net-net from all of it is to avoid when possible :-)  Python 3.8 asyncio feature
maturity coupled with the maturity of the asyncssh package allowed me to implement
`netcfgbu` to maximize speed, reduce user friction, and increase reliability by
avoiding threading.

## Fin
I do hope this document sheds some light on my motivations for creating
`netcfgbu`. My purpose in building this tool is in no way to diminish the work
of tools such as Rancid and Oxidized.  If you are using those tools and they
work for you that is great!  We all learn and grow by [standing on the
shoulders of
giants](https://en.wikipedia.org/wiki/Standing_on_the_shoulders_of_giants). If
you are looking for a network backup configuration tool please give `netcfgbu`
a try.  I'm here to help if you get stuck or need any assistance.

Cheers,<br/>
-- Jeremy Schulman<br/>
Twitter: @nwkautomaniac<br/>
Slack: @nwkautomaniac on networktocode.slack.com
