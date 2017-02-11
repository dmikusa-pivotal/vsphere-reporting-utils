#!/usr/bin/env python
"""A script report on disk usage for all know VMs

This script will recursively search for all VMs that are visible to the
authenticated user.  It will then iterate over each VM, look at the attached
disks and report on that usage.

Current Report Options:
 - Usage by Resource Pool
"""
from __future__ import print_function
from vsphere_api import VSphereApi
from cli_helper import get_args
from collections import defaultdict


def main():
    args = get_args()

    try:
        vApi = None
        vApi = VSphereApi(args)

        # report on disk usage of resource pools
        disk_usage = defaultdict(list)
        for vm in vApi.list_all_vms():
            for disk in vm.disks:
                disk_usage[vm.resourcePool].append(disk.size)
        print("Disk Usage:")
        total = 0
        for rp in sorted(disk_usage.keys()):
            subtotal = sum(disk_usage[rp]) / 1024.0 / 1024.0 / 1024.0
            print("    RP {} -> {} GB".format(rp, subtotal))
            total += subtotal
        print("Total Usage: {} GB".format(total))
    finally:
        if vApi:
            vApi.close()


if __name__ == '__main__':
    main()
