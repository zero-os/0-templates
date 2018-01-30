from js9 import j

from zerorobot.template.base import TemplateBase

from http.client import HTTPSConnection


class HardwareCheck(TemplateBase):

    version = '0.0.1'
    template_name = 'hardware_check'

    def __init__(self, name=None, guid=None, data=None):
        super().__init__(name=name, guid=guid, data=data)
        self._validate_input()

    def _validate_input(self):
        for param in ['numhdd', 'numssd', 'ram', 'cpu', 'botid', 'chatid']:
            if not self.data[param]:
                raise ValueError("parameter '%s' not valid: %s",
                                 str(self.data[param]))

    def check(self, node_name):
        ssd_count = 0
        hdd_count = 0
        cl = j.clients.zero_os.get(instance=node_name)

        conn = HTTPSConnection('api.telegram.org')
        botid = self.data['botid']
        chatid = self.data['chatid']

        try:
            # check disks
            for disk in cl.disk.list()['blockdevices']:
                # ignore the boot usb drive
                if disk.get('tran') == 'usb':
                    continue

                # check disk type
                if disk.get('rota') == '1':
                    hdd_count += 1
                else:
                    ssd_count += 1

                # do drive test
                name = disk.get('name')
                num_sectors = int(disk.get('size')) // int(disk.get('phy-sec'))
                test_sectors = [1, num_sectors // 2, num_sectors - 1]

                cl.bash('echo test > /test')
                for sector in test_sectors:
                    # write to sector
                    cmd = 'dd if=/test of=/dev/{} seek={}'.format(name, sector)
                    cl.system(cmd).get()
                    # read from sector
                    cmd = 'dd if=/dev/{} bs=1 count=4 skip={}'.format(
                        name, sector * 512)
                    result = cl.system(cmd).get().stdout
                    if result != 'test\n':
                        raise j.exceptions.RuntimeError(
                            "Hardwaretest drive /dev/{} failed.".format(name))

            ssd_num = self.data['numssd']
            if ssd_count != ssd_num:
                raise j.exceptions.RuntimeError(
                    "Number of ssds is not as expected. Found {} ssd(s) instead of {}".format(ssd_count, ssd_num))

            hdd_num = self.data['numhdd']
            if hdd_count != hdd_num:
                raise j.exceptions.RuntimeError(
                    "Number of hdds is not as expected. Found {} hdd(s) instead of {}".format(hdd_count, hdd_num))

            # check ram
            ram = cl.info.mem().get('total')
            ram_mib = ram // 1024 // 1024
            exp_ram_mib = self.data['ram']
            if ram_mib < exp_ram_mib - 5:
                raise j.exceptions.RuntimeError(
                    "The total amount of ram is not as expected. Found {} MiB instead of more than {} MiB".format(ram_mib, exp_ram_mib))

            # check cpu
            cpu = cl.info.cpu()[0].get('modelName').split()[2]
            exp_cpu = self.data['cpu']
            if cpu != exp_cpu:
                raise j.exceptions.RuntimeError(
                    "The cpu is not as expected. Found {} instead of {}".format(cpu, exp_cpu))

            self.logger.info("Hardware check succeeded")
            message = "Node with id {} has completed the hardwarecheck successfully.".format(
                node_name)
        except Exception as err:
            message = "Node with id {} has failed the hardwarecheck: {}".format(
                node_name, str(err))
            raise j.exceptions.RuntimeError(message)
        finally:
            url = "/bot{}/sendMessage?chat_id={}&text={}".format(
                botid, chatid, message)
            conn.request("GET", url)
