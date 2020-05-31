import re
import aiofiles
import asyncssh
import io
from pathlib import Path

class ConfigBackupSSHTemplate(object):
    comms_prompt_pattern = re.compile(r"^\r?[a-z0-9.\-@()/:]{1,32}[#>$]$", flags=(re.M | re.I))
    show_running = 'show running-config'

    def __init__(self, host_cfg, app_cfg):
        self.host_cfg = host_cfg
        self.name = host_cfg.get('host') or host_cfg.get('ipaddr')
        self.app_cfg = app_cfg
        self.config = None
        app_defaults = app_cfg['defaults']
        os_name = host_cfg['os_name']
        self.os_spec = app_cfg['os_spec'].get(os_name) or {}

        self.conn_args = {
            'host': self.host_cfg.get('ipaddr') or self.host_cfg.get('host'),
            'username': host_cfg.get('username') or app_defaults.get('username'),
            'password': host_cfg.get('password') or app_defaults.get('password'),
            'known_hosts': None
        }

        self._stdout = None
        self._stdin = None
        self._stderr = None

    async def read_until_prompt(self):
        output = ''
        while True:
            output += await self._stdout.read(io.DEFAULT_BUFFER_SIZE)
            if self.comms_prompt_pattern.match(output):
                return output

    async def run_command(self, command):
        wr_cmd = command + "\n"

        self._stdin.write(wr_cmd)
        output = ''

        while True:
            output += await self._stdout.read(io.DEFAULT_BUFFER_SIZE)
            nl_at = output.rfind('\n')
            if nl_at > 0 and self.comms_prompt_pattern.match(output[nl_at + 1:]):
                return output[len(wr_cmd) + 1:nl_at]

    async def save_config(self):
        save_file = Path(self.app_cfg['defaults']['configs_dir']) / f"{self.name}.cfg"
        async with aiofiles.open(str(save_file.absolute()), "w+") as ofile:
            await ofile.write(self.config)
            await ofile.write("\n")

    async def backup_config(self):
        get_config_meth = (self._get_config if 'disable_paging' not in self.os_spec
                           else self._get_config_disable_paging)

        await get_config_meth()
        await self.save_config()

    async def _get_config(self):
        async with asyncssh.connect(**self.conn_args) as conn:
            command = self.show_running
            res = await conn.run(command)
            ln_at = res.stdout.find(command) + len(command) + 1
            self.config = res.stdout[ln_at:]

    async def _get_config_disable_paging(self):
        async with asyncssh.connect(**self.conn_args) as conn:
            self._stdin, self._stdout, self._stderr = await conn.open_session(
                term_type='tty'
            )

            disable_paging_commands = self.os_spec['disable_paging']
            if not isinstance(disable_paging_commands, list):
                disable_paging_commands = [disable_paging_commands]

            await self.read_until_prompt()
            for cmd in disable_paging_commands:
                res = await self.run_command(cmd)
                x = 2

            command = self.show_running
            result = await self.run_command(command)
            self.config = result.replace("\r", "")
