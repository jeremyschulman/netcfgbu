#!/usr/bin/env python
#
# This script is used to retrieve the device inventory from a Netbox system and
# emil the CSV file to either stdout (default) or a filename provided
#
# The following Environment variables are REQUIRED:
#
#   NETBOX_ADDR: the URL to the NetBox server
#       "https://my-netbox-server"
#
#   NETBOX_TOKEN: the NetBox login token
#       "e0759aa0d6b4146-from-netbox-f744c4489adfec48f"
#
# The following Environment variables are OPTIONAL:
#
#   NETBOX_INVENTORY_OPTIONS
#       Same as the options provided by "--help"
#

import sys
import argparse
import os
import csv

import requests
from urllib3 import disable_warnings


disable_warnings()

options_parser = argparse.ArgumentParser()
options_parser.add_argument('--site', action='store')
options_parser.add_argument('--region', action='store')
options_parser.add_argument('--role', action='append')
options_parser.add_argument('--no-role', action='append')
options_parser.add_argument(
    '--output',
    type=argparse.FileType("w+"),
    default=sys.stdout
)


class NetBoxSession(requests.Session):

    def __init__(self, url, token):
        super(NetBoxSession, self).__init__()
        self.url = url
        self.headers['authorization'] = "Token %s" % token
        self.verify = False

    def prepare_request(self, request):
        request.url = self.url + request.url
        return super(NetBoxSession, self).prepare_request(request)


def main():

    nb_url = os.environ['NETBOX_ADDR']
    nb_token = os.environ['NETBOX_TOKEN']
    nb_env_opts = os.environ.get("NETBOX_INVENTORY_OPTIONS")
    opt_arg = nb_env_opts.split(';') if nb_env_opts else None
    nb_opts = options_parser.parse_args(opt_arg)

    params = dict(limit=0, status=1)

    if nb_opts.site:
        params['site'] = nb_opts.site

    if nb_opts.region:
        params['region'] = nb_opts.region

    netbox = NetBoxSession(url=nb_url, token=nb_token)

    res = netbox.get("/api/dcim/devices/", params=params)
    if not res.ok:
        sys.exit('FAIL: get inventory: ' + res.text)

    body = res.json()
    device_list = body['results']

    # -------------------------------------------------------------------------
    # User Filters
    # -------------------------------------------------------------------------

    # If Caller provided an explicit list of device-roles, then filter the
    # device list based on those roles before creating the inventory

    filter_functions = []

    if nb_opts.role:
        def filter_role(dev_dict):
            return dev_dict['device_role']['slug'] in nb_opts.role
        filter_functions.append(filter_role)

    if nb_opts.no_role:
        def filter_no_role(dev_dict):
            return dev_dict['device_role']['slug'] not in nb_opts.no_role
        filter_functions.append(filter_no_role)

    def apply_filters():
        for dev_dict in device_list:
            if all(fn(dev_dict) for fn in filter_functions):
                yield dev_dict

    # -------------------------------------------------------------------------
    # Create Inventory from device list
    # -------------------------------------------------------------------------

    csv_wr = csv.writer(nb_opts.output)
    csv_wr.writerow(['host', 'ipaddr', 'os_name'])

    for device in apply_filters() if filter_functions else device_list:
        hostname = device['name']

        # if the primary address or the platform value is not assigned, then
        # skip this device.

        try:
            ipaddr = device['primary_ip']['address'].split('/')[0]
            platform = device['platform']['slug']

        except (TypeError, IndexError):
            continue

            # Handle case where the platform value is unassigned

        csv_wr.writerow([hostname, ipaddr, platform])


if __name__ == '__main__':
    main()
