import os
import sys


# We need some of the modules included in the compiler utility:
sys.path.append(os.path.abspath('../compiler'))


from StringIO import StringIO
from dna.base import DNAStorage
from dna.base.DNAPacker import *
from dna.components import DNABattleCell
from dna.components import DNARoot
from dna.components import DNASuitPoint
from dna.parser.tokens import *
from ply import lex


HEADER_LENGTH = 7
HEADER = 'PDNA\n{compressed}\n'


class DNAError(Exception):
    pass
__builtins__['DNAError'] = DNAError


lex.lex(optimize=0)


class Compiler:
    def __init__(self, data, compress=False):
        self.data = data
        self.compress = compress

        self.dnaStore = DNAStorage.DNAStorage()

    def compile(self):
        stream = StringIO(self.data)
        root = DNARoot.DNARoot(name='root', dnaStore=self.dnaStore)
        root.read(stream)
        rootData = root.traverse(recursive=True, verbose=False)
        dnaStoreData = self.dnaStore.dump(verbose=False)
        data = str(dnaStoreData + rootData)
        if self.compress:
            import zlib
            data = zlib.compress(data)
        header = HEADER.format(compressed=chr(int(self.compress)))
        return header + data


class PyReader:
    def __init__(self, data):
        self.data = data[HEADER_LENGTH:]  # We don't need the header here.

        self.topGroup = None
        self.packer = DNAPacker(name='DNAStorage', packer=self.data)
        self.dnaStore = DNAStorage.DNAStorage()

    def readDNAStorage(self):
        # Catalog codes...
        rootCount = self.packer.unpack(UINT16)
        for _ in xrange(rootCount):
            root = self.packer.unpack(SHORT_STRING)
            codeCount = self.packer.unpack(UINT8)
            for _ in xrange(codeCount):
                code = self.packer.unpack(SHORT_STRING)
                self.dnaStore.storeCatalogCode(root, code)

        # Textures...
        textureCount = self.packer.unpack(UINT16)
        for _ in xrange(textureCount):
            code = self.packer.unpack(SHORT_STRING)
            filename = self.packer.unpack(SHORT_STRING)
            self.dnaStore.storeTexture(code, filename)

        # Fonts...
        fontCount = self.packer.unpack(UINT16)
        for _ in xrange(fontCount):
            code = self.packer.unpack(SHORT_STRING)
            filename = self.packer.unpack(SHORT_STRING)
            self.dnaStore.storeFont(filename, code)

        # Nodes...
        nodeCount = self.packer.unpack(UINT16)
        for _ in xrange(nodeCount):
            code = self.packer.unpack(SHORT_STRING)
            filename = self.packer.unpack(SHORT_STRING)
            search = self.packer.unpack(SHORT_STRING)
            self.dnaStore.storeNode(filename, search, code)

        # Hood nodes...
        hoodNodeCount = self.packer.unpack(UINT16)
        for _ in xrange(hoodNodeCount):
            code = self.packer.unpack(SHORT_STRING)
            filename = self.packer.unpack(SHORT_STRING)
            search = self.packer.unpack(SHORT_STRING)
            self.dnaStore.storeHoodNode(filename, search, code)

        # Place nodes...
        placeNodeCount = self.packer.unpack(UINT16)
        for _ in xrange(placeNodeCount):
            code = self.packer.unpack(SHORT_STRING)
            filename = self.packer.unpack(SHORT_STRING)
            search = self.packer.unpack(SHORT_STRING)
            self.dnaStore.storePlaceNode(filename, search, code)

        # Blocks...
        blockNumberCount = self.packer.unpack(UINT16)
        for _ in xrange(blockNumberCount):
            number = self.packer.unpack(UINT8)
            zoneId = self.packer.unpack(UINT16)
            title = self.packer.unpack(SHORT_STRING)
            article = self.packer.unpack(SHORT_STRING)
            buildingType = self.packer.unpack(SHORT_STRING)
            self.dnaStore.storeBlockNumber(number)
            self.dnaStore.storeBlockZone(number, zoneId)
            if title:
                self.dnaStore.storeBlockTitle(number, title)
            if article:
                self.dnaStore.storeBlockArticle(number, article)
            if buildingType:
                self.dnaStore.storeBlockBuildingType(number, buildingType)

        # Suit points...
        suitPointCount = self.packer.unpack(UINT16)
        for _ in xrange(suitPointCount):
            index = self.packer.unpack(UINT16)
            type = self.packer.unpack(UINT8)
            pos = []
            for _ in xrange(3):
                pos.append(self.packer.unpack(INT32) / 100.0)
            pos = tuple(pos)
            graphId = self.packer.unpack(UINT8)
            landmarkBuildingIndex = self.packer.unpack(INT8)
            suitPoint = DNASuitPoint(index, type, pos,
                                     landmarkBuildingIndex=landmarkBuildingIndex)
            suitPoint.setGraphId(graphId)
            self.dnaStore.storeSuitPoint(suitPoint)

        # Suit edges...
        suitEdgeCount = self.packer.unpack(UINT16)
        for _ in xrange(suitEdgeCount):
            startPointIndex = self.packer.unpack(UINT16)
            edgeCount = self.packer.unpack(UINT16)
            for _ in xrange(edgeCount):
                endPointIndex = self.packer.unpack(UINT16)
                zoneId = self.packer.unpack(UINT16)
                self.dnaStore.storeSuitEdge(startPointIndex, endPointIndex, zoneId)

        # Battle cells...
        battleCellCount = self.packer.unpack(UINT16)
        for _ in xrange(battleCellCount):
            width = self.packer.unpack(UINT8)
            height = self.packer.unpack(UINT8)
            pos = []
            for _ in range(3):
                pos.append(self.packer.unpack(INT32) / 100.0)
            pos = tuple(pos)
            cell = DNABattleCell(width, height, pos)
            self.dnaStore.storeBattleCell(cell)

    def readComponent(self, ctor):
        component = ctor('')
        hasChildren = component.construct(self.dnaStore, self.packer)
        if self.topGroup is not None:
            self.topGroup.add(component)
            component.setParent(self.topGroup)
        if hasChildren:
            self.topGroup = component
