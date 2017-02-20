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

import os.path

from vsphere_api import VSphereApi
from cli_helper import ArgBuilder


def parse_ignore_list(args):
    if not args.ignore:
        args.ignore = []
    if args.ignore_path:
        if not os.path.exists(args.ignore_path):
            print("[WARNING] ignore file does not exist, skipping")
        else:
            lines = open(args.ignore_path, 'r').readlines()
            args.ignore.extend([line.strip() for line in lines])


def main():
    ab = ArgBuilder()
    ab.add_argument(
        '-i', '--ignore',
        required=False,
        action='append',
        help='list of directory paths to ignore')
    ab.add_argument(
        '--ignore_path',
        required=False,
        action='store',
        help='path to a file of directories to ignore')
    args = ab.process_args()
    parse_ignore_list(args)

    try:
        vApi = None
        vApi = VSphereApi(args)

        files = vApi.list_all_files()
        vms = vApi.list_all_vms()

        # skip certain files
        files = [f for f in files
                 if not any([f.pathTo.find(s) != -1 for s in args.ignore])]

        print()
        print("Unaccounted file count [{}]".format(len(files)))
        print("Removing known VMs from the list...")
        for vm in vms:
            newFiles = []
            for f in files:
                # remove paths starting with VM name
                if f.pathTo == '[{}] {}/'.format(f.datastore, vm.name):
                    continue
                # remove other references to VM files
                vmDisksLoc = vm.path.split('/')[0]
                if f.pathTo == '{}/'.format(vmDisksLoc):
                    continue
                # remove attached disks
                if any([os.path.join(f.pathTo, f.fileName) == disk.path
                        for disk in vm.disks]):
                    continue
                newFiles.append(f)
            files = newFiles

        print()
        print("The following files are left ({}):".format(len(files)))
        for f in files:
            print("    {}".format(os.path.join(f.pathTo, f.fileName)))
    finally:
        if vApi:
            vApi.close()


if __name__ == '__main__':
    main()
