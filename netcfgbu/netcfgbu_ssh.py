import re
import asyncssh
import io
import asyncio
from pathlib import Path
from copy import copy
import logging


_LOG = logging.getLogger(__package__)


class ConfigBackupSSHTemplate(object):
    PROMPT_PATTERN = re.compile(r"^\r?([a-z0-9.\-@()/:]{1,32}\s*[#>$])\s*$", flags=(re.M | re.I))

    show_running = 'show running-config'

    def __init__(self, host_cfg, os_spec, app_cfg):
        self.host_cfg = host_cfg
        self.name = host_cfg.get('host') or host_cfg.get('ipaddr')
        self.app_cfg = app_cfg
        self.os_spec = copy(os_spec)
        if hasattr(self.__class__, 'disable_paging') and 'disable_paging' not in os_spec:
            self.os_spec['disable_paging'] = self.__class__.disable_paging

        self.os_name = host_cfg['os_name']

        self.conn_args = {
            'host': self.host_cfg.get('ipaddr') or self.host_cfg.get('host'),
            'known_hosts': None
        }

        self.config = None
        self.save_file = None
        self.failed = None

        self.conn = None
        self.process = None

        _LOG.info(f"INIT-READY: {self.name} ({self.os_name})")

    async def login(self):
        creds = copy(self.app_cfg['credentials'])

        # if there are host specific credentials, then try these first.
        if (uname := self.host_cfg.get('username')) and (password := self.host_cfg.get('password')):
            creds.insert(0, [dict(username=uname, password=password)])

        for try_cred in creds:
            try:
                self.failed = None
                self.conn_args.update(try_cred)
                self.conn = await asyncio.wait_for(asyncssh.connect(**self.conn_args), timeout=60)

                if (
                    'disable_paging' in self.os_spec or
                    hasattr(self.__class__, 'disable_paging')
                ):
                    self.process = await self.conn.create_process(term_type='vt100')

                _LOG.info(f"CONNECTED: {self.name}")
                return self.conn

            except asyncssh.PermissionDenied as exc:
                self.failed = exc
                continue

        raise asyncssh.PermissionDenied(
            reason='Bad username/password'
        )

    def close(self):
        if self.process:
            self.process.terminate()

        self.conn.close()

    async def read_until_prompt(self):
        output = ''
        while True:
            output += await self.process.stdout.read(io.DEFAULT_BUFFER_SIZE)
            nl_at = output.rfind('\n')
            if mobj := self.PROMPT_PATTERN.match(output[nl_at + 1:]):
                return mobj.group(1)

    async def run_command(self, command):
        wr_cmd = command + "\n"
        self.process.stdin.write(wr_cmd)

        output = ''
        while True:
            output += await self.process.stdout.read(io.DEFAULT_BUFFER_SIZE)
            nl_at = output.rfind('\n')
            if nl_at > 0 and self.PROMPT_PATTERN.match(output[nl_at + 1:]):
                return output[len(wr_cmd) + 1:nl_at]

    async def save_config(self):
        self.save_file = Path(self.app_cfg['defaults']['configs_dir']) / f"{self.name}.cfg"
        with self.save_file.open("w+") as ofile:
            ofile.write(self.config)
            ofile.write("\n")

    async def backup_config(self):

        await self.login()
        await self.get_running_config()
        self.close()

        if self.config:
            await self.save_config()

        return self

    async def get_running_config(self):
        command = self.show_running

        if not self.process:
            _LOG.info(f"GET-CONFIG: {self.name}")
            res = await self.conn.run(command)
            self.conn.close()
            ln_at = res.stdout.find(command) + len(command) + 1
            self.config = res.stdout[ln_at:]
            return

        await self.read_until_prompt()
        await self.run_disable_paging()
        _LOG.info(f"GET-CONFIG: {self.name}")
        result = await self.run_command(command)
        self.config = result.replace("\r", "")

    async def run_disable_paging(self):
        disable_paging_commands = self.os_spec['disable_paging']
        if not isinstance(disable_paging_commands, list):
            disable_paging_commands = [disable_paging_commands]

        for cmd in disable_paging_commands:
            # TODO: need to check result for errors
            await self.run_command(cmd)
