from dna.base.DNAPacker import *
from dna.components import DNAGroup


class DNANode(DNAGroup.DNAGroup):
    COMPONENT_CODE = 3

    def __init__(self, name):
        DNAGroup.DNAGroup.__init__(self, name)

        self.pos = (0, 0, 0)
        self.hpr = (0, 0, 0)
        self.scale = (1, 1, 1)

    def setPos(self, pos):
        self.pos = pos

    def setHpr(self, hpr):
        self.hpr = hpr

    def setScale(self, scale):
        self.scale = scale

    def traverse(self, recursive=True, verbose=False):
        packer = DNAGroup.DNAGroup.traverse(self, recursive=False, verbose=verbose)
        packer.name = 'DNANode'  # Override the name for debugging.

        packer.packPosition(*self.pos)
        packer.packRotation(*self.hpr)
        packer.packScale(*self.scale)

        if recursive:
            packer += self.traverseChildren(verbose=verbose)
        return packer
