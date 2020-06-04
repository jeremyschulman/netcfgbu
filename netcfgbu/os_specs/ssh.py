from netcfgbu.netcfgbu_ssh import ConfigBackupSSHSpec


class LoginPromoptUserPass(ConfigBackupSSHSpec):
    async def login(self):
        await super(LoginPromoptUserPass, self).login()
        await self.process.stdout.readuntil("User:")
        self.process.stdin.write(self.conn_args["username"] + "\n")
        self.process.stdin.write(self.conn_args["password"] + "\n")
        return self.conn
