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

    # Note: if you want to check the pass/fail of this call os.system() will
    # return 0 or non-zero as the exit code from the underlying script.  There
    # is no exception handling.  If you want to do exception handling, then
    # you'll need to use subprocess.call in place of os.system.

    os.system(script)
