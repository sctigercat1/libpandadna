from dna.base.DNAPacker import *
from dna.components import DNALandmarkBuilding


class DNAAnimBuilding(DNALandmarkBuilding.DNALandmarkBuilding):
    COMPONENT_CODE = 16

    def __init__(self, name):
        DNALandmarkBuilding.DNALandmarkBuilding.__init__(self, name)

        self.animName = ''

    def setAnimName(self, anim):
        self.animName = anim

    def construct(self, dnaStore, packer):
        DNALandmarkBuilding.DNALandmarkBuilding.construct(self, dnaStore, packer)

        self.setAnimName(packer.unpack(SHORT_STRING))

        return True  # We have children.

    def traverse(self, recursive=True, verbose=False):
        packer = DNALandmarkBuilding.DNALandmarkBuilding.traverse(
            self, recursive=False, verbose=verbose)
        packer.name = 'DNAAnimBuilding'  # Override the name for debugging.

        packer.pack('anim name', self.animName, SHORT_STRING)

        if recursive:
            packer += self.traverseChildren(verbose=verbose)
        return packer
