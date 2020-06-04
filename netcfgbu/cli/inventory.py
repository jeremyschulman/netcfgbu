from os.path import expandvars
from netcfgbu.logger import get_logger
import os


def build(inv_def):
    lgr = get_logger()

    script = inv_def.get("script")
    if not script:
        lgr.warning("No script defined for this inventory")
        return

    script = expandvars(script)
    lgr.info(f"Executing script: [{script}]")
    os.system(script)
