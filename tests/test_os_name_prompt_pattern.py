import re
from netcfgbu import os_specs
from netcfgbu.connectors import BasicSSHConnector
from netcfgbu.config import load


def test_config_os_name_prompt_pattern(netcfgbu_envars, request):  # noqa
    """
    This test validates that a User provided prompt_pattern in the [os_name.$name]
    configuration section results in the User defined pattern used by the
    SSH connector instance.
    """
    rec = {"host": "dummy", "os_name": "cumulus"}
    abs_filepath = (
        request.fspath.dirname + "/files/test-config-os-name-prompt-pattern.toml"
    )
    app_cfg = load(filepath=abs_filepath)
    conn = os_specs.make_host_connector(rec, app_cfg)

    # this value is copied from the configuration toml file.  If you
    # change the test data file then you'd have to change this expected pattern.
    expected_pattern = r"[a-z0-9.\-@:~]{10,65}\s*[#$]"

    # the conenctor code adds a capture group for processing reasons.
    expected_pattern = r"^\r?(" + expected_pattern + r")\s*$"
    expected_re = re.compile(expected_pattern.encode("utf-8"))

    # going to perform a PROMPT pattern match against a sample value.
    test_prompt_value = "cumulus@leaf01:mgmt-vrf:~$"

    assert isinstance(conn, BasicSSHConnector)
    assert expected_re.pattern == conn.PROMPT_PATTERN.pattern
    assert expected_re.match(test_prompt_value.encode("utf-8"))
