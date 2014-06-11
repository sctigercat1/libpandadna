from dna.base.DNAPacker import *
from dna.components import DNANode


class DNASignText(DNANode.DNANode):
    COMPONENT_CODE = 7

    def __init__(self):
        DNANode.DNANode.__init__(self, '')

        self.letters = ''

    def setLetters(self, letters):
        self.letters = letters

    def construct(self, dnaStore, packer):
        DNANode.DNANode.construct(self, dnaStore, packer)

        self.setLetters(packer.unpack(SHORT_STRING))

        return False  # We don't have children.

    def traverse(self, recursive=True, verbose=False):
        packer = DNANode.DNANode.traverse(self, recursive=False, verbose=verbose)
        packer.name = 'DNASignText'  # Override the name for debugging.

        packer.pack('letters', self.letters, SHORT_STRING)

        return packer
