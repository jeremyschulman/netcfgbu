# Release Notes

#### v0.5.0
   * BREAKING Change: removed support of non-CSV files for filtering "@<file>".  Only
   CSV files are currently supported.
   * Addes support for SSH jumphost proxy, see [Using Jumphosts](docs/config-ssh-jumphost.md)
   * Added CI/CD tooling - tox & friends, github actions, pre-commit
   * Added unit-test coverage for full infrastructure components; that is
   everything but the CLI.

#### v0.4.0 (2020-Jun-21)
   * BREAKING Change `[[github]]` to `[[git]]` in `netcfgby.toml`
   * BREAKING Change subcommand `inventory ls` to `inventory list`
   * Added unit-test coverage for configuration file use-cases
   * Added Troubleshooting documentation

#### v0.3.1 (2020-Jun-17)
   * Bugfix resulting in missing `os_name` config

#### v0.3.0 (2020-Jun-12)
   * Add support for Github version control system
   * Add config file validation
   * Add support for user-defined inventory columns
   * Enhanced netbox integration script to work with >= version 2.7

#### v0.2.0 (2020-Jun-09)
   * Add Quick-Start docs
   * Add Netbox Integration docs
   * Add --inventory, -i options for inventory file
   * Add NETCFGBU environment variables
   * Add --debug-ssh for debugging
   * Add support for SSH-config options
   * Add config-file validation
   * Refactored config-file options

#### v0.1.0 (2020-Jun-05)
Minimum viable package features that will backup configuration files from
network devices and store the contents onto your server.

This version does not support the following features:
   * Version Control System (VCS) integration with github
   * Removing config content that would result in false-positive changes

These features will be included in the next release.