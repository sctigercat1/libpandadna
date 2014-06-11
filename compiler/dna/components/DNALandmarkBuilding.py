from dna.base.DNAPacker import *
from dna.components import DNANode


class DNALandmarkBuilding(DNANode.DNANode):
    COMPONENT_CODE = 13

    def __init__(self, name):
        DNANode.DNANode.__init__(self, name)

        self.code = ''
        self.wallColor = (1, 1, 1, 1)
        self.title = ''
        self.article = ''
        self.buildingType = ''

    def setCode(self, code):
        self.code = code

    def setWallColor(self, color):
        self.wallColor = color

    def setTitle(self, title):
        self.title = title

    def setArticle(self, article):
        self.article = article

    def setBuildingType(self, buildingType):
        self.buildingType = buildingType

    def construct(self, dnaStore, packer):
        DNANode.DNANode.construct(self, dnaStore, packer)

        self.setCode(packer.unpack(SHORT_STRING))
        self.setWallColor(packer.unpackColor())
        self.setTitle(packer.unpack(SHORT_STRING))
        self.setArticle(packer.unpack(SHORT_STRING))
        self.setBuildingType(packer.unpack(SHORT_STRING))

        return True  # We have children.

    def traverse(self, recursive=True, verbose=False):
        packer = DNANode.DNANode.traverse(self, recursive=False, verbose=verbose)
        packer.name = 'DNALandmarkBuilding'  # Override the name for debugging.

        packer.pack('code', self.code, SHORT_STRING)
        packer.packColor('wall color', *self.wallColor)
        packer.pack('title', self.title, SHORT_STRING)
        packer.pack('article', self.article, SHORT_STRING)
        packer.pack('building type', self.buildingType, SHORT_STRING)

        if recursive:
            packer += self.traverseChildren(verbose=verbose)
        return packer
