from dna.base.DNAPacker import *
from dna.components import DNANode


class DNAFlatBuilding(DNANode.DNANode):
    COMPONENT_CODE = 9

    def __init__(self, name):
        DNANode.DNANode.__init__(self, name)

        self.width = 0
        self.hasDoor = False

    def setWidth(self, width):
        self.width = width

    def setHasDoor(self, hasDoor):
        self.hasDoor = True

    def construct(self, dnaStore, packer):
        DNANode.DNANode.construct(self, dnaStore, packer)

        self.setWidth(packer.unpack(UINT8))
        self.setHasDoor(packer.unpack(BOOLEAN))

        return True  # We have children.

    def traverse(self, recursive=True, verbose=False):
        packer = DNANode.DNANode.traverse(self, recursive=False, verbose=verbose)
        packer.name = 'DNAFlatBuilding'  # Override the name for debugging.

        packer.pack('width', self.width, UINT8)
        packer.pack('has door', self.hasDoor, BOOLEAN)

        if recursive:
            packer += self.traverseChildren(verbose=verbose)
        return packer
