# Some lightweight data types
import json
import os.path
from collections import namedtuple

Vm = namedtuple('Vm', ['name',
                       'path',
                       'resourcePool',
                       'state',
                       'ip',
                       'disks'])
Disk = namedtuple('Disk', ['label',
                           'summary',
                           'path',
                           'size',
                           'mode',
                           'type'])
DsFile = namedtuple('DsFile', ['datastore', 'pathTo', 'fileName', 'size'])


class VSphereObjectStore:
    VMS_CACHE_FILE = 'vms.json'
    FILES_CACHE_FILE = 'files.json'

    def vms_cache_exists(self):
        return os.path.exists(self.VMS_CACHE_FILE)

    def files_cache_exists(self):
        return os.path.exists(self.FILES_CACHE_FILE)

    def save_list_of_vms_to_json(self, vms):
        json.dump(vms, open(self.VMS_CACHE_FILE, 'w'))

    def save_list_of_files_to_json(self, files):
        json.dump(files, open(self.FILES_CACHE_FILE, 'w'))

    def load_list_of_vms_from_json(self):
        vms_json = json.load(open(self.VMS_CACHE_FILE))
        vms = []
        for vm in vms_json:
            vm_rec = Vm._make(vm[0:5] + [[]])
            for disk in vm[5]:
                vm_rec.disks.append(Disk._make(disk))
            vms.append(vm_rec)
        return vms

    def load_list_of_files_from_json(self, fileName):
        files_json = json.load(open(self.FILES_CACHE_FILE))
        return [DsFile._make(f) for f in files_json]
