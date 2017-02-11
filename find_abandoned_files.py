#!/usr/bin/env python
"""A script to find abandoned files on a vSphere datastore

This script will search through a vSphere datastore and look at what files
are present there.  It will then compare those to any VMs that it sees in the
environment.  Anything left unaccounted for will be determined to be abandoned.

This script makes a few assumptions.  The primary being that the datastore is
organized with a top level of folders where the folder name matches the VM
name and then files specific to that VM are under the top level folder.  This
is the standard way vSphere organizes the files.  Thus if you have a folder
named XYZ and a VM named XYZ exists then the folder and everything under it
are files considered to be still active.

The script will also look at all of the disks attached to a VM.  If there are
disks attached to a VM that are outside of the VM folder it will mark those as
still active too.

At the end of the script, anything not marked active is considered abandoned.
The script will print out a list of these files and the file sizes so that you
can get a picture for how much space is being consumed by abandoned files.
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

        files = vApi.list_all_files()
        vms = vApi.list_all_vms()

        # TODO: work out algorithm to detect disk files not attached to a VM
        disk_usage = defaultdict(list)
        for vm in vms:
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
