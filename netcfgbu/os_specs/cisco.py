from netcfgbu.netcfgbu_ssh import ConfigBackupSSHTemplate

cisco_spec = {
    'disable_paging': 'terminal length 0'
}

cisco_asa_spec = {
    'disable_paging': 'terminal pager 0'
}


class CiscoWLCSSHSpec(ConfigBackupSSHTemplate):
    show_running = "show run-config commands"
    disable_paging = "config paging disable"

    async def login(self):
        await super(CiscoWLCSSHSpec, self).login()
        await self.process.stdout.readuntil("User:")
        self.process.stdin.write(self.conn_args['username'] + "\n")
        self.process.stdin.write(self.conn_args['password'] + "\n")
