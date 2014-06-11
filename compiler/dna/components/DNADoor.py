from dna.base.DNAPacker import *
from dna.components import DNAGroup


class DNADoor(DNAGroup.DNAGroup):
    COMPONENT_CODE = 17

    def __init__(self, name):
        DNAGroup.DNAGroup.__init__(self, name)

        self.code = ''
        self.color = (1, 1, 1, 1)

    def setCode(self, code):
        self.code = code

    def setColor(self, color):
        self.color = color

    def construct(self, dnaStore, packer):
        DNAGroup.DNAGroup.construct(self, dnaStore, packer)

        self.setCode(packer.unpack(SHORT_STRING))
        self.setColor(packer.unpackColor())

        return False  # We don't have children.

    def traverse(self, recursive=True, verbose=False):
        packer = DNAGroup.DNAGroup.traverse(self, recursive=False, verbose=verbose)
        packer.name = 'DNADoor'  # Override the name for debugging.

        packer.pack('code', self.code, SHORT_STRING)
        packer.packColor('color', *self.color)

        return packer
