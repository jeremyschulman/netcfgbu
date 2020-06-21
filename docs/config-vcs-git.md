# Git VCS Configuration
When you want to store your configuration files in a git based version control system you
will need to define at least one `[[git]]` section in your configuration file.
 You must use one of the following git authentication methods:

  * Git Token
  * Git SSH deployment key without passphrase
  * Git SSH deployment key with passphrase

___
 
:question: If you are not certain which method you want to use, refer to the document
links in the [References](#References) below.

___


You can define more than one `[[git]]` section in your configuration file
so that you can use different repositories or credential methods.

For inforamtion on using the `netcfgbu vcs` subcommands, see [Using VCS
Subcommands](usage-vcs.md).

## Configuration Options
Each `[[git]]` section supports the following options:

**name**<br/>
When your configuration file contains multiple `[git]` sections you can
assign a name so that you can use the `--name` option when running the 
`netcfgbu vcs` subcommands.

**repo**<br/>
This is the git repository git URL that is found on the git repository
page when you select "Clone or Download".  The value will begin either with "http://"
when using HTTPS mode or or "git@" when using SSH mode.

**username** (Optional)<br/>
When provided this value will be used to indicate the user-name
when files are stored into the git repo.  If you do not configure
this option then the environment `$USER` value is used.  This
option supports the use of Enviornment variables.

**email** (Optional)<br/>
When provided this value will be used to indcate the user email
address with files are stored into the git repo.  If you do not
configure this option then the `username` value is used.

**token** (Optional)<br/>
If you configure this value then `netcfgbu` will use this token
to access your git repository as the credential method.  This
option supports the use of Enviornment variables.  Use this
option if your `repo` field begins with "https://".

**deploy_key** (Optional)<br/>
This option indicates the filepath to the SSH private-key file.  Use
this option if your `repo` field begins with "git@".  This
option supports the use of Enviornment variables.

**deploy_passphrase** (Optional)<br/>
This option is required if your deployment key was created with a passphrase.
This option supports the use of Enviornment variables.

## Examples
```toml
[[git]]
    # the first entry does not require a name and it will be treated
    # as a default; i.e. when the --name option is omitted.
    repo = "https://github.mycorp.com/jschulman/test-network-configs.git"
    token = "$GIT_TOKEN"

[[git]]
    # example of using a deployment key that does not use a passphrase
    name = "demo-key-no-pw"
    repo = "git@gitlab.com:jschulman/test-network-configs.git"
    deploy_key = "$HOME/test-config-backups"

[[git]]
    # example of using a deployment key that uses a passphrase
    name = "demo-key-pw"
    repo = "git@github.mycorp.com:jschulman/test-network-configs.git"
    deploy_key = "$HOME/pwtest-backups"
    deploy_passphrase = "$GITKEY_PASSWORD"  
```

## References
For more information about the tradeoffs of using Tokens vs. Deployment Keys
see [this document](https://developer.github.com/v3/guides/managing-deploy-keys/).

For more information about using Github/Gitlab Tokens see [Github](https://help.github.com/en/github/authenticating-to-github/creating-a-personal-access-token-for-the-command-line)/[Gitlab](https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html).

For more information about using Github/Gitlab deployment keys see [Github](https://developer.github.com/v3/guides/managing-deploy-keys/#deploy-keys)/[Gitlab](https://docs.gitlab.com/ee/user/project/deploy_keys/).