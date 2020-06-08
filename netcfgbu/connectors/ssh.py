import asyncio
from netcfgbu.connectors.basic import BasicSSHConnector


class LoginPromptUserPass(BasicSSHConnector):
    async def login(self):
        await super(LoginPromptUserPass, self).login()

        await asyncio.wait_for(self.process.stdout.readuntil(b"User:"), timeout=10)

        username = (self.conn_args["username"] + "\n").encode("utf-8")
        self.process.stdin.write(username)

        await asyncio.wait_for(self.process.stdout.readuntil(b"Password:"), timeout=10)

        password = (self.conn_args["password"] + "\n").encode("utf-8")
        self.process.stdin.write(password)

        return self.conn
