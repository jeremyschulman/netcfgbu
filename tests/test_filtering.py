import pytest  # noqa
from netcfgbu.filtering import create_filter
import csv


def test_filtering_pass_include():
    """
    Test the use-case where the constraint is a vliad set of "limits"
    """
    key_values = [("os_name", "eos"), ("host", ".*nyc1")]
    constraints = [f"{key}={val}" for key, val in key_values]
    field_names = [key for key, _ in key_values]

    filter_fn = create_filter(
        constraints=constraints, field_names=field_names, include=True
    )

    assert filter_fn(dict(os_name="eos", host="switch1.nyc1")) is True
    assert filter_fn(dict(os_name="ios", host="switch1.nyc1")) is False
    assert filter_fn(dict(os_name="eos", host="switch1.dc1")) is False


def test_filtering_pass_exlcude():
    """
    Test use-case where the constraint is a valid set of "excludes"
    """
    key_values = [("os_name", "eos"), ("host", ".*nyc1")]
    constraints = [f"{key}={val}" for key, val in key_values]
    field_names = [key for key, _ in key_values]

    filter_fn = create_filter(
        constraints=constraints, field_names=field_names, include=False
    )

    assert filter_fn(dict(os_name="ios", host="switch1.nyc1")) is False
    assert filter_fn(dict(os_name="eos", host="switch1.dc1")) is False
    assert filter_fn(dict(os_name="ios", host="switch1.dc1")) is True


def test_filtering_fail_constraint_field():
    """
    Test the use-case where the constraint form is invalid due to a
    field name being incorrect.
    """
    key_values = [("os_name2", "eos"), ("host", ".*nyc1")]
    constraints = [f"{key}={val}" for key, val in key_values]
    field_names = ["os_name", "host"]

    with pytest.raises(ValueError) as excinfo:
        create_filter(constraints=constraints, field_names=field_names, include=False)

    errmsg = excinfo.value.args[0]
    assert "Invalid filter expression: os_name2=eos" in errmsg


def test_filtering_fail_constraint_regex():
    """
    Test the case where the constraint value is an invalid regular-expression.
    """
    with pytest.raises(ValueError) as excinfo:
        create_filter(
            constraints=["os_name=***"], field_names=["os_name"], include=False
        )

    errmsg = excinfo.value.args[0]
    assert "Invalid filter regular-expression" in errmsg


def test_filtering_pass_filepath(tmpdir):
    """
    Test use-case where a filepath constraint is provide, and the file exists.
    """
    filename = "failures.csv"
    tmpfile = tmpdir.join(filename)
    tmpfile.ensure()
    abs_filepath = str(tmpfile)

    create_filter(constraints=[f"@{abs_filepath}"], field_names=["host"])


def test_filtering_fail_filepath(tmpdir):
    """
    Test use-case where a filepath constraint is provide, and the file does not exist.
    """
    filename = "failures.csv"
    tmpfile = tmpdir.join(filename)
    abs_filepath = str(tmpfile)

    with pytest.raises(FileNotFoundError) as excinfo:
        create_filter(constraints=[f"@{abs_filepath}"], field_names=["host"])

    errmsg = excinfo.value.args[0]
    assert errmsg == abs_filepath


def test_filtering_pass_csv_filecontents(tmpdir):
    """
    Test use-case where the constraint is a valid CSV file.
    """
    filename = "failures.csv"
    tmpfile = tmpdir.join(filename)

    inventory_recs = [
        dict(host="swtich1.nyc1", os_name="eos"),
        dict(host="switch2.dc1", os_name="ios"),
    ]

    not_inventory_recs = [
        dict(host="swtich3.nyc1", os_name="eos"),
        dict(host="switch4.dc1", os_name="ios"),
    ]

    with open(tmpfile, "w+") as ofile:
        csv_wr = csv.DictWriter(ofile, fieldnames=["host", "os_name"])
        csv_wr.writeheader()
        csv_wr.writerows(inventory_recs)

    abs_filepath = str(tmpfile)

    filter_fn = create_filter(constraints=[f"@{abs_filepath}"], field_names=["host"])
    for rec in inventory_recs:
        assert filter_fn(rec) is True

    for rec in not_inventory_recs:
        assert filter_fn(rec) is False

    filter_fn = create_filter(
        constraints=[f"@{abs_filepath}"], field_names=["host"], include=False
    )
    for rec in inventory_recs:
        assert filter_fn(rec) is False

    for rec in not_inventory_recs:
        assert filter_fn(rec) is True


def test_filtering_fail_csv_missinghostfield(tmpdir):
    """
    Test use-case where the constraint is an invalid CSV file; meaning that there
    is no `host` field.
    """
    filename = "failures.csv"
    tmpfile = tmpdir.join(filename)

    # create an inventory that does not use 'host' as required, but uses
    # 'hostname' instead.

    inventory_recs = [
        dict(hostname="swtich1.nyc1", os_name="eos"),
        dict(hostname="switch2.dc1", os_name="ios"),
    ]

    with open(tmpfile, "w+") as ofile:
        csv_wr = csv.DictWriter(ofile, fieldnames=["hostname", "os_name"])
        csv_wr.writeheader()
        csv_wr.writerows(inventory_recs)

    abs_filepath = str(tmpfile)

    with pytest.raises(ValueError) as excinfo:
        create_filter(constraints=[f"@{abs_filepath}"], field_names=["hostname"])

    errmsg = excinfo.value.args[0]
    assert "does not contain host content as expected" in errmsg


def test_filtering_fail_csv_filecontentsnotcsv(tmpdir):
    """
    Test use-case where the constraint expects a CSV file, but the file is not
    a CSV file due to contents; i.e. when attempting to read the CSV file it fails
    to load content.
    """

    # rather than provide a CSV file, provide this python file (not a CSV file).
    # but call it a CSV file.

    filepath = tmpdir.join("dummy.csv")
    filepath.mklinkto(__file__)

    with pytest.raises(ValueError) as excinfo:
        create_filter(constraints=[f"@{filepath}"], field_names=["host"])

    errmsg = excinfo.value.args[0]
    assert "does not contain host content as expected" in errmsg


def test_filtering_fail_csv_notcsvfile():
    """
    Test use-case when the provided file is not a CSV, and indicated by the
    filename suffix not being '.csv'
    """
    with pytest.raises(ValueError) as excinfo:
        create_filter(constraints=[f"@{__file__}"], field_names=["host, os_name"])

    errmsg = excinfo.value.args[0]
    assert "not a CSV file." in errmsg
