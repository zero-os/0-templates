from js9 import j

from zerorobot.template.base import TemplateBase
from zerorobot.template.state import StateCheckError

class ZerobootIpmiHost(TemplateBase):

    version = '0.0.1'
    template_name = "zeroboot_ipmi_host"

    def __init__(self, name=None, guid=None, data=None):
        super().__init__(name=name, guid=guid, data=data)

    @property
    def _zeroboot(self):
        """ Returns zeroboot client
        
        Returns:
            ZerobootClient -- zeroboot JS client
        """
        return j.clients.zboot.get(self.data['zerobootClient'], interactive=False)

    @property
    def _network(self):
        """ Returns the zeroboot network of the host
        
        Returns:
            ZerobootClient.Network -- Zeroboot network
        """
        return self._zeroboot.networks.get(self.data['network'])

    @property
    def _ipmi(self):
        """ Returns ipmi client
        
        Returns:
            IpmiClient -- ipmi JS client
        """
        return j.clients.ipmi.get(self.data['ipmiClient'], interactive=False)

    @property
    def _host(self):
        """ Returns zeroboot host for this service
        
        Returns:
            ZerobootClient.Host -- Zeroboot Host
        """
        return self._network.hosts.get(self.data['hostname'])

    def validate(self):
        for key in ['zerobootClient', 'ipmiClient', 'ipmiClient', 'mac', 'ip', 'network', 'hostname']:
            if not self.data.get(key):
                raise ValueError("data key '%s' not specified." % key)

        # check if clients exists
        if self.data['zerobootClient'] not in j.clients.zboot.list():
            raise LookupError("No zboot client instance found named '%s'" % self.data['zerobootClient'])

        if self.data['ipmiClient'] not in j.clients.ipmi.list():
            raise LookupError("No ipmi client instance found named '%s'" % self.data['ipmiClient'])

    def install(self):
        # add host to zeroboot
        if self.data['hostname'] in self._network.hosts.list():
            if self.data['mac'] != self._host.mac:
                raise RuntimeError("Host was found in the network but mac address did not match")
            if self.data['ip'] != self._host.address:
                raise RuntimeError("Host was found in the network but ip address did not match")
        else:
            self._network.hosts.add(self.data['mac'], self.data['ip'], self.data['hostname'])

        if self.data.get('ipxeUrl'):
            self._host.configure_ipxe_boot(self.data['ipxeUrl'])

        self.state.set('actions', 'install', 'ok')
        self.data['powerState'] = self.power_status()

    def uninstall(self):
        # remove host from zeroboot
        self._network.hosts.remove(self.data['hostname'])
        self.state.delete('actions', 'install')
    
    def power_on(self):
        """ Powers on host
        """
        self.state.check('actions', 'install', 'ok')

        self._ipmi.power_on()
        self.data['powerState'] = True

    def power_off(self):
        """ Powers off host
        """
        self.state.check('actions', 'install', 'ok')
        
        self._ipmi.power_off()
        self.data['powerState'] = False

    def power_cycle(self):
        """ Power cycles host

        After a power cycle, the host will always be powered on.
        """
        self.state.check('actions', 'install', 'ok')
        
        self._ipmi.power_cycle()
        self.data['powerState'] = True

    def power_status(self):
        """ Power state of host
        
        Returns:
            bool -- True if on, False if off
        """
        self.state.check('actions', 'install', 'ok')

        status = self._ipmi.power_status()

        if status == "on":
            return True
        elif status == "off":
            return False
        else:
            raise RuntimeError("Received unexpected power state: '%s'\nExpected 'on' or 'off'" % status)

    def monitor(self):
        """Checks if the power status of the host is the same as the last called power_on/power_off action
        If the state does not match, the last power state set trough an action will be set on the host.
        """
        self.state.check('actions', 'install', 'ok')

        if self.data['powerState'] != self.power_status():
            self.logger.debug('power state did not match')
            if self.data['powerState']:
                self.logger.debug('powering on host to match internal saved power state')
                self.power_on()
            else:
                self.logger.debug('powering off host to match internally saved power state')
                self.power_off()

    def configure_ipxe_boot(self, boot_url):
        """ Configure the IPXE boot settings of the host
        
        Arguments:
            boot_url str -- url to boot from includes zerotier network id ex: http://unsecure.bootstrap.gig.tech/ipxe/zero-os-master/a84ac5c10a670ca3
        
        Keyword Arguments:
            tftp_root str -- tftp root location where pxe config are stored (default: '/opt/storage')
        """
        self.state.check('actions', 'install', 'ok')

        if boot_url == self.data.get('ipxeUrl'):
            return

        self._host.configure_ipxe_boot(boot_url)
        self.data['ipxeUrl'] = boot_url
