from dna.base.DNAPacker import *
from dna.components import DNABattleCell
from dna.components import DNAGroup


class DNAVisGroup(DNAGroup.DNAGroup):
    COMPONENT_CODE = 2

    def __init__(self, name):
        DNAGroup.DNAGroup.__init__(self, name)

        self.visibles = []
        self.suitEdges = []
        self.battleCells = []

    def getVisGroup(self):
        return self

    def addVisible(self, visible):
        self.visibles.append(visible)

    def addSuitEdge(self, edge):
        self.suitEdges.append(edge)

    def addBattleCell(self, cell):
        self.battleCells.append(cell)

    def construct(self, dnaStore, packer):
        DNAGroup.DNAGroup.construct(self, dnaStore, packer)

        edgeCount = packer.unpack(UINT16)
        for _ in xrange(edgeCount):
            startPointIndex = packer.unpack(UINT16)
            endPointIndex = packer.unpack(UINT16)
            edge = dnaStore.getSuitEdge(startPointIndex, endPointIndex)
            self.addSuitEdge(edge)

        visibleCount = packer.unpack(UINT16)
        for _ in xrange(visibleCount):
            visible = packer.unpack(SHORT_STRING)
            self.addVisible(visible)

        battleCellCount = packer.unpack(UINT16)
        for _ in xrange(battleCellCount):
            width = packer.unpack(UINT8)
            height = packer.unpack(UINT8)
            pos = packer.unpackPosition()
            cell = DNABattleCell(width, height, pos)
            self.addBattleCell(cell)

        return True # We have children.

    def traverse(self, recursive=True, verbose=False):
        packer = DNAGroup.DNAGroup.traverse(self, recursive=False, verbose=verbose)
        packer.name = 'DNAVisGroup'  # Override the name for debugging.

        packer.pack('suit edge count', len(self.suitEdges), UINT16)
        for edge in self.suitEdges:
            startPointIndex = edge.startPoint.index
            packer.pack('start point index', startPointIndex, UINT16)
            endPointIndex = edge.endPoint.index
            packer.pack('end point index', endPointIndex, UINT16)

        packer.pack('visible count', len(self.visibles), UINT16)
        for visible in self.visibles:
            packer.pack('visible', visible, SHORT_STRING)

        packer.pack('battle cell count', len(self.battleCells), UINT16)
        for cell in self.battleCells:
            packer.pack('width', cell.width, UINT8)
            packer.pack('height', cell.height, UINT8)
            packer.packPosition(*cell.pos)

        if recursive:
            packer += self.traverseChildren(verbose=verbose)
        return packer
