import re
import os
from typing import Optional, Union, List, Dict
from os.path import expandvars
from itertools import chain
from pathlib import Path

from pydantic import (
    BaseModel,
    SecretStr,
    BaseSettings,
    PositiveInt,
    FilePath,
    Field,
    validator,
    root_validator,
)


from . import consts

__all__ = [
    "AppConfig",
    "Credential",
    "InventorySpec",
    "OSNameSpec",
    "LinterSpec",
    "GitSpec",
    "JumphostSpec",
]

_var_re = re.compile(
    r"\${(?P<bname>[a-z0-9_]+)}" r"|" r"\$(?P<name>[^{][a-z_0-9]+)", flags=re.IGNORECASE
)


class NoExtraBaseModel(BaseModel):
    class Config:
        extra = "forbid"


class EnvExpand(str):
    """
    When a string value contains a reference to an environment variable, use
    this type to expand the contents of the variable using os.path.expandvars.

    For example like:
        password = "$MY_PASSWORD"
        foo_password = "${MY_PASSWORD}_foo"

    will be expanded, given MY_PASSWORD is set to 'boo!' in the environment:
        password -> "boo!"
        foo_password -> "boo!_foo"
    """

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if found_vars := list(filter(len, chain.from_iterable(_var_re.findall(v)))):
            for var in found_vars:
                if (var_val := os.getenv(var)) is None:
                    raise ValueError(f'Environment variable "{var}" missing.')

                if not len(var_val):
                    raise ValueError(f'Environment variable "{var}" empty.')

            return expandvars(v)

        return v


class EnvSecretStr(EnvExpand, SecretStr):
    @classmethod
    def validate(cls, v):
        return SecretStr.validate(EnvExpand.validate(v))


class Credential(NoExtraBaseModel):
    username: EnvExpand
    password: EnvSecretStr


class DefaultCredential(Credential, BaseSettings):
    username: EnvExpand = Field(..., env="NETCFGBU_DEFAULT_USERNAME")
    password: EnvSecretStr = Field(..., env="NETCFGBU_DEFAULT_PASSWORD")


class Defaults(NoExtraBaseModel, BaseSettings):
    configs_dir: Optional[EnvExpand] = Field(..., env=("NETCFGBU_CONFIGSDIR", "PWD"))
    inventory: EnvExpand = Field(..., env="NETCFGBU_INVENTORY")
    credentials: DefaultCredential

    @validator("inventory")
    def _inventory_provided(cls, value):  # noqa
        if not len(value):
            raise ValueError("inventory empty value not allowed")
        return value

    @validator("configs_dir")
    def _configs_dir(cls, value):  # noqa
        return Path(value).absolute()


class FilePathEnvExpand(FilePath):
    """ A FilePath field whose value can interpolated from env vars """

    @classmethod
    def __get_validators__(cls):
        yield from EnvExpand.__get_validators__()
        yield from FilePath.__get_validators__()


class GitSpec(NoExtraBaseModel):
    name: Optional[str]
    repo: str
    email: Optional[str]
    username: Optional[EnvExpand]
    password: Optional[EnvExpand]
    token: Optional[EnvSecretStr]
    deploy_key: Optional[FilePathEnvExpand]
    deploy_passphrase: Optional[EnvSecretStr]

    @validator("repo")
    def validate_repo(cls, repo):  # noqa
        expected = ("https:", "git@")
        if not repo.startswith(expected):
            raise ValueError(
                f"Bad repo URL [{repo}]: expected to start with {expected}."
            )
        return repo

    @root_validator
    def enure_proper_auth(cls, values):
        req = ("token", "deploy_key", "password")
        auth_vals = list(filter(None, (values.get(auth) for auth in req)))
        auth_c = len(auth_vals)
        if not auth_c:
            raise ValueError(
                f'Missing one of required auth method fields: {"|".join(req)}'
            )

        if auth_c > 1:
            raise ValueError(f'Only one of {"|".join(req)} allowed')

        if values.get("deploy_passphrase") and not values.get("deploy_key"):
            raise ValueError("deploy_key required when using deploy_passphrase")

        return values


class OSNameSpec(NoExtraBaseModel):
    credentials: Optional[List[Credential]]
    pre_get_config: Optional[Union[str, List[str]]]
    get_config: Optional[str]
    connection: Optional[str]
    linter: Optional[str]
    timeout: PositiveInt = Field(consts.DEFAULT_GETCONFIG_TIMEOUT)
    ssh_configs: Optional[Dict]


class LinterSpec(NoExtraBaseModel):
    config_starts_after: Optional[str]
    config_ends_at: Optional[str]


class InventorySpec(NoExtraBaseModel):
    name: Optional[str]
    script: EnvExpand

    @validator("script")
    def validate_script(cls, script_exec):  # noqa
        script_bin, *script_vargs = script_exec.split()
        if not os.path.isfile(script_bin):
            raise ValueError(f"File not found: {script_bin}")

        if not os.access(script_bin, os.X_OK):
            raise ValueError(f"{script_bin} is not executable")

        return script_exec


class JumphostSpec(NoExtraBaseModel):
    proxy: str
    name: Optional[str]
    include: Optional[List[str]]
    exclude: Optional[List[str]]
    timeout: PositiveInt = Field(consts.DEFAULT_LOGIN_TIMEOUT)

    @validator("name", always=True)
    def _default_name(cls, value, values):  # noqa
        return values["proxy"] if not value else value


class AppConfig(NoExtraBaseModel):
    defaults: Defaults
    credentials: Optional[List[Credential]]
    linters: Optional[Dict[str, LinterSpec]]
    os_name: Optional[Dict[str, OSNameSpec]]
    inventory: Optional[List[InventorySpec]]
    logging: Optional[Dict]
    ssh_configs: Optional[Dict]
    git: Optional[List[GitSpec]]
    jumphost: Optional[List[JumphostSpec]]

    @validator("os_name")
    def _linters(cls, v, values):  # noqa
        linters = values.get("linters") or {}
        for os_name, os_spec in v.items():
            if os_spec.linter and os_spec.linter not in linters:
                raise ValueError(
                    f'OS spec "{os_name}" using undefined linter "{os_spec.linter}"'
                )
        return v
