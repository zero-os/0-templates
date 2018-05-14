from js9 import j

from zerorobot.template.base import TemplateBase
from zerorobot.template.state import StateCheckError

class ZerobootHost(TemplateBase):

    version = '0.0.1'
    template_name = "zeroboot_host"

    def __init__(self, name=None, guid=None, data=None):
        super().__init__(name=name, guid=guid, data=data)

        self._power_state = None

    @property
    def _zeroboot(self):
        """ Returns zeroboot client
        
        Returns:
            ZerobootClient -- zeroboot JS client
        """
        return j.clients.zboot.get(self.data['zerobootClient'], interactive=False)
    
    @property
    def _racktivity(self):
        """ Returns Racktivity client
        
        Returns:
            RacktivityClient -- racktivity JS client
        """
        return j.clients.racktivity.get(self.data['racktivityClient'], interactive=False)

    @property
    def _powermodule_id(self):
        """ Returns the Racktivity power module id
        returns None if empty.
        
        Returns:
            str -- Racktivity powermodule ID
        """
        return self.data['racktivityPowerModule'] if self.data['racktivityPowerModule'] != "" else None

    @property
    def _network(self):
        """ Returns the zeroboot network of the host
        
        Returns:
            ZerobootClient.Network -- Zeroboot network
        """
        return self._zeroboot.networks.get('network')

    @property
    def _host(self):
        """ Returns zeroboot host for this service
        
        Returns:
            ZerobootClient.Host -- Zeroboot Host
        """
        return self._network.hosts.get(self.data['hostname'])

    def validate(self):
        if not self.data['zerobootClient']:
            raise ValueError("No zeroboot instance specified (zerobootClient)")

        if not self.data['racktivityClient']:
            raise ValueError("No Racktivity instance specified (racktivityClient)")

        if not self.data['network']:
            raise ValueError("No network specified")

        if not self.data['mac']:
            raise ValueError("No mac specified")

        if not self.data['ip']:
            raise ValueError("No ip specified")

        if not self.data['hostname']:
            raise ValueError("No hostname specified")

        if not self.data['ipxeUrl']:
            raise ValueError("No ipxeUrl specified")

        if not self.data['racktivityPort']:
            raise ValueError("No Racktivity port for the host specified (racktivityPort)")

        # check if clients exists
        if self.data['zerobootClient'] not in j.clients.zboot.list():
            raise RuntimeError("No zboot client instance found named '%s'" % self.data['zerobootClient'])

        if self.data['racktivityClient'] not in j.clients.racktivity.list():
            raise RuntimeError("No racktivity client instance found named '%s'" % self.data['racktivityClient'])

    def install(self):
        # add host to zeroboot
        if self.data['hostname'] in self._network.hosts.list():
            if self.data['mac'] != self._host.mac:
                raise RuntimeError("Host was found in the network but mac address did not match")
            if self.data['ip'] != self._host.ip:
                raise RuntimeError("Host was found in the network but ip address did not match")
        else:
            self._network.hosts.add(self.data['mac'], self.data['ip'], self.data['hostname'])

        self._host.configure_ipxe_boot(self.data['ipxeUrl'])

        self.state.set('actions', 'install', 'ok')
        self._powerstate = self.power_status()

    def uninstall(self):
        # remove host from zeroboot
        self._network.hosts.remove(self.data['hostname'])
        self.state.delete('actions', 'install')
    
    def power_on(self):
        """ Powers on host
        """
        self.state.check('actions', 'install', 'ok')

        self._zeroboot.port_power_on(self.data['racktivityPort'], self._racktivity, self._powermodule_id)
        self._powerstate = True

    def power_off(self):
        """ Powers off host
        """
        self.state.check('actions', 'install', 'ok')
        
        self._zeroboot.port_power_off(self.data['racktivityPort'], self._racktivity, self._powermodule_id)
        self._powerstate = False

    def power_cycle(self):
        """ Power cycles host
        """
        self.state.check('actions', 'install', 'ok')
        
        self._zeroboot.port_power_cycle([self.data['racktivityPort']], self._racktivity, self._powermodule_id)

    def power_status(self):
        """ Power state of host
        
        Returns:
            bool -- True if on, False if off
        """
        self.state.check('actions', 'install', 'ok')

        return self._zeroboot.port_info(self.data['racktivityPort'], self._racktivity, self._powermodule_id)[1]

    def monitor(self):
        """Checks if the power status of the host is the same as the last called power_on/power_off action
        If the state does not match, the last power state set trough an action will be set on the host.
        """
        self.state.check('actions', 'install', 'ok')

        if self._power_state != self.power_status():
            self.logger.debug('power state did not match')
            if self._power_state:
                self.logger.debug('powering on host to match internal saved power state')
                self.power_on()
            else:
                self.logger.debug('powering off host to match internally saved power state')
                self.power_off()

    def configure_ipxe_boot(self, boot_url):
        """ Configure the IPXE boot settings of the host
        
        Arguments:
            boot_url str -- url to boot from includes zerotier netowrk id ex: http://unsecure.bootstrap.gig.tech/ipxe/zero-os-master/a84ac5c10a670ca3
        
        Keyword Arguments:
            tftp_root str -- tftp root location where pxe config are stored (default: '/opt/storage')
        """
        self.state.check('actions', 'install', 'ok')

        if boot_url == self.data['ipxeUrl']:
            return

        self._host.configure_ipxe_boot(boot_url)
        self.data['ipxeUrl'] = boot_url
