from js9 import j

from zerorobot.template.base import TemplateBase
from zerorobot.template.state import StateCheckError


class ZerobootReservation(TemplateBase):

    version = '0.0.1'
    template_name = "zeroboot_reservation"

    def __init__(self, name=None, guid=None, data=None):
        super().__init__(name=name, guid=guid, data=data)

    @property
    def _pool(self):
        """ Returns pool service
        
        Returns:
            ServiceProxy -- zeroboot pool service
        """
        return self.api.services.get(name=self.data['zerobootPool'])

    @property
    def _host(self):
        """ Returns host service
        
        Returns:
            ServiceProxy -- host service
        """
        return self.api.services.get(name=self.data['zerobootHost'])

    def validate(self):
        for key in ['zerobootPool', 'ipxeUrl']:
            if not self.data.get(key):
                raise ValueError("data key '%s' not specified." % key)

        # zerobootHost can only be set when installed
        try:
            self.state.check('actions', 'install', 'ok')
            if not self.data.get('zerobootHost'):
                raise ValueError("zerobootHost is not set while installed")
        except StateCheckError:
            if self.data.get('zerobootHost'):
                raise ValueError("zerobootHost can not only be set when installed")

    def install(self):
        """ Install the reservation

        Fetches a free host from the pool and reserves it.
        Powers on the host
        """
        self.data["zerobootHost"] = self._pool.schedule_action("unreserved_host", args={'caller_guid': self.guid}).wait(die=True).result

        # configure ipxe
        self._host.schedule_action('configure_ipxe_boot', args={'boot_url': self.data['ipxeUrl']}).wait(die=True)
        self._host.schedule_action('power_cycle').wait(die=True)

        self.state.set('actions', 'install', 'ok')

    def uninstall(self):
        """ Uninstalls the reservation

        Powers off the host and releases the lease on the host.
        """
        self.power_off()
        self.data["zerobootHost"] = None

        self.state.delete('actions', 'install')

    def host(self):
        """Returns the reserved hostname
        
        Returns:
            str -- Hostname of the reserved host
        """
        self.state.check('actions', 'install', 'ok')

        return self.data['zerobootHost']

    def power_on(self):
        """ Powers on the reserved host
        """
        self.state.check('actions', 'install', 'ok')

        return self._host.schedule_action('power_on').wait(die=True).result

    def power_off(self):
        """ Powers off the reserved host
        """
        self.state.check('actions', 'install', 'ok')

        return self._host.schedule_action('power_off').wait(die=True).result

    def power_cycle(self):
        """ Powers cycles the reserved host
        """
        self.state.check('actions', 'install', 'ok')
        
        return self._host.schedule_action('power_cycle').wait(die=True).result

    def power_status(self):
        """ Returns the power status of the reserved host
        
        Returns:
            bool -- True if on, False if off
        """
        self.state.check('actions', 'install', 'ok')
        
        return self._host.schedule_action('power_status').wait(die=True).result

    def monitor(self):
        """ Checks if the power status of the host is the same as the last called power_on/power_off action.
        If the state does not match, the last power state set trough an action will be set on the host.
        """
        self.state.check('actions', 'install', 'ok')

        return self._host.schedule_action('monitor').wait(die=True).result

    def configure_ipxe_boot(self, boot_url):
        """ Sets the ipxe boot url of the host

        May need a power_cycle to boot from the url.
        
        Arguments:
            boot_url str -- URL of the ipxe boot script
        """
        self.state.check('actions', 'install', 'ok')

        self._host.schedule_action('configure_ipxe_boot', args={'boot_url': boot_url}).wait(die=True)
