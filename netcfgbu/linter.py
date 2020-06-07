from pathlib import Path
import re

from .logger import get_logger

log = get_logger()


def lint_content(config_content, lint_spec):
    start_offset = 0
    end_offset = None

    if not start_offset and (starts_after := lint_spec.get("config_starts_after")):
        if start_mo := re.search(f"^{starts_after}.*$", config_content, re.MULTILINE):
            start_offset = start_mo.end() + 1

    if not end_offset and (ends_at := lint_spec.get("config_ends_at")):
        end_offset = config_content.rfind("\n" + ends_at)

    config_content = config_content[start_offset:end_offset]

    if remove_lines := lint_spec.get("remove_lines"):
        remove_lines_reg = "|".join(remove_lines)
        config_content = re.sub(remove_lines_reg, "", config_content, flags=re.M)

    return config_content


def lint_file(fileobj: Path, lint_spec):
    orig_config_content = fileobj.read_text()

    config_content = lint_content(orig_config_content, lint_spec)
    if config_content == orig_config_content:
        log.debug(f"LINT no change on {fileobj.name}")
        return

    fileobj.rename(str(fileobj.absolute()) + ".orig")
    fileobj.write_text(config_content)
