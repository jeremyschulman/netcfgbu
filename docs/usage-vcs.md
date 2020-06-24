# Using VCS Git Subcommands

When you are using a Git Version Control System to store your configuration files you can use the
`netcfgbu vcs` subcommands.  Before using these commands ensure you have
setup your configuration file as described [here](config-vcs-git.md).

Each of the vcs subcommands support the `--name` option if your configuration
file contains more than one `[[git]]` section.

## Preparing Your Configs Directory

As a one-time initial step you will need to run the `prepare` subcommand so that the
directory used for config backups (`configs_dir`) is initialized for use with your chosen platform.

This command will run the necessary command to initialize the directory for
git usage and fetch the current git repository files.

```shell script
$ netcfgbu vcs prepare
```

If you have more than one `[[git]]` configuraiton section defined, you can
use the `--name` option.

For example, if you have a configuraiton with `name = "firewalls"` defined you
would run:

```shell script
$ netcfgbu vcs prepare --name firewalls
```

## Saving to Git

Once you have completed the backup process and you want to store your changes
into the git repository you run the `save` command.  By default `netcfgbu`
will create a git tag (release) based on the current timestamp in the format
`<year><month-number><day-number>_<hour24><minute><seconds>`.  For example, if
you run the `save` command on June 12, 2020 at 1:35p the tag release name would
be `20200612_133500`.  If want to explicitly set the tag-release name use the
`--tag-name` option.

---

:warning: If there are no actual changes to the files in `configs_dir`
then the `save` command will not make any updates to git.

---


### Examples:

Save using the first `[[git]]` configuration and the default tag-name

```shell script
$ netcfgbu vcs save
```

Save the configs using the tag-name "pre-change-ticket12345"

```shell script
$ netcfgbu vcs save --tag-name pre-change-ticket12345
```

Save using the git configuraiton named "firewalls"

```shell script
$ netcfgbu vcs save --name firewalls
```

## Checking the Status of Changes before You Save

If after running your backup process you want to see the status of changes that
would be made to your git platform you can run the `status` command. The output of this
command is the same as if you ran `git status` in the `configs_dir`.

Example when no changes / differences in `configs_dir`:
```shell script
$ netcfgbu vcs status
2020-06-12 11:32:22,722 INFO:
VCS diffs git: https://github.mycorp.com/jschulman/test-network-configs.git
             dir: /home/jschulman/Projects/NetworkBackup/configs

On branch master
nothing to commit, working tree clean
```

Example when changes in `configs_dir`
```shell script
$ netcfgbu vcs status
2020-06-12 11:34:27,786 INFO:
VCS diffs git: https://github.mycorp.com/jschulman/test-network-configs.git
             dir: /home/jschulman/Projects/NetworkBackup/configs

On branch master
Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
	modified:   switch01.cfg
	modified:   switch02.cfg

no changes added to commit (use "git add" and/or "git commit -a")
```