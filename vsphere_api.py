import ssl
import time

from vsphere_objects import Vm, Disk, DsFile, VSphereObjectStore
from pyVim import connect
from pyVmomi import vim
from Queue import Queue, Empty
from threading import Thread


class VSphereApi:
    def __init__(self, args):
        self.args = args
        self.service_instance = None
        self.objStore = VSphereObjectStore()

        # setup SSL context
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        ssl_context.verify_mode = ssl.CERT_NONE \
            if args.disable_ssl_verification else ssl.CERT_REQUIRED

        # setup vSphere connection
        if not args.cache or (args.cache and (
                not self.objStore.vms_cache_exists() or
                not self.objStore.files_cache_exists())):
            self.service_instance = connect.SmartConnect(
                host=args.host,
                user=args.user,
                pwd=args.password,
                port=int(args.port),
                sslContext=ssl_context)

    def close(self):
        if self.service_instance:
            connect.Disconnect(self.service_instance)

    def list_all_vms(self):
        # load list of vms from vSphere or cache
        if self.args.cache and self.objStore.vms_cache_exists():
            vms = self.objStore.load_list_of_vms_from_json()
        else:
            vms = self.load_all_vms_from_api()
            if self.args.cache:
                self.objStore.save_list_of_vms_to_json(vms)
        return vms

    def load_all_vms_from_api(self):
        content = self.service_instance.RetrieveContent()
        container = content.rootFolder  # starting point to look into
        viewType = [vim.VirtualMachine]  # object types to look for
        recursive = True  # whether we should look into it recursively

        containerView = content.viewManager.CreateContainerView(
            container, viewType, recursive)

        # initialize queue and worker threads
        q = Queue()
        done = False

        def handle_vm(ctx, vm):
            summary = vm.summary
            devices = vm.config.hardware.device
            vm_rec = Vm(
                name=summary.config.name,
                path=summary.config.vmPathName,
                resourcePool=vm.resourcePool.name if vm.resourcePool else None,
                state=summary.runtime.powerState,
                ip=summary.guest.ipAddress,
                disks=[])
            for disk in devices:
                if type(disk) == vim.vm.device.VirtualDisk:
                    dt = "thin" if disk.backing.thinProvisioned else "thick"
                    vm_rec.disks.append(
                        Disk(label=disk.deviceInfo.label,
                             summary=disk.deviceInfo.summary,
                             path=disk.backing.fileName,
                             size=disk.capacityInBytes,
                             mode=disk.backing.diskMode,
                             type=dt))
            ctx.append(vm_rec)
            print("Located vm [{}]".format(vm_rec.name))

        def worker():
            while not done:
                try:
                    (ctx, vm) = q.get(True, 1)
                    handle_vm(ctx, vm)
                    q.task_done()
                except Empty:
                    pass

        threads = []
        for i in range(15):
            t = Thread(target=worker)
            t.start()
            threads.append(t)

        # load up the queue with work
        # Note: ctx is shared across all worker threads,
        #   but it's a list and we're only appending so it should be OK
        #     https://stackoverflow.com/questions/6319207/are-lists-thread-safe
        ctx = []
        for child in containerView.view:
            q.put((ctx, child))

        # wait for it to finish & clean up threads
        q.join()
        done = True
        [th.join() for th in threads]
        return ctx

    def list_all_files(self):
        # load list of files from vSphere or cache
        if self.args.cache and self.objStore.files_cache_exists():
            files = self.objStore.load_list_of_files_from_json()
        else:
            # can use `load_all_files_from_search_api` instead
            files = self.load_all_files_from_api()
            if self.args.cache:
                self.objStore.save_list_of_files_to_json(files)
        return files

    def load_all_files_from_search_api(self):
        """Loads all files using a recursive search run on all datastores

        Logically this is pretty simple.  Just point it at the datastore and
        search recursively for all files.
        """
        content = self.service_instance.RetrieveContent()
        container = content.rootFolder  # starting point to look into
        viewType = [vim.Datastore]  # object types to look for
        recursive = True  # whether we should look into it recursively

        containerView = content.viewManager.CreateContainerView(
            container, viewType, recursive)

        def handle_datastore(ctx, ds):
            # configure search to return all files and size of each
            search = vim.host.DatastoreBrowser.SearchSpec()
            search.details = vim.host.DatastoreBrowser.FileInfo.Details()
            search.details.fileType = True
            search.details.fileSize = True
            search.details.modification = False
            search.details.fileOwner = False
            search.query.append(vim.host.DatastoreBrowser.Query)

            # caching this property because accessing it triggers an HTTP
            #  request and the name doesn't change since we're searching
            #  a specific datastore
            dsName = ds.name

            # search starting from the root of our datasource recursive
            print("Searching for all files on [{}]".format(dsName))
            search_req = ds.browser.SearchSubFolders(
                "[{}] /".format(dsName), search)
            count = 0
            while search_req.info.state != "success":
                time.sleep(1.0)  # wait a bit so we don't hammer the server
                count += 1
                if count % 60 == 0:
                    print("Still running after {} secs".format(count))

            # search has finished.
            #  it returns a list of results, each of which has files
            results = search_req.info.result
            for result in results:
                if result.folderPath == '[LUN01]':
                    # skip this node which just lists all the top level folders
                    continue
                if hasattr(result, 'file'):
                    for f in result.file:
                        if hasattr(f, 'path'):
                            dsf = DsFile(
                                datastore=dsName,
                                pathTo=result.folderPath,
                                fileName=f.path,
                                size=f.fileSize)
                            ctx.append(dsf)
                            print("Located file {} /{}".format(
                                dsf.pathTo, dsf.fileName))
                        else:
                            print("Not a file [{}]".format(f))
                else:
                    print("No files [{}]".format(result))

        ctx = []
        for child in containerView.view:
            handle_datastore(ctx, child)
        return ctx

    def find_datastore_by_name(self, name):
        content = self.service_instance.RetrieveContent()
        container = content.rootFolder  # starting point to look into
        viewType = [vim.Datastore]  # object types to look for
        recursive = True  # whether we should look into it recursively
        containerView = content.viewManager.CreateContainerView(
            container, viewType, recursive)
        for ds in containerView.view:
            if ds.name == name:
                return ds

    def load_all_files_from_ds_under_path(self, ds, underPath):
        # caching this property because accessing it triggers an HTTP
        #  request and the name doesn't change since we're searching
        #  a specific datastore
        dsName = ds.name

        # configure search to return all files and size of each
        search = vim.host.DatastoreBrowser.SearchSpec()
        search.details = vim.host.DatastoreBrowser.FileInfo.Details()
        search.details.fileType = True
        search.details.fileSize = True
        search.details.modification = True
        search.details.fileOwner = True
        search.query.append(vim.host.DatastoreBrowser.Query)

        # list only the files in underPath
        print("Searching for all files on [{}] {}".format(
            dsName, underPath))
        search_req = ds.browser.Search(
            "[{}] {}".format(dsName, underPath), search)
        count = 0
        while search_req.info.state != "success":
            if search_req.info.state == "error":
                print("Lookup failed [{}]".format(search_req.info.error.msg))
                return []
            time.sleep(1.0)  # wait a bit so we don't hammer the server
            count += 1
            if count % 60 == 0:
                print("Not finished after {} secs -> {}".format(
                    count, search_req.info.state))

        # search has finished.
        #  it returns a list of results, each of which has files
        ctx = []
        results = search_req.info.result
        for f in results.file:
            dsf = DsFile(
                datastore=dsName,
                pathTo=results.folderPath.strip(),
                fileName=f.path.strip(),
                size=f.fileSize)
            ctx.append(dsf)
            print("Located file {} {}".format(dsf.pathTo, dsf.fileName))
        return ctx

    def load_all_files_from_api(self):
        """Load all files by submitting multiple smaller search requests.

        Starts by loading the root level of each datastore, which this assumes
        is all folders (assumes based on standard way of storing VMs).  Then
        for each folder in the root level, we issue another search that loads
        just the contents of that sub folder.  We combine all the results into
        one list.

        This should in theory do the same thing as the method
        `load_all_files_from_search_api`, but more testing needs to be done to
        confirm.
        """
        ds = self.find_datastore_by_name('LUN01')
        q = Queue()
        done = False

        def worker():
            while not done:
                try:
                    (ctx, path) = q.get(True, 1)
                    newFiles = self.load_all_files_from_ds_under_path(ds, path)
                    print("Adding {} new files".format(len(newFiles)))
                    ctx.extend(newFiles)
                    q.task_done()
                except Empty:
                    pass

        threads = []
        for i in range(15):
            t = Thread(target=worker)
            t.start()
            threads.append(t)

        # load up the queue with work
        # Note: ctx is shared across all worker threads,
        #   but it's a list and we're only appending so it should be OK
        #     https://stackoverflow.com/questions/6319207/are-lists-thread-safe
        ctx = []
        for f in self.load_all_files_from_ds_under_path(ds, '/'):
            q.put((ctx, f.fileName))

        # wait for it to finish & clean up threads
        q.join()
        done = True
        [th.join() for th in threads]
        return ctx
