from pathlib import Path
import re

from .logger import get_logger
from .config_model import LinterSpec


log = get_logger()


def lint_content(config_content, lint_spec: LinterSpec):
    start_offset = 0
    end_offset = None

    if not start_offset and lint_spec.config_starts_after:
        if start_mo := re.search(
            f"^{lint_spec.config_starts_after}.*$", config_content, re.MULTILINE
        ):
            start_offset = start_mo.end() + 1

    if lint_spec.config_ends_at:
        # if not found, rfind returns -1 to indciate; therefore need to make
        # this check
        if (found := config_content.rfind("\n" + lint_spec.config_ends_at)) > 0:
            end_offset = found

    config_content = config_content[start_offset:end_offset]

    # if remove_lines := lint_spec.remove_lines:
    #     remove_lines_reg = "|".join(remove_lines)
    #     config_content = re.sub(remove_lines_reg, "", config_content, flags=re.M)

    return config_content


def lint_file(fileobj: Path, lint_spec) -> bool:
    """
    Perform the linting function on the content in the given file.
    Returns True if the content was changed, False otherwise.
    """
    orig_config_content = fileobj.read_text()

    config_content = lint_content(orig_config_content, lint_spec)
    if config_content == orig_config_content:
        log.debug(f"LINT no change on {fileobj.name}")
        return False

    fileobj.rename(str(fileobj.absolute()) + ".orig")
    fileobj.write_text(config_content)
    return True
