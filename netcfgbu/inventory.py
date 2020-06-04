from pathlib import Path
import csv
import re

FIELDNAMES = ["host", "ipaddr", "os_name", "username", "password"]


class CommentedCsvReader(csv.DictReader):
    def __next__(self):
        value = super(CommentedCsvReader, self).__next__()

        if value[self.fieldnames[0]].startswith("#"):
            return self.__next__()

        return value


def load(app_cfg, limits=None):
    inventory_file = Path(app_cfg["defaults"]["inventory"])
    csv_rd = CommentedCsvReader(inventory_file.open())

    if limits:
        filter_fn = create_limit_filter(limits)
        return list(filter(filter_fn, csv_rd))

    return list(csv_rd)


def create_limit_filter(limits):

    fieldn_pattern = "^(?P<keyword>" + "|".join(fieldn for fieldn in FIELDNAMES) + ")"

    value_pattern = r"(?P<value>\S+)$"

    limit_reg = re.compile(fieldn_pattern + "=" + value_pattern)

    op_filters = list()

    def mk_op_filter(_reg, _fieldn):
        def op_filter(rec):
            return _reg.match(rec[_fieldn])

        op_filter.__doc__ = f"limit_{_fieldn}({_reg.pattern})"
        op_filter.__name__ = op_filter.__doc__
        op_filter.__qualname__ = op_filter.__doc__

        return op_filter

    for limit_expr in limits:
        mo = limit_reg.match(limit_expr)
        if not mo:
            raise ValueError(f"INVALID limit expression: {limit_expr}")

        fieldn, value = mo.groupdict().values()

        try:
            value_reg = re.compile(f"^{value}$", re.IGNORECASE)

        except re.error as exc:
            raise ValueError(f"INVALID limit expression: {limit_expr}: {str(exc)}")

        op_filters.append(mk_op_filter(value_reg, fieldn))

    def filter_fn(rec):
        for op_fn in op_filters:
            if not op_fn(rec):
                return False

        return True

    filter_fn.op_filters = op_filters
    filter_fn.limits = limits

    return filter_fn
