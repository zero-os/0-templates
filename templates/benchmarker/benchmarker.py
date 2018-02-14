from js9 import j
from zerorobot.template.base import TemplateBase
import os


class Benchmarker(TemplateBase):

    version = '0.0.1'
    template_name = 'node'

    def __init__(self, name, guid=None, data=None):
        super().__init__(name=name, guid=guid, data=data)

    def validate(self):
        self.logger.info("validate")

    def benchmark(self, size=4096):
        return j.data.idgenerator.generateXCharID(size)
