import re
import os
from typing import Optional, Union, List, Dict
from os.path import expandvars
from pydantic import BaseModel, SecretStr, BaseSettings, PositiveInt, Field, validator

from itertools import chain

from . import consts

__all__ = ["AppConfig", "Credential", "InventorySpec", "OSNameSpec", "LinterSpec"]

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
                if not os.getenv(var):
                    raise ValueError(f'Environment variable "{var}" missing.')
            return expandvars(v)

        return v


class EnvSecretStr(EnvExpand, SecretStr):
    @classmethod
    def validate(cls, v):
        return SecretStr.validate(EnvExpand.validate(v))


class Credential(NoExtraBaseModel):
    username: EnvExpand
    password: EnvSecretStr


class DefaultCredential(NoExtraBaseModel, BaseSettings):
    username: EnvExpand = Field(..., env="NETCFGBU_DEFAULT_USERNAME")
    password: EnvSecretStr = Field(..., env="NETCFGBU_DEFAULT_PASSWORD")


class Defaults(NoExtraBaseModel, BaseSettings):
    configs_dir: Optional[EnvExpand] = Field(..., env=("NETCFGBU_CONFIGSDIR", "PWD"))
    inventory: Optional[EnvExpand] = Field(..., env="NETCFGBU_INVENTORY")
    credentials: DefaultCredential


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
            raise FileNotFoundError(script_bin)

        if not os.access(script_bin, os.X_OK):
            raise ValueError(f"{script_bin} is not executable")

        return script_exec


class AppConfig(NoExtraBaseModel):
    defaults: Defaults
    credentials: Optional[List[Credential]]
    os_name: Optional[Dict[str, OSNameSpec]]
    inventory: Optional[List[InventorySpec]]
    linters: Optional[Dict[str, LinterSpec]]
    logging: Optional[Dict]
    ssh_configs: Optional[Dict]
