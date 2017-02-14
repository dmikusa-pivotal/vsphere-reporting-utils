#!/usr/bin/env python
"""A script report on disk usage for all know VMs

This script will recursively search for all VMs that are visible to the
authenticated user.  It will then iterate over each VM, look at the attached
disks and report on that usage.

Current Report Options:
 - Usage by Resource Pool
"""
from __future__ import print_function
from operator import itemgetter
from vsphere_api import VSphereApi
from cli_helper import ArgBuilder
from collections import defaultdict
from utils import convert_size


def main():
    ab = ArgBuilder()
    ab.add_argument(
        '-s', '--sort',
        default='size',
        action='store',
        help='Sort order: resource_pool or size')
    args = ab.process_args()
    sort_order = 0 if args.sort == 'resource_pool' else 1

    try:
        vApi = None
        vApi = VSphereApi(args)

        # report on disk usage of resource pools
        disk_usage = defaultdict(int)
        total = 0
        for vm in vApi.list_all_vms():
            for disk in vm.disks:
                disk_usage[vm.resourcePool] += disk.size
                total += disk.size

        print("Disk Usage:")
        for row in sorted(disk_usage.items(),
                          key=itemgetter(sort_order),
                          reverse=sort_order != 0):
            print("    RP {:20} -> {}".format(
                row[0], convert_size(row[1])))
        print("Total Usage: {}".format(convert_size(total)))
    finally:
        if vApi:
            vApi.close()


if __name__ == '__main__':
    main()
