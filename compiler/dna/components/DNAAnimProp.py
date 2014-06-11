from dna.base.DNAPacker import *
from dna.components import DNAProp


class DNAAnimProp(DNAProp.DNAProp):
    COMPONENT_CODE = 14

    def __init__(self, name):
        DNAProp.DNAProp.__init__(self, name)

        self.animName = ''

    def setAnimName(self, anim):
        self.animName = anim

    def construct(self, dnaStore, packer):
        DNAProp.DNAProp.construct(self, dnaStore, packer)

        self.setAnimName(packer.unpack(SHORT_STRING))

        return True  # We have children.

    def traverse(self, recursive=True, verbose=False):
        packer = DNAProp.DNAProp.traverse(self, recursive=False, verbose=verbose)
        packer.name = 'DNAAnimProp'  # Override the name for debugging.

        packer.pack('anim name', self.animName, SHORT_STRING)

        if recursive:
            packer += self.traverseChildren(verbose=verbose)
        return packer
