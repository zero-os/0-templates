from js9 import j

from zerorobot.template.base import TemplateBase
from zerorobot.template.state import StateCheckError


class ZerobootReservation(TemplateBase):

    version = '0.0.1'
    template_name = "zeroboot_reservation"

    def __init__(self, name=None, guid=None, data=None):
        super().__init__(name=name, guid=guid, data=data)

        self._pool = None

    def validate(self):
        if self.data['zerobootHost']:
            raise ValueError("zerobootHost can not be specified")
        
        self._pool = self.api.services.get(name=self.data['zerobootPool'])

    def install(self):
        """ Install the reservation

        Fetches a free host from the pool and reserves it.
        Powers on the host
        """
        self.data["zerobootHost"] = self._pool.schedule_action("unreserved_host", args={'caller_guid': self.guid}).wait(die=True).result

        self.state.set('actions', 'install', 'ok')
        self.power_on()

    def uninstall(self):
        """ Uninstalls the reservation

        Powers off the host and releases the leases the host.
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

        return self.api.services.get(name=self.data['zerobootHost']).schedule_action('power_on').wait(die=True).result

    def power_off(self):
        """ Powers off the reserved host
        """
        self.state.check('actions', 'install', 'ok')

        return self.api.services.get(name=self.data['zerobootHost']).schedule_action('power_off').wait(die=True).result

    def power_cycle(self):
        """ Powers cycles the reserved host
        """
        self.state.check('actions', 'install', 'ok')
        
        return self.api.services.get(name=self.data['zerobootHost']).schedule_action('power_cycle').wait(die=True).result

    def power_status(self):
        """ Returns the power status of the reserved host
        
        Returns:
            bool -- True if on, False if off
        """
        self.state.check('actions', 'install', 'ok')
        
        return self.api.services.get(name=self.data['zerobootHost']).schedule_action('power_status').wait(die=True).result
