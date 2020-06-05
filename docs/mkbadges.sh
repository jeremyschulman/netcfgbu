#!/bin/sh

python -m pybadges \
  --left-text="python" \
  --right-text="3.8" \
  --whole-link="https://www.python.org/" \
  --embed-logo \
  --logo='https://dev.w3.org/SVG/tools/svgweb/samples/svg-files/python.svg' > py38.svg


python -m pybadges \
  --left-text="package version" \
  --right-text=$(cat ../VERSION) \
  --right-color="red" \
  --whole-link="https://www.python.org/" > version.svg
