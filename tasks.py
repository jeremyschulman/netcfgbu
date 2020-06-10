#!/usr/bin/env python
#
# For use with the invoke tool, see: http://www.pyinvoke.org/
#
# References
# ----------
#
# Black:
# Flake8: https://flake8.pycqa.org/en/latest/user/configuration.html


from invoke import task

PYTHON_PATHS = [
    'netcfgbu/',
    'bin/netcfgbu',
    'netbox/*.py'
]


@task
def lint(ctx):
    for each in PYTHON_PATHS:
        ctx.run(f"black {each}")
        ctx.run(f"flake8 {each}")
