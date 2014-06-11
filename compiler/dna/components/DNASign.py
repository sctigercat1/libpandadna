from dna.base.DNAPacker import *
import DNANode


class DNASign(DNANode.DNANode):
    COMPONENT_CODE = 5

    def __init__(self):
        DNANode.DNANode.__init__(self, '')

        self.code = ''
        self.color = (1, 1, 1, 1)

    def setCode(self, code):
        self.code = code

    def setColor(self, color):
        self.color = color

    def construct(self, dnaStore, packer):
        DNANode.DNANode.construct(self, dnaStore, packer)

        self.setCode(packer.unpack(SHORT_STRING))
        self.setColor(packer.unpackColor())

        return True  # We have children.

    def traverse(self, recursive=True, verbose=False):
        packer = DNANode.DNANode.traverse(self, recursive=False, verbose=verbose)
        packer.name = 'DNASign'  # Override the name for debugging.

        packer.pack('code', self.code, SHORT_STRING)
        packer.packColor('color', *self.color)

        if recursive:
            packer += self.traverseChildren(verbose=verbose)
        return packer
