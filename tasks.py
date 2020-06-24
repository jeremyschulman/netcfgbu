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

PYTHON_PATHS = ["netcfgbu/", "bin/netcfgbu", "netbox/*.py", "tests/*.py"]


@task
def lint(ctx):
    ctx.run("black .")
    ctx.run("flake8 .")
    # for each in PYTHON_PATHS:
    #     ctx.run(f"black {each}")
    #     ctx.run(f"flake8 {each}")


@task
def clean(ctx):
    ctx.run("python setup.py clean")
    ctx.run("rm -rf netcfgbu.egg-info")
    ctx.run("rm -rf .pytest_cache .pytest_tmpdir")
    ctx.run("rm -rf htmlcov")
