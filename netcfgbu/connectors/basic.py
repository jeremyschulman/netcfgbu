from typing import Optional
import asyncio
import io
from pathlib import Path
import re
from copy import copy

import aiofiles
import asyncssh


from netcfgbu.config_model import AppConfig, OSNameSpec, Credential
from netcfgbu.logger import get_logger
from netcfgbu import consts
from netcfgbu import linter
from netcfgbu import jumphosts


__all__ = ["BasicSSHConnector", "set_max_startups"]


class BasicSSHConnector(object):
    """
    The BasicSSHConnector class is used to define and process the
    configuration file backup process over SSH.  The primary usage is to
    initialize the class with the host configuration, the operating system
    specification, and the application configuration.  Once initialized the
    Caller should await on `backup_config()` to execute the backup process.

    If the BasicSSHConnector defines `pre_get_config` will execute those
    commands before executinig the `get_config` command.

    If the BasicSSHConnector does not define the `pre_get_config` attribute,
    then only the `get_config` command will be executed.


    Attributes
    ----------
    cls.PROMPT_PATTERN: re.Pattern
        compiled regular expression this used to find the CLI prompt

    cls.get_config: str
        The device CLI command that when executed will produce the output of
        the running configuraiton

    cls.pre_get_config: Optional[Union[str,list]]
        The device CLI command(s) that when execute will disable paging so that
        when the show-running command is executed the output will not be
        blocked with a "--More--" user prompt.
    """

    PROMPT_PATTERN = re.compile(
        (
            "^\r?(["
            + consts.PROMPT_VALID_CHARS
            + "]{%s,%s}" % (1, consts.PROMPT_MAX_CHARS)
            + r"\s*[#>$])\s*$"
        ).encode("utf-8"),
        flags=(re.M | re.I),
    )

    get_config = "show running-config"
    pre_get_config = None

    _max_startups_sem4 = asyncio.Semaphore(consts.DEFAULT_MAX_STARTUPS)

    def __init__(self, host_cfg: dict, os_spec: OSNameSpec, app_cfg: AppConfig):
        """
        Initialize the backup spec with information about the host, the os_spec assigned
        to the host, and the command app configuration.

        Parameters
        ----------
        host_cfg
        os_spec
        app_cfg
        """
        self.host_cfg = host_cfg
        self.name = host_cfg.get("host") or host_cfg.get("ipaddr")
        self.app_cfg = app_cfg
        self.os_spec = copy(os_spec)
        self.log = get_logger()

        if not self.os_spec.pre_get_config:
            self.os_spec.pre_get_config = self.pre_get_config

        if not self.os_spec.get_config:
            self.os_spec.get_config = self.get_config

        self.os_name = host_cfg["os_name"]

        self.conn_args = {
            "host": self.host_cfg.get("ipaddr") or self.host_cfg.get("host"),
            "known_hosts": None,
        }

        if app_cfg.ssh_configs:
            self.conn_args.update(app_cfg.ssh_configs)

        if os_spec.ssh_configs:
            self.conn_args.update(os_spec.ssh_configs)

        self._cur_prompt: Optional[str] = None
        self.config = None
        self.save_file = None
        self.failed = None

        self.conn = None
        self.process: Optional[asyncssh.SSHClientProcess] = None
        self.creds = self._setup_creds()

        if not len(self.creds):
            raise RuntimeError(f"{self.name}: No credentials")

    @classmethod
    def set_max_startups(cls, max_startups):
        cls._max_startups_sem4 = asyncio.Semaphore(value=max_startups)

    # -------------------------------------------------------------------------
    #
    #                       Backup Config Coroutine Task
    #
    # -------------------------------------------------------------------------

    async def backup_config(self):
        """
        This is the "main" coroutine that should be used as Task that will
        perform each of the steps to backup the running configuration to a text
        file.

        Returns
        -------
        BasicSSHConnector
            Instance of self so that information about the process can be
            examined once the backup process completes, or fails.
        """

        async with await self.login():
            try:
                await self.get_running_config()
                retval = True
            except Exception as exc:
                retval = exc

            finally:
                await self.close()

        if self.config:
            await self.save_config()

        return retval

    # -------------------------------------------------------------------------
    #
    #                       Test Login Coroutine Task
    #
    # -------------------------------------------------------------------------

    async def test_login(self, timeout=None) -> Optional[str]:
        login_as = None
        self.os_spec.timeout = timeout

        try:
            async with await self.login():
                login_as = self.conn_args["username"]

        except asyncssh.PermissionDenied:
            pass

        return login_as

    # -------------------------------------------------------------------------
    #
    #                            Get Configuration
    #
    # -------------------------------------------------------------------------

    async def get_running_config(self):
        command = self.os_spec.get_config
        timeout = self.os_spec.timeout
        log_msg = f"GET-CONFIG: {self.name} timeout={timeout}"

        if not self.process:
            self.log.info(log_msg)
            res = await self.conn.run(command)
            self.conn.close()
            ln_at = res.stdout.find(command) + len(command) + 1
            self.config = res.stdout[ln_at:]
            return

        at_prompt = False
        paging_disabled = False

        try:
            res = await asyncio.wait_for(self.read_until_prompt(), timeout=10)
            at_prompt = True
            self.log.debug(f"AT-PROMPT: {res}")

            res = await asyncio.wait_for(self.run_disable_paging(), timeout=10)
            paging_disabled = True
            self.log.debug(f"AFTER-PRE-GET-RUNNING: {res}")

            self.log.info(log_msg)
            self.config = await asyncio.wait_for(
                self.run_command(command), timeout=timeout
            )

        except asyncio.TimeoutError:
            if not at_prompt:
                msg = "Timeout awaiting prompt"
            elif not paging_disabled:
                msg = "Timeout executing pre-get-running commands"
            else:
                msg = "Timeout getting running configuration"

            raise asyncio.TimeoutError(msg)

    # -------------------------------------------------------------------------
    #
    #                                  Login
    #
    # -------------------------------------------------------------------------

    def _setup_creds(self):
        creds = list()

        # use credential from inventory host record first, if defined
        # TODO: bug-fix where these values are None; but exist in dict :-(
        if all(key in self.host_cfg for key in ("username", "password")):
            creds.append(
                Credential(
                    username=self.host_cfg.get("username"),
                    password=self.host_cfg.get("password"),
                )
            )

        # add any addition credentials defined in the os spec
        if self.os_spec.credentials:
            creds.extend(self.os_spec.credentials)

        # add the default credentials
        creds.append(self.app_cfg.defaults.credentials)

        # add any additional global credentials
        if self.app_cfg.credentials:
            creds.extend(self.app_cfg.credentials)

        return creds

    async def login(self):
        """
        This coroutine is used to execute the SSH login process to the target device.
        Each of the `credentials` provided in the app-configure are tried in the order
        they were provided in the configuration file.  If the host configuraiton included
        credentials, these will be used first.

        When this coroutine completes successfully the `conn` attribute is
        initialized to the SSHClientConnection.  If this SSHSpec requires the
        use of multiple commands, so that paging can be disabled, then the
        `process` attribute is also initiazed so that the `process.stdin` and
        `process.stdout` can be used to interact with the SSH CLI.

        Returns
        -------
        The AsyncSSH will obtain a protocol connection instance from asyncio.loop.create_connection(), and
        then enrobe it with an async context manager so that the Caller can either use the instnace
        directly or as a context manager.

        Raises
        ------
        asyncssh.PermissionDenied
            When none of the provided credentials result in a successful login.

        asyncio.TimeoutError
            When attempting to connect to a device exceeds the timeout value.
        """

        timeout: int = self.os_spec.timeout

        # if this host requires the use of a JumpHost, then configure the
        # connection args to include the supporting jumphost tunnel connection.

        if jh := jumphosts.get_jumphost(self.host_cfg):
            self.conn_args["tunnel"] = jh.tunnel

        # interate through all of the credential options until one is accepted.
        # the number of max setup connections is controlled by a semaphore
        # instance so that the server running this code is not overwhelmed.

        for try_cred in self.creds:
            try:
                self.failed = None
                self.conn_args.update(
                    {
                        "username": try_cred.username,
                        "password": try_cred.password.get_secret_value(),
                    }
                )
                async with self.__class__._max_startups_sem4:

                    login_msg = (
                        f"LOGIN: {self.name} ({self.os_name}) "
                        f"as {self.conn_args['username']}"
                    )

                    self.log.info(login_msg)
                    self.conn = await asyncio.wait_for(
                        asyncssh.connect(**self.conn_args), timeout
                    )
                    self.log.info(f"CONNECTED: {self.name}")

                    if self.os_spec.pre_get_config:
                        self.process = await self.conn.create_process(
                            term_type="vt100", encoding=None
                        )

                    return self.conn

            except asyncssh.PermissionDenied as exc:
                self.failed = exc
                continue

        # Indicate that the login failed with the number of credential
        # attempts.

        raise asyncssh.PermissionDenied(
            reason=f"No valid username/password, attempted {len(self.creds)} credentials."
        )

    async def close(self):
        self.conn.close()
        await self.conn.wait_closed()
        self.log.info(f"CLOSED: {self.name}")

    # -------------------------------------------------------------------------
    #
    #                                    Helpers
    #
    # -------------------------------------------------------------------------

    async def read_until_prompt(self):
        output = b""
        while True:
            output += await self.process.stdout.read(io.DEFAULT_BUFFER_SIZE)
            nl_at = output.rfind(b"\n")
            if mobj := self.PROMPT_PATTERN.match(output[nl_at + 1 :]):
                self._cur_prompt = mobj.group(1)
                return output[0:nl_at]

    async def run_command(self, command):
        wr_cmd = command + "\n"
        self.process.stdin.write(wr_cmd.encode("utf-8"))
        output = await self.read_until_prompt()
        return output[len(wr_cmd) + 1 :]

    async def run_disable_paging(self):
        """
        This coroutine is used to execute each of the `pre_get_config` commands
        so that the CLI will not prompt for "--More--" output.
        """

        disable_paging_commands = self.os_spec.pre_get_config
        if not isinstance(disable_paging_commands, list):
            disable_paging_commands = [disable_paging_commands]

        for cmd in disable_paging_commands:
            # TODO: need to check result for errors
            await self.run_command(cmd)

    # -------------------------------------------------------------------------
    #
    #                         Store Config to Filesystem
    #
    # -------------------------------------------------------------------------

    async def save_config(self):
        if isinstance(self.config, bytes):
            self.config = self.config.decode("utf-8", "ignore")

        config_content = self.config.replace("\r", "")

        if linter_name := self.os_spec.linter:
            lint_spec = self.app_cfg.linters[linter_name]
            orig = config_content
            config_content = linter.lint_content(config_content, lint_spec)
            if orig == config_content:
                self.log.debug(f"LINT no change on {self.name}")

        self.save_file = Path(self.app_cfg.defaults.configs_dir) / f"{self.name}.cfg"

        async with aiofiles.open(self.save_file, mode="w+") as ofile:
            await ofile.write(config_content)
            await ofile.write("\n")


def set_max_startups(count, cls=BasicSSHConnector):
    cls.set_max_startups(count)
