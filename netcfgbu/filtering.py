"""
This file contains the filtering functions that are using to process the
'--include' and '--exclude' command line options.  The code in this module is
not specific to the netcfgbu inventory column names, can could be re-used for
other CSV related tools and use-cases.
"""
from typing import List, AnyStr, Optional, Callable, Dict
import re
import operator
from pathlib import Path

from .filetypes import CommentedCsvReader

__all__ = ["create_filter"]


value_pattern = r"(?P<value>\S+)$"
file_reg = re.compile(r"@(?P<filename>.+)$")
wordsep_re = re.compile(r"\s+|,")


def mk_op_filter(_reg, _fieldn):
    def op_filter(rec):
        return _reg.match(rec[_fieldn])

    op_filter.__doc__ = f"limit_{_fieldn}({_reg.pattern})"
    op_filter.__name__ = op_filter.__doc__
    op_filter.__qualname__ = op_filter.__doc__

    return op_filter


def create_filter_function(op_filters, optest_fn):
    def filter_fn(rec):
        for op_fn in op_filters:
            if optest_fn(op_fn(rec)):
                return False

        return True

    return filter_fn


def mk_file_filter(filepath, key):

    if filepath.endswith(".csv"):
        filter_hostnames = [rec[key] for rec in CommentedCsvReader(open(filepath))]
    else:
        raise ValueError(
            f"File '{filepath}' not a CSV file.  Only CSV files are supported at this time"
        )

    def op_filter(rec):
        return rec[key] in filter_hostnames

    op_filter.hostnames = filter_hostnames
    op_filter.__doc__ = f"file: {filepath})"
    op_filter.__name__ = op_filter.__doc__
    op_filter.__qualname__ = op_filter.__doc__

    return op_filter


def create_filter(
    constraints: List[AnyStr], field_names: List[AnyStr], include: Optional[bool] = True
) -> Callable[[Dict], bool]:
    """
    This function returns a function that is used to filter inventory records.

    Parameters
    ----------
    constraints:
        A list of contraint expressions that are in the form "<field-name>=<value>".

    field_names:
        A list of known field names

    include:
        When True, the filter function will match when the constraint is true,
        for example if the contraint is "os_name=eos", then it would match
        records that have os_name field euqal to "eos".

        When False, the filter function will match when the constraint is not
        true. For exampl if the constraint is "os_name=eos", then the filter
        function would match recoreds that have os_name fields not equal to
        "eos".

    Returns
    -------
    The returning filter function expects an inventory record as the single
    input parameter, and the function returns True/False on match.
    """
    fieldn_pattern = "^(?P<keyword>" + "|".join(fieldn for fieldn in field_names) + ")"
    field_value_reg = re.compile(fieldn_pattern + "=" + value_pattern)

    op_filters = list()
    for filter_expr in constraints:

        # check for the '@<filename>' filtering use-case first.

        if mo := file_reg.match(filter_expr):
            filepath = mo.group(1)
            if not Path(filepath).exists():
                raise FileNotFoundError(filepath)

            try:
                op_filters.append(mk_file_filter(filepath, key="host"))
                continue

            except KeyError:
                raise ValueError(
                    f"File '{filepath}' does not contain host content as expected"
                )

        # next check for keyword=value filtering use-case

        if (mo := field_value_reg.match(filter_expr)) is None:
            raise ValueError(f"Invalid filter expression: {filter_expr}")

        fieldn, value = mo.groupdict().values()

        try:
            value_reg = re.compile(f"^{value}$", re.IGNORECASE)

        except re.error as exc:
            raise ValueError(
                f"Invalid filter regular-expression: {filter_expr}: {str(exc)}"
            )

        op_filters.append(mk_op_filter(value_reg, fieldn))

    optest_fn = operator.not_ if include else operator.truth
    filter_fn = create_filter_function(op_filters, optest_fn)
    filter_fn.op_filters = op_filters
    filter_fn.constraints = constraints

    return filter_fn
