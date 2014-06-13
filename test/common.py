import os
import sys


# We need some of the modules included in the compiler utility:
sys.path.append(os.path.abspath('../compiler'))


from StringIO import StringIO

from ply import lex

from dna.base import DNAStorage
from dna.base.DNAPacker import *
from dna.components import DNAAnimProp
from dna.components import DNABattleCell
from dna.components import DNACornice
from dna.components import DNADoor
from dna.components import DNAFlatBuilding
from dna.components import DNAFlatDoor
from dna.components import DNAGroup
from dna.components import DNAInteractiveProp
from dna.components import DNALandmarkBuilding
from dna.components import DNANode
from dna.components import DNAProp
from dna.components import DNARoot
from dna.components import DNASign
from dna.components import DNASignBaseline
from dna.components import DNASignGraphic
from dna.components import DNASignText
from dna.components import DNAStreet
from dna.components import DNASuitPoint
from dna.components import DNAVisGroup
from dna.components import DNAWall
from dna.components import DNAWindows
from dna.parser.tokens import *


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


class Reader:
    def __init__(self, data):
        self.data = data

        # Make sure we don't have the PDNA header:
        if self.data.startswith('PDNA\n'):
            self.data = self.data[HEADER_LENGTH:]

        self.topGroup = None
        self.packer = DNAPacker()
        self.packer += self.data
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
            self.dnaStore.storeFont(code, filename)

        # Nodes...
        nodeCount = self.packer.unpack(UINT16)
        for _ in xrange(nodeCount):
            code = self.packer.unpack(SHORT_STRING)
            filename = self.packer.unpack(SHORT_STRING)
            search = self.packer.unpack(SHORT_STRING)
            self.dnaStore.storeNode(code, filename, search)

        # Hood nodes...
        hoodNodeCount = self.packer.unpack(UINT16)
        for _ in xrange(hoodNodeCount):
            code = self.packer.unpack(SHORT_STRING)
            filename = self.packer.unpack(SHORT_STRING)
            search = self.packer.unpack(SHORT_STRING)
            self.dnaStore.storeHoodNode(code, filename, search)

        # Place nodes...
        placeNodeCount = self.packer.unpack(UINT16)
        for _ in xrange(placeNodeCount):
            code = self.packer.unpack(SHORT_STRING)
            filename = self.packer.unpack(SHORT_STRING)
            search = self.packer.unpack(SHORT_STRING)
            self.dnaStore.storePlaceNode(code, filename, search)

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
            pointType = self.packer.unpack(UINT8)
            pos = self.packer.unpackPosition()
            landmarkBuildingIndex = self.packer.unpack(INT8)
            suitPoint = DNASuitPoint.DNASuitPoint(
                index, pointType, pos,
                landmarkBuildingIndex=landmarkBuildingIndex)
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
            pos = self.packer.unpackPosition()
            cell = DNABattleCell.DNABattleCell(width, height, pos)
            self.dnaStore.storeBattleCell(cell)

    def readComponent(self, ctor):
        component = ctor('')
        hasChildren = component.construct(self.dnaStore, self.packer)
        if self.topGroup is not None:
            self.topGroup.add(component)
            component.setParent(self.topGroup)
        if hasChildren:
            self.topGroup = component

    def readComponents(self):
        componentCode = self.packer.unpack(UINT8)
        if componentCode == DNAGroup.DNAGroup.COMPONENT_CODE:
            self.readComponent(DNAGroup.DNAGroup)
        elif componentCode == DNAVisGroup.DNAVisGroup.COMPONENT_CODE:
            self.readComponent(DNAVisGroup.DNAVisGroup)
        elif componentCode == DNAProp.DNAProp.COMPONENT_CODE:
            self.readComponent(DNAProp.DNAProp)
        elif componentCode == DNASign.DNASign.COMPONENT_CODE:
            self.readComponent(DNASign.DNASign)
        elif componentCode == DNASignBaseline.DNASignBaseline.COMPONENT_CODE:
            self.readComponent(DNASignBaseline.DNASignBaseline)
        elif componentCode == DNASignText.DNASignText.COMPONENT_CODE:
            self.readComponent(DNASignText.DNASignText)
        elif componentCode == DNASignGraphic.DNASignGraphic.COMPONENT_CODE:
            self.readComponent(DNASignGraphic.DNASignGraphic)
        elif componentCode == DNAFlatBuilding.DNAFlatBuilding.COMPONENT_CODE:
            self.readComponent(DNAFlatBuilding.DNAFlatBuilding)
        elif componentCode == DNAWall.DNAWall.COMPONENT_CODE:
            self.readComponent(DNAWall.DNAWall)
        elif componentCode == DNAWindows.DNAWindows.COMPONENT_CODE:
            self.readComponent(DNAWindows.DNAWindows)
        elif componentCode == DNACornice.DNACornice.COMPONENT_CODE:
            self.readComponent(DNACornice.DNACornice)
        elif componentCode == DNALandmarkBuilding.DNALandmarkBuilding.COMPONENT_CODE:
            self.readComponent(DNALandmarkBuilding.DNALandmarkBuilding)
        elif componentCode == DNAAnimProp.DNAAnimProp.COMPONENT_CODE:
            self.readComponent(DNAAnimProp.DNAAnimProp)
        elif componentCode == DNAInteractiveProp.DNAInteractiveProp.COMPONENT_CODE:
            self.readComponent(DNAInteractiveProp.DNAInteractiveProp)
        elif componentCode == DNADoor.DNADoor.COMPONENT_CODE:
            self.readComponent(DNADoor.DNADoor)
        elif componentCode == DNAFlatDoor.DNAFlatDoor.COMPONENT_CODE:
            self.readComponent(DNAFlatDoor.DNAFlatDoor)
        elif componentCode == DNAStreet.DNAStreet.COMPONENT_CODE:
            self.readComponent(DNAStreet.DNAStreet)
        else:
            self.topGroup = self.topGroup.getParent()
        if self.packer:
            self.readComponents()
