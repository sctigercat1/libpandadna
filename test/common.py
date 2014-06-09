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
        self.data = data[len(HEADER):]  # We don't need the header here.

        self.dnaStore = DNAStorage.DNAStorage()

    def readDNAStorage(self):
        packer = DNAPacker(name='DNAStorage', packer=self.data)

        # Catalog codes...
        rootCount = packer.unpack(UINT16)
        for _ in xrange(rootCount):
            root = packer.unpack(SHORT_STRING)
            codeCount = packer.unpack(UINT8)
            for _ in xrange(codeCount):
                code = packer.unpack(SHORT_STRING)
                self.dnaStore.storeCatalogCode(root, code)

        # Textures...
        textureCount = packer.unpack(UINT16)
        for _ in xrange(textureCount):
            code = packer.unpack(SHORT_STRING)
            filename = packer.unpack(SHORT_STRING)
            self.dnaStore.storeTexture(code, filename)

        # Fonts...
        fontCount = packer.unpack(UINT16)
        for _ in xrange(fontCount):
            code = packer.unpack(SHORT_STRING)
            filename = packer.unpack(SHORT_STRING)
            self.dnaStore.storeFont(filename, code)

        # Nodes...
        nodeCount = packer.unpack(UINT16)
        for _ in xrange(nodeCount):
            code = packer.unpack(SHORT_STRING)
            filename = packer.unpack(SHORT_STRING)
            search = packer.unpack(SHORT_STRING)
            self.dnaStore.storeNode(filename, search, code)

        # Hood nodes...
        hoodNodeCount = packer.unpack(UINT16)
        for _ in xrange(hoodNodeCount):
            code = packer.unpack(SHORT_STRING)
            filename = packer.unpack(SHORT_STRING)
            search = packer.unpack(SHORT_STRING)
            self.dnaStore.storeHoodNode(filename, search, code)

        # Place nodes...
        placeNodeCount = packer.unpack(UINT16)
        for _ in xrange(placeNodeCount):
            code = packer.unpack(SHORT_STRING)
            filename = packer.unpack(SHORT_STRING)
            search = packer.unpack(SHORT_STRING)
            self.dnaStore.storePlaceNode(filename, search, code)

        # Blocks...
        blockNumberCount = packer.unpack(UINT16)
        for _ in xrange(blockNumberCount):
            number = packer.unpack(UINT8)
            zoneId = packer.unpack(UINT16)
            title = packer.unpack(SHORT_STRING)
            article = packer.unpack(SHORT_STRING)
            buildingType = packer.unpack(SHORT_STRING)
            self.dnaStore.storeBlockNumber(number)
            self.dnaStore.storeBlockZone(number, zoneId)
            if title:
                self.dnaStore.storeBlockTitle(number, title)
            if article:
                self.dnaStore.storeBlockArticle(number, article)
            if buildingType:
                self.dnaStore.storeBlockBuildingType(number, buildingType)

        # Suit points...
        suitPointCount = packer.unpack(UINT16)
        for _ in xrange(suitPointCount):
            index = packer.unpack(UINT16)
            type = packer.unpack(UINT8)
            pos = []
            for _ in xrange(3):
                pos.append(packer.unpack(INT32) / 100.0)
            pos = tuple(pos)
            graphId = packer.unpack(UINT8)
            landmarkBuildingIndex = packer.unpack(INT8)
            suitPoint = DNASuitPoint(index, type, pos,
                                     landmarkBuildingIndex=landmarkBuildingIndex)
            suitPoint.setGraphId(graphId)
            self.dnaStore.storeSuitPoint(suitPoint)

        # Suit edges...
        suitEdgeCount = packer.unpack(UINT16)
        for _ in xrange(suitEdgeCount):
            startPointIndex = packer.unpack(UINT16)
            edgeCount = packer.unpack(UINT16)
            for _ in xrange(edgeCount):
                endPointIndex = packer.unpack(UINT16)
                zoneId = packer.unpack(UINT16)
                self.dnaStore.storeSuitEdge(startPointIndex, endPointIndex, zoneId)

        # Battle cells...
        battleCellCount = packer.unpack(UINT16)
        for _ in xrange(battleCellCount):
            width = packer.unpack(UINT8)
            height = packer.unpack(UINT8)
            pos = []
            for _ in range(3):
                pos.append(packer.unpack(INT32) / 100.0)
            pos = tuple(pos)
            cell = DNABattleCell(width, height, pos)
            self.dnaStore.storeBattleCell(cell)
