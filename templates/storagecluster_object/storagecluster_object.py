from js9 import j

from zerorobot.template.base import TemplateBase


class StorageclusterObject(TemplateBase):

    version = '0.0.1'
    template_name = "storagecluster_object"

    def __init__(self, name=None, guid=None, data=None):
        super().__init__(name=name, guid=guid, data=data)
