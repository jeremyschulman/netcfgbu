from netcfgbu.connectors.basic import BasicSSHConnector


class LoginPromptUserPass(BasicSSHConnector):
    async def login(self):
        await super(LoginPromptUserPass, self).login()
        await self.process.stdout.readuntil("User:")
        self.process.stdin.write(self.conn_args["username"] + "\n")
        self.process.stdin.write(self.conn_args["password"] + "\n")
        return self.conn
