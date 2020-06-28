import asyncio

from collections import defaultdict
from errno import errorcode
import csv
from time import monotonic
from datetime import datetime

from tabulate import tabulate

LN_SEP = "# " + "-" * 78
SPACES_4 = " " * 4


def err_reason(exc):
    return {
        str: lambda: exc,
        asyncio.TimeoutError: lambda: "TIMEOUT%s" % (str(exc.args or "")),
        OSError: lambda: errorcode[exc.errno],
    }.get(exc.__class__, lambda: "%s: %s" % (str(exc.__class__.__name__), str(exc)))()


class Report(object):
    TIME_FORMAT = "%Y-%b-%d %I:%M:%S %p"

    def __init__(self):
        self.start_ts = None
        self.start_tm = 0

        self.stop_ts = None
        self.stop_tm = 0

        self.task_results = defaultdict(list)

    def start_timing(self):
        self.start_ts = datetime.now()
        self.start_tm = monotonic()

    def stop_timing(self):
        self.stop_ts = datetime.now()
        self.stop_tm = monotonic()

    @property
    def start_time(self):
        return self.start_ts.strftime(self.TIME_FORMAT)

    @property
    def stop_time(self):
        return self.stop_ts.strftime(self.TIME_FORMAT)

    @property
    def duration(self):
        return self.stop_tm - self.start_tm

    def print_report(self):
        if not self.stop_tm:
            self.stop_timing()  # pragma: no cover

        fail_n = len(self.task_results[False])
        ok_n = len(self.task_results[True])

        total_n = ok_n + fail_n

        print(LN_SEP)

        print(
            f"Summary: TOTAL={total_n}, OK={ok_n}, FAIL={fail_n}\n"
            f"         START={self.start_time}, STOP={self.stop_time}\n"
            f"         DURATION={self.duration:.3f}s"
        )

        headers = ["host", "os_name", "reason"]

        failure_tabular_data = [
            [rec["host"], rec["os_name"], err_reason(exc)]
            for rec, exc in self.task_results[False]
        ]

        if not fail_n:
            print(LN_SEP)
            return

        with open("failures.csv", "w+") as ofile:
            wr_csv = csv.writer(ofile)
            wr_csv.writerow(headers)
            wr_csv.writerows(failure_tabular_data)

        print(f"\n\nFAILURES: {fail_n}")
        print(tabulate(headers=headers, tabular_data=failure_tabular_data))
        print(LN_SEP)
